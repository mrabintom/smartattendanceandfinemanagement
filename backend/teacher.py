from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, current_app
from backend.models import db, Teacher, Student, Attendance, Fine, Payment
from datetime import datetime, time as dt_time
import pandas as pd
from io import BytesIO

teacher_bp = Blueprint("teacher", __name__)

@teacher_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        teacher = Teacher.query.filter_by(teacher_email=email, teacher_password=password).first()
        if teacher:
            session["user_id"] = teacher.teacher_id
            session["role"] = "teacher"
            session["name"] = teacher.teacher_name
            session["teacher_department"] = teacher.teacher_department
            flash("Welcome, " + teacher.teacher_name, "success")
            return redirect(url_for("teacher.dashboard"))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.index") + "#login")
    return render_template("teacher_login.html")

@teacher_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session or session.get("role") != "teacher":
        return redirect(url_for("auth.index") + "#login")

    # Student details - map to fields expected by template
    students = []
    for s in Student.query.order_by(Student.student_id).all():
        students.append({
            "roll_no": s.student_id,
            "name": s.name,
            "email": s.email,
            "status": "Active"
        })

    # Attendance records - join Attendance + Student
    cutoff = dt_time(8, 50)
    attendance_records = []
    records = db.session.query(Attendance, Student).join(Student, Attendance.student_id == Student.student_id).order_by(Attendance.date.desc()).all()
    for att, stu in records:
        arrival_time = att.time.strftime("%H:%M") if att.time else ""
        late_by = 0
        if att.time and att.time > cutoff:
            late_by = (att.time.hour - cutoff.hour) * 60 + (att.time.minute - cutoff.minute)
        status = "Present"
        if late_by > 0:
            status = "Late"
        attendance_records.append({
            "date": att.date.strftime("%Y-%m-%d") if att.date else "",
            "roll_no": stu.student_id,
            "name": stu.name,
            "status": status,
            "arrival_time": arrival_time,
            "late_by": late_by
        })

    # Fine records: compute per-student late entries after 08:50 and total amount = count * 20
    fines = []
    LATE_FINE_PER_ENTRY = 20
    for s in Student.query.order_by(Student.student_id).all():
        late_entries = Attendance.query.filter(
            Attendance.student_id == s.student_id,
            Attendance.time != None,
            Attendance.time > cutoff
        ).order_by(Attendance.date.desc(), Attendance.time.desc()).all()

        if not late_entries:
            continue

        late_times = []
        for a in late_entries:
            d = a.date.strftime("%Y-%m-%d") if getattr(a, "date", None) else ""
            t = a.time.strftime("%H:%M") if getattr(a, "time", None) else ""
            late_times.append(f"{d} {t}".strip())

        total_amount = len(late_entries) * LATE_FINE_PER_ENTRY
        fines.append({
            "roll_no": s.student_id,
            "name": s.name,
            "late_times": ", ".join(late_times),
            "total_amount": total_amount,
            "status": "Unpaid"  # adjust if you have payment/fine status stored elsewhere
        })

    return render_template("teacher.html",
                           students=students,
                           attendance_records=attendance_records,
                           fines=fines)

@teacher_bp.route("/export_students_excel")
def export_students_excel():
    pass

# Add this new route
@teacher_bp.route("/export_attendance_excel")
def export_attendance_excel():
    import pandas as pd
    from io import BytesIO

    # Join Attendance + Student and build rows
    rows = []
    records = db.session.query(Attendance, Student).join(
        Student, Attendance.student_id == Student.student_id
    ).order_by(Attendance.date.desc(), Attendance.time.desc()).all()

    for att, stu in records:
        rows.append({
            "Attendance ID": getattr(att, "attendance_id", ""),
            "Student ID": stu.student_id,
            "Student Name": stu.name,
            "Department": getattr(stu, "department", ""),
            "Date": att.date.strftime("%Y-%m-%d") if getattr(att, "date", None) else "",
            "Arrival Time": att.time.strftime("%H:%M") if getattr(att, "time", None) else "",
            "Late By (mins)": (
                max(0, (att.time.hour * 60 + att.time.minute) - (8 * 60 + 50))
            ) if getattr(att, "time", None) else 0
        })

    df = pd.DataFrame(rows)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance")
    output.seek(0)
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        download_name="attendance.xlsx",
        as_attachment=True
    )

