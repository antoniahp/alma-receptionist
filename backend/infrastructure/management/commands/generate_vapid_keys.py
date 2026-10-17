import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from django.core.management.base import BaseCommand


def b64url(data):
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


class Command(BaseCommand):
    help = "Genera las claves VAPID para los avisos emergentes del navegador. Cópialas en backend/.env."

    def handle(self, *args, **options):
        private_key = ec.generate_private_key(ec.SECP256R1())
        private_number = private_key.private_numbers().private_value.to_bytes(32, "big")
        public_bytes = private_key.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
        self.stdout.write("Añade estas dos líneas a backend/.env (y no las compartas):\n")
        self.stdout.write(f"VAPID_PUBLIC_KEY={b64url(public_bytes)}")
        self.stdout.write(f"VAPID_PRIVATE_KEY={b64url(private_number)}")
