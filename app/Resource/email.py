import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import request, jsonify
from flask_restful import Resource
from dotenv import load_dotenv
import os
load_dotenv()

# @app.route('/send-email', methods=['POST'])
class SendEmail(Resource):
    def post():
        try:
            data = request.get_json()
            trip_code = data.get('trip_code')
            email_address = data.get('email_address')

            if not trip_code or not email_address:
                return jsonify({"error": "trip_code and email_address are required"}), 400

            # Email configuration
            # sender_email = "shubhsetampwr9945@gmail.com"
            # sender_password = os.getenv("EMAIL_PASSWORD")  # Use environment variable for security
            smtp_server = "smtp.example.com"
            smtp_port = 587

            # Create the email
            subject = "Your Trip Code"
            body = f"Your trip code is: {trip_code}"
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email_address
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Send the email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email_address, msg.as_string())

            return jsonify({"message": "Email sent successfully"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
