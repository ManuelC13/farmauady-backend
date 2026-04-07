import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

def send_reset_password_email(to_email: str, token: str):
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("Las credenciales de correo (SMTP_USERNAME, SMTP_PASSWORD) no están configuradas.")
        return False

    msg = MIMEMultipart("alternative")
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = "Recuperación de Contraseña - FarmaUADY"
    
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"
    
    text_body = f"""Hola,

Has solicitado restablecer tu contraseña.
Usa el siguiente enlace para recuperar tu cuenta:

{reset_link}

Si no fuiste tú quien solicitó este cambio, puedes ignorar y eliminar este correo.

Saludos,
El equipo de FarmaUADY
"""

    html_body = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #fafafa; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #fafafa; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 500px; background-color: #ffffff; border: 1px solid #eaeaea; border-radius: 8px; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 40px 40px 30px 40px; text-align: left;">
                                
                                <p style="font-size: 16px; color: #333333; margin: 0 0 20px 0;">Hola,</p>
                                
                                <p style="font-size: 16px; color: #333333; line-height: 1.6; margin: 0 0 35px 0;">
                                    Has solicitado restablecer tu contraseña.<br>
                                    Usa el siguiente enlace para recuperar tu cuenta:
                                </p>
                                
                                <div style="text-align: center; margin: 40px 0;">
                                    <a href="{reset_link}" style="display: inline-block; background-color: #004a99; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 500; padding: 14px 32px; border-radius: 6px;">
                                        Restablecer contraseña
                                    </a>
                                </div>
                                
                                <p style="font-size: 14px; color: #666666; line-height: 1.6; margin: 0 0 40px 0;">
                                    Si no fuiste tú quien solicitó este cambio, puedes ignorar y eliminar este correo.
                                </p>
                                
                                <div style="border-top: 1px solid #eaeaea; padding-top: 25px;">
                                    <p style="font-size: 15px; color: #333333; margin: 0; line-height: 1.6;">
                                        Saludos,<br>
                                        <strong>El equipo de FarmaUADY</strong>
                                    </p>
                                </div>

                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    part1 = MIMEText(text_body, 'plain', 'utf-8')
    part2 = MIMEText(html_body, 'html', 'utf-8')
    
    msg.attach(part1)
    msg.attach(part2)
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Correo enviado exitosamente a {to_email}")
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False