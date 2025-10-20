from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import secrets
from .models import EmailConfirmationToken, PasswordResetToken


def generate_confirmation_token(user):
    """Generate a unique confirmation token for user"""
    token = secrets.token_urlsafe(32)
    expiresAt = timezone.now() + timedelta(minutes=3)
    EmailConfirmationToken.objects.create(user=user, token=token, expiresAt=expiresAt)
    return token


def send_confirmation_email(user, token):
    """Send confirmation email to user"""
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5174")
    logo_url = getattr(settings, "LOGO_URL", f"{frontend_url}/static/logo/logo.png")
    confirmation_link = f"{frontend_url}/confirm-email?token={token}"

    subject = "🚦 Confirma tu cuenta - TrafiSmart"

    text_content = f"""
    Hola {user.firstName},

    Bienvenido a TrafiSmart. Por favor confirma tu correo electrónico usando el siguiente enlace:

    {confirmation_link}

    Este enlace expirará en 3 minutos.

    Saludos,
    El equipo de TrafiSmart
    """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Confirma tu cuenta - TrafiSmart</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo-img {{
                max-width: 100px;
                height: auto;
                margin-bottom: 15px;
            }}
            .title {{
                font-size: 24px;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 20px;
            }}
            .content {{
                margin-bottom: 30px;
                color: #555;
            }}
            .button {{
                display: inline-block;
                background-color: #2043B2;
                color: white;
                text-decoration: none;
                padding: 14px 32px;
                border-radius: 20px;
                font-weight: 600;
                text-align: center;
                margin: 20px 0;
            }}
            .button:hover {{
                background-color: #1a3699;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                font-size: 14px;
                color: #888;
                text-align: center;
            }}
            .warning {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 12px;
                margin: 20px 0;
                font-size: 14px;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="{logo_url}" alt="TrafiSmart Logo" class="logo-img" />
                <h1 class="title">¡Confirma tu cuenta!</h1>
            </div>
            <div class="content">
                <p>Hola <strong>{user.firstName}</strong>,</p>
                <p>¡Bienvenido a TrafiSmart! Nos emociona que te unas a nuestra plataforma de análisis de tráfico inteligente.</p>
                <p>Para activar tu cuenta y comenzar a usar todas nuestras funcionalidades, por favor confirma tu correo electrónico:</p>
                <div style="text-align: center;">
                    <a href="{confirmation_link}" class="button" style="color: #ffffff !important;">
                        Confirmar mi cuenta
                    </a>
                </div>
                <div class="warning">
                    ⏰ Este enlace expirará en 3 minutos. Por favor confírmalo de inmediato.
                </div>
                <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
                <p style="word-break: break-all; color: #2043B2; font-size: 12px;">
                    {confirmation_link}
                </p>
            </div>
            <div class="footer">
                <p>Si no creaste esta cuenta, puedes ignorar este correo.</p>
                <p style="margin-top: 10px;">
                    © 2025 TrafiSmart. Todos los derechos reservados.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    email_from = getattr(settings, "EMAIL_FROM", settings.EMAIL_HOST_USER)
    email = EmailMultiAlternatives(
        subject=subject, body=text_content, from_email=email_from, to=[user.email]
    )
    email.attach_alternative(html_content, "text/html")

    try:
        email.send()
        print(f"✓ Confirmation email sent to {user.email}")
        return True
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False


def generate_password_reset_token(user):
    """Generate a unique password reset token for user"""
    token = secrets.token_urlsafe(32)
    expiresAt = timezone.now() + timedelta(minutes=2)
    PasswordResetToken.objects.create(user=user, token=token, expiresAt=expiresAt)
    return token


def send_password_reset_email(user, token):
    """Send password reset email to user"""
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5174")
    logo_url = getattr(settings, "LOGO_URL", f"{frontend_url}/static/logo/logo.png")
    reset_link = f"{frontend_url}/reset-password?token={token}"

    subject = "🔐 Recupera tu contraseña - TrafiSmart"

    text_content = f"""
    Hola {user.firstName},

    Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en TrafiSmart.

    Para crear una nueva contraseña, haz clic en el siguiente enlace:

    {reset_link}

    Este enlace expirará en 2 minutos por seguridad.

    Si no solicitaste este cambio, puedes ignorar este correo. Tu contraseña actual seguirá siendo válida.

    Saludos,
    El equipo de TrafiSmart
    """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Recupera tu contraseña - TrafiSmart</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo-img {{
                max-width: 100px;
                height: auto;
                margin-bottom: 15px;
            }}
            .title {{
                font-size: 24px;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 20px;
            }}
            .content {{
                margin-bottom: 30px;
                color: #555;
            }}
            .button {{
                display: inline-block;
                background-color: #2043B2;
                color: white;
                text-decoration: none;
                padding: 14px 32px;
                border-radius: 20px;
                font-weight: 600;
                text-align: center;
                margin: 20px 0;
            }}
            .button:hover {{
                background-color: #1a3699;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                font-size: 14px;
                color: #888;
                text-align: center;
            }}
            .warning {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 12px;
                margin: 20px 0;
                font-size: 14px;
                border-radius: 4px;
            }}
            .security {{
                background-color: #e3f2fd;
                border-left: 4px solid #2196f3;
                padding: 12px;
                margin: 20px 0;
                font-size: 14px;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="{logo_url}" alt="TrafiSmart Logo" class="logo-img" />
                <h1 class="title">Recupera tu contraseña</h1>
            </div>
            
            <div class="content">
                <p>Hola <strong>{user.firstName}</strong>,</p>
                <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en TrafiSmart.</p>
                <p>Para crear una nueva contraseña, haz clic en el siguiente botón:</p>
                
                <div style="text-align: center;">
                    <a href="{reset_link}" class="button" style="color: #ffffff !important;">
                        Restablecer mi contraseña
                    </a>
                </div>
                
                <div class="warning">
                    ⏰ Este enlace expirará en 2 minutos. Por favor úsalo de inmediato.
                </div>
                
                <div class="security">
                    🛡️ Si no solicitaste este cambio, ignora este correo. Tu contraseña actual seguirá siendo válida.
                </div>
                
                <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
                <p style="word-break: break-all; color: #2043B2; font-size: 12px;">
                    {reset_link}
                </p>
            </div>
            
            <div class="footer">
                <p>Si tienes problemas, contacta a nuestro equipo de soporte.</p>
                <p style="margin-top: 10px;">
                    © 2025 TrafiSmart. Todos los derechos reservados.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    email_from = getattr(settings, "EMAIL_FROM", settings.EMAIL_HOST_USER)
    email = EmailMultiAlternatives(
        subject=subject, body=text_content, from_email=email_from, to=[user.email]
    )
    email.attach_alternative(html_content, "text/html")

    try:
        email.send()
        print(f"✓ Password reset email sent to {user.email}")
        return True
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False


def send_welcome_email(user):
    """Send welcome email after successful email confirmation"""
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5174')
    logo_url = getattr(settings, 'LOGO_URL', f"{frontend_url}/static/logo/logo.png")
    login_url = f"{frontend_url}/login"

    subject = "🎉 ¡Bienvenido a TrafiSmart!"

    text_content = f"""
    Hola {user.firstName},

    ¡Tu cuenta ha sido confirmada exitosamente!

    Ya puedes acceder a todas las funcionalidades de TrafiSmart.

    Inicia sesión en: {login_url}

    Saludos,
    El equipo de TrafiSmart
    """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bienvenido - TrafiSmart</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo-img {{
                max-width: 100px;
                height: auto;
                margin-bottom: 15px;
            }}
            .success-icon {{
                font-size: 64px;
                margin: 20px 0;
            }}
            .title {{
                font-size: 24px;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 20px;
            }}
            .content {{
                margin-bottom: 30px;
                color: #555;
            }}
            .button {{
                display: inline-block;
                background-color: #2043B2;
                color: white;
                text-decoration: none;
                padding: 14px 32px;
                border-radius: 20px;
                font-weight: 600;
                text-align: center;
                margin: 20px 0;
            }}
            .button:hover {{
                background-color: #1a3699;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                font-size: 14px;
                color: #888;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="{logo_url}" alt="TrafiSmart Logo" class="logo-img" />
                <div class="success-icon">✅</div>
                <h1 class="title">¡Cuenta Activada!</h1>
            </div>
            
            <div class="content">
                <p>Hola <strong>{user.firstName}</strong>,</p>
                <p>¡Tu cuenta ha sido confirmada exitosamente!</p>
                <p>Ya puedes acceder a todas las funcionalidades de TrafiSmart y comenzar a analizar el tráfico de manera inteligente.</p>
                
                <div style="text-align: center;">
                    <a href="{login_url}" class="button" style="color: #ffffff !important;">
                        Iniciar Sesión
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <p>© 2025 TrafiSmart. Todos los derechos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """

    email_from = getattr(settings, "EMAIL_FROM", settings.EMAIL_HOST_USER)
    
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=email_from,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        print(f"✓ Welcome email sent to {user.email}")
        return True
        
    except Exception as e:
        print(f"Error sending welcome email to {user.email}: {e}")
        return False