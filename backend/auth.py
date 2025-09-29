from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend.models import db, Student, Teacher, Admin

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def index():
    return render_template("index.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    role = request.form.get("role")
    email = request.form.get("email")
    password = request.form.get("password")

    if role == "student":
        user = Student.query.filter_by(email=email, password=password).first()
        if user:
            session.clear()
            session["user_id"] = user.student_id
            session["role"] = "student"
            session["name"] = user.name
            session["department"] = user.department
            session["email"] = user.email
            session["mobile"] = getattr(user, 'mobile', 'N/A')
            session["photo"] = getattr(user, 'photo', 'default-avatar.png')
            flash("Student login successful!", "success")
            return redirect(url_for("student_dashboard"))
        flash("Invalid student credentials!", "danger")

    elif role == "teacher":
        user = Teacher.query.filter_by(teacher_email=email, teacher_password=password).first()
        if user:
            session.clear()
            session["user_id"] = user.teacher_id
            session["role"] = "teacher"
            session["name"] = user.teacher_name
            session["email"] = user.teacher_email
            session['teacher_department'] = user.teacher_department
            flash("Teacher login successful!", "success")
            return redirect(url_for("teacher_dashboard"))
        flash("Invalid teacher credentials!", "danger")

    elif role == "admin":
        user = Admin.query.filter_by(admin_email=email, admin_password=password).first()
        if user:
            session.clear()
            session["user_id"] = user.admin_id
            session["role"] = "admin"
            session["name"] = user.admin_name
            session["department"] = user.admin_department
            session["email"] = user.admin_email
            flash("Admin login successful!", "success")
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Invalid admin credentials!", "danger")
            return redirect(url_for("auth.index") + "#login")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("auth.index"))
