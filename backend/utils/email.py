# email.py
# This file handles sending emails using Python's built-in smtplib library
# We use Gmail's SMTP server to send the emails
# The admin's email and password are stored in the .env file

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(to_email, subject, html_body):
    # Read email credentials from the .env file
    sender_email = os.getenv("MAIL_EMAIL")
    sender_password = os.getenv("MAIL_PASSWORD")

    # If no email is configured, just skip sending (so the app doesn't crash)
    if not sender_email or not sender_password:
        print("Email not configured - skipping email send")
        return False

    try:
        # Create the email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        # Attach the HTML body to the email
        part = MIMEText(html_body, "html")
        msg.attach(part)

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())

        print(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        # If sending fails, we print the error but don't crash the app
        print(f"Email failed: {e}")
        return False


def send_invoice_email(client_name, client_email, month, amount, status):
    # This function sends an invoice notification to a client
    subject = f"Invoice - {month} | GuardLink Security"
    
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1B2E24; color: #ffffff; border-radius: 8px; overflow: hidden;">
        <div style="background: #2D6A4F; padding: 32px 40px; border-bottom: 2px solid #52B788;">
            <h1 style="margin: 0; font-size: 28px; color: #ffffff;">Guard<span style="color: #D4A017;">Link</span></h1>
            <p style="color: #52B788; font-size: 12px; letter-spacing: 2px; margin: 4px 0 0;">Security Management</p>
        </div>
        <div style="padding: 40px;">
            <p style="color: #52B788;">Dear {client_name},</p>
            <p style="color: #ccc;">Please find your invoice details for <strong style="color: #D4A017;">{month}</strong> below.</p>
            <div style="background: #243d2e; border: 1px solid #2D6A4F; border-radius: 6px; padding: 28px; margin: 24px 0;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px 0; color: #52B788; font-size: 11px; letter-spacing: 2px; text-transform: uppercase;">Period</td>
                        <td style="padding: 10px 0; color: #fff; text-align: right;">{month}</td>
                    </tr>
                    <tr style="border-top: 1px solid #2D6A4F;">
                        <td style="padding: 10px 0; color: #52B788; font-size: 11px; letter-spacing: 2px; text-transform: uppercase;">Amount Due</td>
                        <td style="padding: 10px 0; color: #D4A017; font-size: 20px; font-weight: bold; text-align: right;">KES {float(amount):,.2f}</td>
                    </tr>
                    <tr style="border-top: 1px solid #2D6A4F;">
                        <td style="padding: 10px 0; color: #52B788; font-size: 11px; letter-spacing: 2px; text-transform: uppercase;">Status</td>
                        <td style="padding: 10px 0; text-align: right;">
                            <span style="background: {'#0d2e1a' if status == 'paid' else '#2e1a1a'}; color: {'#4caf7d' if status == 'paid' else '#e57373'}; padding: 4px 12px; border-radius: 20px; font-size: 12px;">
                                {status.upper()}
                            </span>
                        </td>
                    </tr>
                </table>
            </div>
            <p style="color: #888;">If you have any questions, please contact us.</p>
        </div>
        <div style="background: #2D6A4F; padding: 20px 40px; text-align: center;">
            <p style="color: #52B788; font-size: 11px; letter-spacing: 2px; margin: 0;">GUARDLINK SECURITY · NAIROBI, KENYA</p>
        </div>
    </div>
    """
    return send_email(client_email, subject, html_body)


def send_complaint_email(admin_email, client_name, client_email, message):
    # This function notifies the admin when a client submits a complaint
    subject = f"New Complaint from {client_name} | GuardLink"

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1B2E24; color: #ffffff; border-radius: 8px; overflow: hidden;">
        <div style="background: #2D6A4F; padding: 32px 40px; border-bottom: 2px solid #52B788;">
            <h1 style="margin: 0; font-size: 28px; color: #ffffff;">Guard<span style="color: #D4A017;">Link</span></h1>
            <p style="color: #52B788; font-size: 12px; letter-spacing: 2px; margin: 4px 0 0;">New Client Complaint</p>
        </div>
        <div style="padding: 40px;">
            <p style="color: #52B788;">A new complaint has been submitted.</p>
            <div style="background: #243d2e; border: 1px solid #2D6A4F; border-radius: 6px; padding: 28px; margin: 24px 0;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px 0; color: #52B788; font-size: 11px; letter-spacing: 2px; text-transform: uppercase;">Client</td>
                        <td style="padding: 10px 0; color: #fff; text-align: right;">{client_name}</td>
                    </tr>
                    <tr style="border-top: 1px solid #2D6A4F;">
                        <td style="padding: 10px 0; color: #52B788; font-size: 11px; letter-spacing: 2px; text-transform: uppercase;">Email</td>
                        <td style="padding: 10px 0; color: #D4A017; text-align: right;">{client_email}</td>
                    </tr>
                    <tr style="border-top: 1px solid #2D6A4F;">
                        <td style="padding: 10px 0; color: #52B788; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; vertical-align: top;">Message</td>
                        <td style="padding: 10px 0; color: #ccc; text-align: right; line-height: 1.7;">{message}</td>
                    </tr>
                </table>
            </div>
            <p style="color: #888;">Log in to the admin portal to view and resolve this complaint.</p>
        </div>
        <div style="background: #2D6A4F; padding: 20px 40px; text-align: center;">
            <p style="color: #52B788; font-size: 11px; letter-spacing: 2px; margin: 0;">GUARDLINK SECURITY · NAIROBI, KENYA</p>
        </div>
    </div>
    """
    return send_email(admin_email, subject, html_body)