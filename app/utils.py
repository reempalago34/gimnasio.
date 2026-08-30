from datetime import datetime, timedelta, timezone
import smtplib
from email.mime.text import MIMEText
from flask import current_app

def get_colombia_time():
    # Colombia is UTC-5
    offset = timezone(timedelta(hours=-5))
    # Return naive datetime representing Colombia time
    return datetime.now(offset).replace(tzinfo=None)

def get_colombia_date():
    return get_colombia_time().date()

def send_email(destinatario, asunto, cuerpo_html):
    """Envía un correo usando la configuración SMTP de la app. Lanza excepción si falla."""
    mail_server = current_app.config['MAIL_SERVER']
    mail_port = current_app.config['MAIL_PORT']
    mail_username = current_app.config['MAIL_USERNAME']
    mail_password = current_app.config['MAIL_PASSWORD']
    mail_sender = current_app.config['MAIL_DEFAULT_SENDER']

    if not mail_username or not mail_password:
        raise RuntimeError('El servicio de correo no está configurado (MAIL_USERNAME/MAIL_PASSWORD).')

    msg = MIMEText(cuerpo_html, 'html', 'utf-8')
    msg['Subject'] = asunto
    msg['From'] = mail_sender
    msg['To'] = destinatario

    with smtplib.SMTP(mail_server, mail_port, timeout=10) as server:
        if current_app.config.get('MAIL_USE_TLS'):
            server.starttls()
        server.login(mail_username, mail_password)
        server.sendmail(mail_sender, [destinatario], msg.as_string())
