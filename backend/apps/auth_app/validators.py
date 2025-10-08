"""
Email validation utilities
"""

import dns.resolver
import dns.exception
import re
from typing import Tuple


def validate_email_format(email: str) -> bool:
    """Validate email format using regex"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_email_domain_exists(email: str) -> Tuple[bool, str]:
    """
    Validate that the email domain has valid MX (Mail Exchange) records.
    This checks if the domain can receive emails.

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    print(f"\n🌐 Verificando MX records para: {email}")

    try:
        # Extract domain from email
        domain = email.split("@")[1]
        print(f"📧 Dominio extraído: {domain}")

        # Check MX records
        try:
            print(f"🔍 Consultando DNS para MX records de: {domain}")
            mx_records = dns.resolver.resolve(domain, "MX")
            print(f"✅ MX records encontrados: {[str(mx) for mx in mx_records]}")
            if mx_records:
                return True, ""
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN) as e:
            error_msg = (
                f"El dominio '{domain}' no tiene servidores de correo configurados."
            )
            print(f"❌ Sin MX records: {error_msg} - Excepción: {type(e).__name__}")
            return (
                False,
                error_msg,
            )
        except dns.resolver.NoNameservers as e:
            error_msg = f"No se pudieron encontrar servidores DNS para '{domain}'."
            print(f"❌ Sin nameservers: {error_msg}")
            return False, error_msg
        except dns.exception.Timeout as e:
            print(f"⏰ Timeout en DNS, permitiendo (fail-open)")
            # If DNS timeout, we'll allow it (don't block user due to network issues)
            return True, ""

    except IndexError as e:
        error_msg = "Formato de correo electrónico inválido."
        print(f"❌ Error de formato: {error_msg}")
        return False, error_msg
    except Exception as e:
        # If any other error occurs, allow registration (fail open)
        # We don't want to block users due to temporary DNS issues
        print(f"⚠️ Error inesperado en validación DNS (permitiendo): {e}")
        return True, ""

    print(f"❌ No se pudo verificar el dominio")
    return False, "No se pudo verificar el dominio del correo electrónico."


def validate_email_complete(email: str) -> Tuple[bool, str]:
    """
    Complete email validation:
    1. Format validation
    2. Domain MX record validation

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # First check format
    if not validate_email_format(email):
        return False, "El formato del correo electrónico no es válido."

    # Then check domain
    return validate_email_domain_exists(email)
