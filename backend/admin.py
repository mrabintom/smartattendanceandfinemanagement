from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from backend.models import db, Student, Teacher, Admin, Attendance

admin_bp = Blueprint("admin", __name__)

def admin_required(f):
    """Decorator to require admin login"""
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash('Access denied. Admin login required.', 'danger')
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    teachers = Teacher.query.all()
    total_teachers = Teacher.query.count()
    attendance_records = Attendance.query.order_by(Attendance.date.desc()).all()
    return render_template(
        "admin.html",
        teachers=teachers,
        total_teachers=total_teachers,
        admin_name=session.get("name"),
        admin_department=session.get("department"),
        admin_email=session.get("email"),
        attendance_records=attendance_records
    )

@admin_bp.route("/students")
@admin_required
def students():
    students = Student.query.all()
    return render_template("admin_students.html", students=students)

@admin_bp.route("/teachers")
@admin_required
def teachers():
    teachers = Teacher.query.all()
    return render_template("admin_teachers.html", teachers=teachers)

@admin_bp.route("/attendance")
@admin_required
def attendance():
    attendance_records = Attendance.query.order_by(Attendance.date.desc()).all()
    return render_template("admin_attendance.html", attendance_records=attendance_records)

@admin_bp.route("/add_teacher", methods=["POST"])
@admin_required
def add_teacher():
    data = request.get_json()
    teacher = Teacher(
        teacher_name=data.get("teacher_name"),
        teacher_email=data.get("teacher_email"),
        teacher_department=data.get("teacher_department"),
        teacher_password=data.get("teacher_password"),
        teacher_status=data.get("teacher_status", "Active")
    )
    db.session.add(teacher)
    db.session.commit()
    return jsonify({"success": True, "message": "Teacher added successfully."})

@admin_bp.route("/delete_teacher/<int:teacher_id>", methods=["POST"])
@admin_required
def delete_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        db.session.delete(teacher)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Teacher not found"}), 404