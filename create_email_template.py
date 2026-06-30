#!/usr/bin/env python3
import frappe
from frappe import _

def create_email_template():
    """Create the Academic Report Guardian Notification email template"""
    
    # Check if template already exists
    if frappe.db.exists("Email Template", "Academic Report - Guardian Notification"):
        print("Email Template already exists!")
        return
    
    # Create the email template
    email_template = frappe.get_doc({
        "doctype": "Email Template",
        "name": "Academic Report - Guardian Notification",
        "subject": "Academic Report Available: {{ student_name }} - {{ term }} {{ academic_year }}",
        "use_html": 1,
        "response": """<p>Dear {{ guardian_name }},</p>

<p>We hope this message finds you well.</p>

<p>We are pleased to inform you that the academic report for <strong>{{ student_name }}</strong> (Admission No: {{ admission_no }}) is now available.</p>

<h4>Report Details:</h4>
<ul>
    <li><strong>Academic Year:</strong> {{ academic_year }}</li>
    <li><strong>Term:</strong> {{ term }}</li>
    <li><strong>Class:</strong> {{ class_name }}</li>
    <li><strong>GPA:</strong> {{ gpa }}</li>
</ul>

<p>Please find the complete academic report attached to this email as a PDF document. You can also access it online using the link below:</p>

<p style="text-align: center; margin: 20px 0;">
    <a href="{{ report_url }}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">View Report Online</a>
</p>

<p>If you have any questions or concerns regarding your ward's performance, please do not hesitate to contact us.</p>

<p>Best regards,<br>
<strong>GCIHS Academic Administration</strong></p>"""
    })
    
    email_template.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Email Template 'Academic Report - Guardian Notification' created successfully!")

if __name__ == "__main__":
    frappe.connect(site="erp.gcihs.local")
    create_email_template()
