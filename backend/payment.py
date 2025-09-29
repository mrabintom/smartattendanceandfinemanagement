from flask import Blueprint, render_template, request, jsonify, current_app
import razorpay
from backend.models import db, Payment, Student

payment_bp = Blueprint("payment", __name__)

def get_razorpay_client():
    return razorpay.Client(auth=(
        current_app.config["RAZORPAY_KEY_ID"],
        current_app.config["RAZORPAY_KEY_SECRET"]
    ))

@payment_bp.route("/pay/<int:student_id>")
def pay(student_id):
    amount = request.args.get("amount", type=int)
    student = Student.query.get(student_id)
    if not student or not amount or amount <= 0:
        return "Invalid payment request", 400

    razorpay_client = get_razorpay_client()
    razorpay_order = razorpay_client.order.create(dict(amount=amount*100, currency="INR", payment_capture="1"))

    payment = Payment(
        student_id=student_id,
        order_id=razorpay_order['id'],
        amount=amount,
        status="created"
    )
    db.session.add(payment)
    db.session.commit()

    return render_template("payment.html", student=student, order=razorpay_order, amount=amount*100, razorpay_key_id=current_app.config["RAZORPAY_KEY_ID"])



@payment_bp.route("/payment/success", methods=["POST"])
def payment_success():
    data = request.get_json()
    payment = Payment.query.filter_by(order_id=data['razorpay_order_id']).first()

    if payment:
        payment.payment_ref_id = data['razorpay_payment_id']
        payment.status = "paid"
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "failed"})
