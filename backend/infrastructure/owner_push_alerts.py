"""Aviso emergente para la dueña (Web Push) cuando Aura le pasa una pregunta que no sabe contestar.

Le llega aunque tenga el panel cerrado o esté viendo otra cosa. Se envía en segundo plano y después de
guardar en la base de datos, para no hacer esperar a la clienta.
"""

import logging
import threading

from django.db import close_old_connections, transaction
from django.db.models.signals import post_save

from application.commands.send_owner_push.command import SendOwnerPushCommand
from application.commands.send_owner_push.command_dto import SendOwnerPushCommandDTO
from domain.entities import HelpRequest
from infrastructure import dependencies

logger = logging.getLogger(__name__)


def send_in_background(title, body, url):
    def run():
        try:
            SendOwnerPushCommand(dependencies.get_repositories(), dependencies.get_push_service()).execute(
                SendOwnerPushCommandDTO(title=title, body=body, url=url)
            )
        except Exception:
            logger.exception("No se pudo enviar el aviso emergente a la dueña")
        finally:
            close_old_connections()

    if dependencies.get_push_service().is_enabled():
        transaction.on_commit(lambda: threading.Thread(target=run, daemon=True).start())


def on_help_request(sender, instance, created, **kwargs):
    if not created:
        return
    who = instance.client.name if instance.client else "Una clienta"
    send_in_background(f"🙋 {who} tiene una pregunta", instance.question, "/panel/mensajes")


def connect():
    post_save.connect(on_help_request, sender=HelpRequest, dispatch_uid="owner_push_help_request")
