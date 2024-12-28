import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from io import BytesIO

def send_email_with_excel(subject, body, email_config, json_data):

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = 'madheswaran.s@vknowlabs.com'
    sender_password = 'fgjs jzee unnp omwa'

    to_emails = email_config.get('to', [])
    cc_emails = email_config.get('cc', [])
    bcc_emails = email_config.get('bcc', [])
    all_recipients = to_emails + cc_emails + bcc_emails

    data = pd.DataFrame.from_dict(json_data, orient='index')
    data.reset_index(inplace=True)
    data.rename(columns={'index': 'Client Name'}, inplace=True)

    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        data.to_excel(writer, index=False, sheet_name='Summary')

    excel_buffer.seek(0) 

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = ', '.join(to_emails)
    message['Cc'] = ', '.join(cc_emails)
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(excel_buffer.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename='summary.xlsx')
    message.attach(part)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, all_recipients, text)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        server.quit()
