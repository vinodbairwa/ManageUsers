import smtplib

def send_email(
    to_email: str,
    reset_link: str):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'bairwavinod499@gmail.com'
    smtp_password = 'eniv mczb yxgp mlql'
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        message = f"Subject: verification\n\n {reset_link}"
        server.sendmail(smtp_user, to_email, message)