@teacher_bp.route("/export_students_pdf")
def export_students_pdf():
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        from reportlab.lib import colors
    except Exception:
        return "PDF export requires reportlab. Install with: pip install reportlab", 501

    students = Student.query.order_by(Student.student_id).all()
    data = [["Student ID", "Name", "Department", "Email", "Mobile"]]
    for s in students:
        data.append([str(s.student_id), s.name or "", s.department or "", s.email or "", s.mobile or ""])

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    table = Table(data, repeatRows=1)
    style = TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ])
    table.setStyle(style)
    doc.build([table])
    buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf", download_name="students.pdf", as_attachment=True)

@teacher_bp.route("/download_student/<int:student_id>")
def download_student(student_id):
    student = Student.query.get_or_404(student_id)

    # Attendance sheet
    attendance_rows = []
    att_records = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.date.desc(), Attendance.time.desc()).all()
    for a in att_records:
        attendance_rows.append({
            "Attendance ID": getattr(a, "attendance_id", ""),
            "Date": getattr(a, "date", "").strftime("%Y-%m-%d") if getattr(a, "date", None) else "",
            "Arrival Time": getattr(a, "time", "").strftime("%H:%M") if getattr(a, "time", None) else "",
            "Late By (mins)": (
                max(0, (a.time.hour*60 + a.time.minute) - (8*60 + 50))
            ) if getattr(a, "time", None) else 0
        })

    # Fine / payment sheet
    fine_rows = []
    fine_records = Fine.query.filter_by(student_id=student_id).order_by(Fine.attendance_date.desc()).all()
    for f in fine_records:
        fine_rows.append({
            "Fine ID": getattr(f, "fine_id", ""),
            "Attendance Date": getattr(f, "attendance_date", "").strftime("%Y-%m-%d") if getattr(f, "attendance_date", None) else "",
            "Late By (mins)": getattr(f, "late_by", 0),
            "Amount": float(getattr(f, "amount", 0) or 0),
            "Status": getattr(f, "status", "")
        })

    # Payments
    payment_rows = []
    payments = Payment.query.filter_by(student_id=student_id).order_by(Payment.created_at.desc()).all()
    for p in payments:
        payment_rows.append({
            "Payment ID": getattr(p, "payment_id", ""),
            "Ref ID": getattr(p, "payment_ref_id", ""),
            "Amount": float(getattr(p, "amount", 0) or 0),
            "Currency": getattr(p, "currency", ""),
            "Status": getattr(p, "status", ""),
            "Created At": getattr(p, "created_at", "").strftime("%Y-%m-%d %H:%M") if getattr(p, "created_at", None) else ""
        })

    # Build Excel with multiple sheets
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        # Student info sheet
        info_df = pd.DataFrame([{
            "Student ID": student.student_id,
            "Name": student.name,
            "Department": student.department,
            "Email": student.email,
            "Mobile": student.mobile,
            "Parent Mobile": student.parent_mobile
        }])
        info_df.to_excel(writer, index=False, sheet_name="Student_Info")

        pd.DataFrame(attendance_rows).to_excel(writer, index=False, sheet_name="Attendance")
        pd.DataFrame(fine_rows).to_excel(writer, index=False, sheet_name="Fines")
        pd.DataFrame(payment_rows).to_excel(writer, index=False, sheet_name="Payments")

    output.seek(0)
    filename = f"student_{student_id}_report.xlsx"
    return send_file(output,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     download_name=filename,
                     as_attachment=True)
