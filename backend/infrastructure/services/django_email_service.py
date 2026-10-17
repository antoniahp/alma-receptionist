import logging
import smtplib

from django.conf import settings
from django.core.mail import send_mail

from domain.exceptions import MessageNotSent
from domain.services.email_service import EmailService

logger = logging.getLogger(__name__)


class DjangoEmailService(EmailService):
    def send(self, to, subject, body):
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to])
        except (smtplib.SMTPException, OSError) as error:
            logger.warning("No se pudo enviar el correo a %s: %s", to, error)
            raise MessageNotSent("No se ha podido enviar el correo al proveedor. Revisa la configuración del correo.") from error
