import datetime
from flask import Blueprint, request, jsonify, current_app
from app.models import db

def formatting_id(indicator, model_class, id_field):
    """Generate a new ID based on the current date and last entry."""
    current_date_str = datetime.datetime.now().strftime('%Y%m%d')

    # Query the last entry for the current date to get the latest ID
    last_entry = model_class.query.filter(getattr(model_class, id_field).like(f'{indicator}-{current_date_str}-%')) \
                                  .order_by(getattr(model_class, id_field).desc()) \
                                  .first()

    # Determine the next sequence number
    if last_entry:
        last_sequence = int(getattr(last_entry, id_field).split('-')[-1])
        next_sequence = f"{last_sequence + 1:03d}"
    else:
        next_sequence = "001"  # Start with 001 if no previous entry

    # Generate the new ID
    generated_id = f"{indicator}-{current_date_str}-{next_sequence}"
    return generated_id

def log_audit_trail(user_id, table_name, record_id, operation, action_desc):
    """Log an audit trail entry."""
    from app.models.audit_trail import AuditTrail
    try:
        audit_id = formatting_id('AUD', AuditTrail, 'audit_id')

        # Create the audit trail entry
        new_audit = AuditTrail(
            audit_id=audit_id,
            user_id=user_id,
            table_name=table_name,
            record_id=record_id,
            operation=operation,
            change_datetime=datetime.datetime.now(),
            action_desc=action_desc
        )

        # Add and commit the new audit log
        db.session.add(new_audit)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        # Log the error message to a file or monitoring system
        print(f"Error logging audit trail: {e}")  # Change this to a logging call in production