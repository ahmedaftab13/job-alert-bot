import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


# ---------------------------
# EMAIL CONFIG (FROM GITHUB SECRETS)
# ---------------------------

EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")


# ---------------------------
# FORMAT JOBS INTO HTML EMAIL
# ---------------------------

def format_jobs_html(jobs):
    if not jobs:
        return "<p>No new matching jobs found today.</p>"

    html = """
    <h2>Daily Job Alert</h2>
    <p>Here are the latest matching jobs based on your profile:</p>
    <hr>
    """

    for job in jobs:
        html += f"""
        <div style="margin-bottom:20px;">
            <h3>{job['title']}</h3>
            <p><b>Company:</b> {job.get('company', 'N/A')}</p>
            <p><b>Location:</b> {job.get('location', 'N/A')}</p>
            <p><a href="{job.get('link', '#')}">👉 Apply Here</a></p>
        </div>
        <hr>
        """

    html += f"<p><b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
    return html


# ---------------------------
# SEND EMAIL
# ---------------------------

def send_email(jobs):
    if not EMAIL_USER or not EMAIL_PASSWORD or not RECIPIENT_EMAIL:
        raise Exception("Missing email environment variables!")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Daily Job Alerts - Matching Your Profile"
    msg["From"] = EMAIL_USER
    msg["To"] = RECIPIENT_EMAIL

    html_content = format_jobs_html(jobs)
    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, RECIPIENT_EMAIL, msg.as_string())
        server.quit()

        print("Email sent successfully!")

    except Exception as e:
        print("Email sending failed:", e)


# ---------------------------
# TEST RUN
# ---------------------------

if __name__ == "__main__":
    sample_jobs = [
        {
            "title": "Store Officer",
            "company": "ABC Logistics",
            "location": "Islamabad",
            "link": "https://example.com"
        }
    ]

    send_email(sample_jobs)
