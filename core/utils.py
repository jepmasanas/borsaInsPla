from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(user, code):
    """Envía email de verificación con código usando Gmail SMTP"""

    subject = 'Verifica el teu compte - BorsaInsPla'

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); 
                       color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; }}
            .code {{ background: white; border: 2px dashed #2563eb; padding: 20px; 
                     text-align: center; font-size: 32px; font-weight: bold; 
                     letter-spacing: 8px; margin: 20px 0; border-radius: 8px; }}
            .footer {{ background: #1f2937; color: #9ca3af; padding: 20px; 
                      text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎓 BorsaInsPla</h1>
                <p>Borsa de Treball - Institut Pla de l'Estany</p>
            </div>
            <div class="content">
                <h2>Hola, {user.username}!</h2>
                <p>Gràcies per registrar-te a BorsaInsPla. Per completar el registre, 
                   si us plau verifica el teu compte introduint el següent codi:</p>

                <div class="code">{code}</div>

                <p><strong>Aquest codi expira en 15 minuts.</strong></p>

                <p>Si no has sol·licitat aquest registre, pots ignorar aquest email.</p>
            </div>
            <div class="footer">
                <p>© 2025 BorsaInsPla - Institut Pla de l'Estany</p>
                <p>Aquest és un email automàtic, si us plau no responguis.</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        print(f"Email enviado correctamente a {user.email}")
        return True

    except Exception as e:
        print(f"Error enviando email: {e}")
        return False


def send_password_recovery_email(user, code):
    """Envía email para recuperación de contraseña"""

    subject = 'Recupera la teva contrasenya - BorsaInsPla'

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); 
                       color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #fef2f2; padding: 30px; }}
            .code {{ background: white; border: 2px dashed #dc2626; padding: 20px; 
                     text-align: center; font-size: 32px; font-weight: bold; 
                     letter-spacing: 8px; margin: 20px 0; border-radius: 8px; color: #dc2626; }}
            .warning {{ background: #fee2e2; border-left: 4px solid #dc2626; 
                       padding: 15px; margin: 15px 0; border-radius: 4px; color: #991b1b; }}
            .footer {{ background: #1f2937; color: #9ca3af; padding: 20px; 
                      text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔑 Recuperació de Contrasenya</h1>
                <p>BorsaInsPla</p>
            </div>
            <div class="content">
                <h2>Hola, {user.username}!</h2>
                <p>Hem rebut una sol·licitud per recuperar la contrasenya del teu compte.</p>

                <div class="code">{code}</div>

                <p><strong>Introdueix aquest codi per establir una nova contrasenya.</strong></p>

                <div class="warning">
                    ⚠️ <strong>Seguretat:</strong> Aquest codi expira en 30 minuts. 
                    No comparteixis aquest codi amb ningú.
                </div>

                <p>Si no has sol·licitat aquesta recuperació de contrasenya, 
                   <strong>ignora aquest email</strong> i la teva contrasenya romandrà igual.</p>
            </div>
            <div class="footer">
                <p>© 2025 BorsaInsPla - Institut Pla de l'Estany</p>
                <p>Per a qüestions de seguretat, no responguis a aquest email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        print(f"Email de recuperación enviado a {user.email}")
        return True

    except Exception as e:
        print(f"Error enviando email de recuperación: {e}")
        return False


def send_welcome_email(user):
    """Envía email de bienvenida después de verificar"""

    subject = '¡Bienvenido a BorsaInsPla!'

    role_text = "Alumne/Exalumne" if user.role == 'alumno' else "Empresa" if user.role == 'empresa' else "Administrador"

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                       color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f0fdf4; padding: 30px; }}
            .features {{ list-style: none; padding: 0; }}
            .features li {{ padding: 10px 0; border-bottom: 1px solid #d1fae5; }}
            .features li:before {{ content: "✓ "; color: #10b981; font-weight: bold; margin-right: 10px; }}
            .footer {{ background: #1f2937; color: #9ca3af; padding: 20px; 
                      text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 ¡Bienvenido!</h1>
                <p>BorsaInsPla - Borsa de Treball</p>
            </div>
            <div class="content">
                <h2>Hola, {user.username}!</h2>
                <p>¡Felicitats! El teu email ha estat verificat correctament 
                   i el teu compte està actiu com a <strong>{role_text}</strong>.</p>

                <p><strong>Funcionalitats disponibles:</strong></p>
                <ul class="features">
                    <li>Accés complet a la plataforma</li>
                    <li>Perfil personalitzat</li>
                    <li>Notificacions i alerts</li>
                    <li>Suport tècnic 24/7</li>
                </ul>

                <p>Si tens alguna pregunta o necessites ajuda, no dubtes en contactar amb nosaltres.</p>
            </div>
            <div class="footer">
                <p>© 2025 BorsaInsPla - Institut Pla de l'Estany</p>
                <p><strong>Email:</strong> support@borsainspla.com</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        print(f"Email de bienvenida enviado a {user.email}")
        return True

    except Exception as e:
        print(f"Error enviando email de bienvenida: {e}")
        return False