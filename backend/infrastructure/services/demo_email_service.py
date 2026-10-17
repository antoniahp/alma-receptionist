import logging

from domain.services.email_service import EmailService

logger = logging.getLogger(__name__)


class DemoEmailService(EmailService):
    """En la demo pública no se manda ningún correo de verdad: solo se apunta en el log."""

    def send(self, to, subject, body):
        logger.info("Modo demo: correo a %s NO enviado (%s)", to, subject)
