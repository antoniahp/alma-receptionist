import importlib.util
import json
import logging

from django.conf import settings

from domain.exceptions import PushSubscriptionExpired
from domain.services.push_service import PushService

logger = logging.getLogger(__name__)
GONE_STATUSES = (404, 410)


def pywebpush_installed():
    """Si falta la librería (pip install pywebpush), el panel funciona igual pero sin avisos emergentes."""
    return importlib.util.find_spec("pywebpush") is not None


class WebPushService(PushService):
    """Envía avisos con el estándar Web Push (Chrome, Firefox, Edge, Safari). No hace falta ninguna cuenta externa."""

    def is_enabled(self):
        return bool(settings.VAPID_PUBLIC_KEY and settings.VAPID_PRIVATE_KEY) and pywebpush_installed()

    def public_key(self):
        return settings.VAPID_PUBLIC_KEY

    def send(self, subscription, title, body, url):
        from pywebpush import WebPushException, webpush

        try:
            webpush(
                subscription_info={"endpoint": subscription.endpoint, "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth}},
                data=json.dumps({"title": title, "body": body, "url": url}),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_SUBJECT},
                timeout=10,
            )
        except WebPushException as error:
            status = getattr(error.response, "status_code", None)
            if status in GONE_STATUSES:
                raise PushSubscriptionExpired() from error
            logger.warning("No se pudo enviar el aviso al navegador: %s", error)
