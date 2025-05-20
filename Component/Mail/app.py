import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import create_engine

# MySQL connection (adjust username, password, and database name)
engine = create_engine('mysql+pymysql://root:your_password@127.0.0.1:3306/BudgetBountry')

# Test connection
with engine.connect() as conn:
    result = conn.execute("SELECT NOW()")
    print("Connected! Current time:", result.scalar())

def mail(to_mail, passcode):
    sender_email = "noreply.devsuriya@gmail.com"
    sender_password = "imaz xrtw yomb ttjq"
    
    message = MIMEMultipart("alternative")
    message['Subject'] = "Your OTP from BudgetBoundry"
    message["From"] = sender_email
    message["To"] = to_mail  # FIXED VARIABLE NAME
    
    text = f"Your OTP is: {passcode}"
    html = f"<p>Your <strong>One-Time Passcode</strong> is: <strong>{passcode}</strong></p>"

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_mail, message.as_string())