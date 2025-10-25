from datetime import datetime, time
from backend.models import Fine, db, Student, SMSLog
from twilio.rest import Client

# Twilio credentials
account_sid = 'ACb54bfabfea9e23d6211a4bf51d76956a'
auth_token = '[AuthToken]'  # Replace with your actual Auth Token
twilio_from = '+1234567890' # Replace with your Twilio phone number

def create_fine_if_late(student_id, attendance_id, attendance_time):
    cutoff_time = time(8, 50)  # 8:50 AM
    if attendance_time > cutoff_time:
        fine = Fine(
            attendance_id=attendance_id,
            student_id=student_id,
            attendance_date=datetime.now()
        )
        # Set additional fields
        fine.late_by = (attendance_time.hour - 8) * 60 + attendance_time.minute - 50
        fine.amount = 20  # Fixed fine
        fine.status = "Unpaid"

        db.session.add(fine)
        db.session.commit()

        # Fetch student mobile number
        student = Student.query.get(student_id)
        if student and student.mobile:
            client = Client(account_sid, auth_token)
            sms_body = (
                f"Dear {student.name}, a fine of Rs.20 has been generated due to late entry at {attendance_time.strftime('%H:%M')}. "
                "Please pay your fine at the earliest."
            )
            try:
                message = client.messages.create(
                    body=sms_body,
                    from_=twilio_from,
                    to=student.mobile
                )
                # Log SMS as sent
                sms_log = SMSLog(
                    student_id=student_id,
                    message=sms_body,
                    status="sent",
                    sent_at=datetime.utcnow()
                )
                db.session.add(sms_log)
                db.session.commit()
                print("Twilio SMS sent:", message.sid)
            except Exception as e:
                # Log SMS as failed
                sms_log = SMSLog(
                    student_id=student_id,
                    message=sms_body,
                    status="failed",
                    sent_at=datetime.utcnow()
                )
                db.session.add(sms_log)
                db.session.commit()
                print("Twilio SMS failed:", str(e))
