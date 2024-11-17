from flask import Blueprint, request, jsonify, json
from werkzeug.security import generate_password_hash,check_password_hash
from app.models import db, Account, Role,Visitor
from flask_jwt_extended import create_access_token,get_jwt_identity,get_jwt,unset_jwt_cookies,jwt_required
from datetime import datetime,timedelta,timezone
from app.decorators.acc_decorators import roles_required
from app.services.otp import generate_otp
from flask import current_app
from app.services.mail import send_otp_email,send_notification_email




auth = Blueprint('auth', __name__)

def get_redis_client():
    redis_client = current_app.redis_client
    return redis_client


# Step 1: Route to initiate registration and send OTP
@auth.route('/register/send_otp', methods=['POST'])
def send_registration_otp():
    try:
        email = request.json['email']

        # Check if the user already exists
        user_exists = Account.query.filter_by(email=email).first() is not None
        if user_exists:
            return jsonify({"error": "User already exists"}), 409

        redis_client=get_redis_client()
        otp = generate_otp()
        otp_key = f"otp:{email}"  # Unique key for each user (using email)
        redis_client.setex(otp_key, timedelta(minutes=5), otp)

        #send_otp_email(email, 'Your OTP Code', f'Your OTP code is {otp}')
        #send_notification_email(email,"NOTIFICATION",f'An OTP has been sent successfully.')
        
        return jsonify({"message": "OTP sent successfully. Please verify your email.","otp":otp})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Step 2: Route to verify OTP for registration
@auth.route('/register/verify_otp', methods=['POST'])
def verify_registration_otp():
    try:
        email = request.json['email']
        otp_input = request.json['otp']

        redis_client = get_redis_client()
        otp_key = f"otp:{email}"
        otp_stored = redis_client.get(otp_key)

        if otp_stored is None:
            return jsonify({"error": "OTP request not found or expired."}), 400

        # Verify OTP
        if otp_input != otp_stored:
            return jsonify({"error": "Invalid OTP."}), 400

        # OTP is valid, proceed to next step of registration
        # Cleanup: Delete the OTP from Redis after it has been used
        redis_client.delete(otp_key)

        return jsonify({"message": "OTP verified. You can now complete your registration."})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Step 3: Route to complete registration after OTP verification
@auth.route('/register/complete', methods=['POST'])
def complete_registration():
    try:
        email = request.json['email']
        password = request.json['password']
        user_role = request.json['role_id']

        # Additional visitor details
        institution = request.json.get('institution')
        first_name = request.json.get('first_name')
        middle_name = request.json.get('middle_name', '')  # Optional field
        last_name = request.json.get('last_name')
        suffix = request.json.get('suffix', '')  # Optional field
        reason = request.json.get('reason', '')

        # Check if the user already exists (double-checking)
        user_exists = Account.query.filter_by(email=email).first() is not None
        if user_exists:
            return jsonify({"error": "User already exists"}), 409

        # Hash the password and create a new user in the Account table
        hashed_password = generate_password_hash(password)
        new_user = Account(
            email=email,
            user_pw=hashed_password,
            role_id=user_role
        )
        db.session.add(new_user)
        db.session.flush()  # Ensure new_user.user_id is generated before adding to Visitor table

        # Create a new visitor entry linked to the Account table
        new_visitor = Visitor(
            visitor_id=new_user.user_id,
            institution=institution,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            suffix=suffix,
            reason=reason
        )
        db.session.add(new_visitor)
        db.session.commit()

        return jsonify({
            'id': new_user.user_id,
            'email': new_user.email,
            'role': new_user.role_id,
            'institution': institution,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'suffix': suffix,
            'reason': reason
        })
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        return jsonify({'error': str(e)}), 400



@auth.route('/login', methods=['POST'])
def login_user():
    try:
        email = request.json['email']
        password = request.json['password']

        user = Account.query.filter_by(email=email).first()
        
        if user is None:
            return jsonify({"error":"Unauthorized"}), 401
        if not check_password_hash(user.user_pw,password):
            return jsonify({"error":"Unauthorized"}), 401
        
        additional_claims = {
            "role": user.role_id,
            "email": user.email
        }

        access_token = create_access_token(identity=user.user_id, additional_claims=additional_claims)

        return jsonify({
            'id': user.user_id,
            'email': user.email,
            "access_token": access_token,
            "message": "Login successful.",
        })

    except Exception as e:
            return jsonify({'error': str(e)}), 400

# Route to verify OTP and generate access token
@auth.route('/verify_otp', methods=['POST'])
def verify_otp():
    try:
        email = request.json['email']
        otp_input = request.json['otp']

        redis_client=get_redis_client()

        # Get the OTP from Redis
        otp_key = f"otp:{email}"
        otp_stored = redis_client.get(otp_key)

        if otp_stored is None:
            return jsonify({"error": "OTP request not found or expired."}), 400

        # Verify OTP
        if otp_input != otp_stored:
            return jsonify({"error": "Invalid OTP."}), 400

        # If OTP is valid, generate the access token
        user = Account.query.filter_by(email=email).first()

        additional_claims = {
            "role": user.role_id,
            "email": user.email
        }

        access_token = create_access_token(identity=user.user_id, additional_claims=additional_claims)

        # Cleanup: Delete the OTP from Redis after it has been used
        redis_client.delete(otp_key)

        return jsonify({
            'id': user.user_id,
            'email': user.email,
            "access_token": access_token
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@auth.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))  # Extend expiration by 4 hours

        if target_timestamp > exp_timestamp:
            # Extract identity and additional claims from the existing JWT
            identity = get_jwt_identity()  # Typically the user_id
            claims = get_jwt()  # All the claims (including additional ones like 'role', 'email')

            # You may want to store your additional claims separately or just reuse them
            additional_claims = {
                "role": claims.get("role"),
                "email": claims.get("email")
            }
            
            # Create a new access token with the same identity and additional claims
            access_token = create_access_token(
                identity=identity, 
                additional_claims=additional_claims,
                expires_delta=timedelta(hours=6)  # Extend the expiration time to 6 hours
            )

            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token 
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response
    
@auth.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response

@auth.route('/profile/<user_id>', methods=['GET'])
@jwt_required() 
def my_profile(user_id):
    print(user_id)
    if not user_id:
        return jsonify({"error": "Unauthorized Access"}), 401
       
    user = Account.query.filter_by(user_id=user_id).first()
  
    response_body = {
        "id": user.user_id,
        "email": user.email,
        "role_id" : user.role_id
    }
  
    return jsonify(response_body)

@auth.route("/test", methods=['POST'])
@jwt_required()
@roles_required(['01','04','05'])
def track_user():

    user_id = get_jwt_identity()
    claims = get_jwt()
    role_id=claims.get("role")
    email=claims.get("email")

    roles=Role.query.filter_by(role_id=role_id).first()
    # do something

    data={
        "user":user_id,
        "role":roles.role_name,
        "email":email

    }
    return jsonify(data)