from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = "students"  # Use plural to match your existing DB and foreign keys
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    parent_mobile = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    photo = db.Column(db.String(255))

class Teacher(db.Model):
    __tablename__ = "teacher"
    teacher_id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(100))
    teacher_email = db.Column(db.String(100), unique=True, nullable=False)
    teacher_department = db.Column(db.String(100))
    teacher_password = db.Column(db.String(100), nullable=False)
    teacher_status = db.Column(db.String(20))

class Admin(db.Model):
    __tablename__ = "admin"
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(100))
    admin_department = db.Column(db.String(100))
    admin_email = db.Column(db.String(100), unique=True, nullable=False)
    admin_password = db.Column(db.String(100), nullable=False)

class Attendance(db.Model):
    __tablename__ = "attendance"
    attendance_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id"))  # ✅ correct reference
    student_name = db.Column(db.String(100))
    date = db.Column(db.Date)
    time = db.Column(db.Time)

class Fine(db.Model):
    __tablename__ = 'fine'
    
    fine_id = db.Column(db.Integer, primary_key=True)
    attendance_id = db.Column(db.Integer, db.ForeignKey('attendance.attendance_id', ondelete="CASCADE"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete="CASCADE"), nullable=False)
    attendance_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    late_by = db.Column(db.Integer, default=0)  # Minutes late
    amount = db.Column(db.Numeric(10,2), default=0)
    status = db.Column(db.String(10), default='Unpaid')  # 'Unpaid' or 'Paid'
    sms_sent = db.Column(db.Boolean, default=False)  # SMS notification sent

    # Relationships (optional, if you want to access related objects easily)
    student = db.relationship('Student', backref=db.backref('fines', lazy=True))
    attendance = db.relationship('Attendance', backref=db.backref('fines', lazy=True))

    def __init__(self, attendance_id, student_id, attendance_date):
        self.attendance_id = attendance_id
        self.student_id = student_id
        self.attendance_date = attendance_date

        # Calculate late_by and fine amount
        if self.attendance_date.hour >= 9:
            self.late_by = (self.attendance_date.hour - 9) * 60 + self.attendance_date.minute
            self.amount = 50  # Default fine amount
            self.sms_sent = False
        else:
            self.late_by = 0
            self.amount = 0
            self.sms_sent = True  # No fine, SMS not required




class Payment(db.Model):
    __tablename__ = "payments"

    payment_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    order_id = db.Column(db.String(100), unique=True, nullable=False)   # Razorpay Order ID
    payment_ref_id = db.Column(db.String(100), unique=True, nullable=True)  # Razorpay Payment ID
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), default="INR")

    status = db.Column(db.String(20), default="created")  
    # possible values: created, pending, paid, failed, refunded

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship("Student", backref=db.backref("payments", lazy=True))

    def __repr__(self):
        return f"<Payment {self.payment_id} - {self.status}>"


class SMSLog(db.Model):
    __tablename__ = "sms_logs"

    sms_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="pending")  
    # possible values: pending, sent, failed

    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship("Student", backref=db.backref("sms_logs", lazy=True))

    def __repr__(self):
        return f"<SMSLog {self.sms_id} - {self.status}>"
