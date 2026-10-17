"""Errores de negocio. La API los convierte en respuestas con un mensaje claro para la persona."""


class DomainError(Exception):
    status_code = 400
    message = "No se ha podido completar la operación."

    def __init__(self, message=None):
        super().__init__(message or self.message)


class SlotNotAvailable(DomainError):
    status_code = 409
    message = "Ese hueco ya no está libre. Elige otra hora, por favor."


class InvalidBookingData(DomainError):
    message = "Servicio u hora no válidos."


class AppointmentNotActive(DomainError):
    message = "Esta cita ya no está activa."


class OrderNotDraft(DomainError):
    message = "Solo se pueden enviar o descartar pedidos en borrador."


class InvalidEmail(DomainError):
    message = "Ese correo no es válido. Revísalo, por favor."


class OrderNotSent(DomainError):
    message = "Solo se pueden recibir pedidos enviados."


class ReactivationNotDue(DomainError):
    message = "A esta clienta no le toca repetir ahora mismo."


class EmptyAnswer(DomainError):
    message = "Escribe una respuesta."


class MessageNotSent(DomainError):
    message = "No se ha podido enviar el mensaje."


class PriceSearchUnavailable(DomainError):
    message = "No se han podido buscar precios ahora mismo. Inténtalo en un rato."


class ShoppingListEmpty(DomainError):
    message = "No hay nada de esa tienda en la lista de compra."


class InvalidShoppingListItem(DomainError):
    message = "Revisa las unidades y el precio."


class InvalidExpense(DomainError):
    message = "Pon un concepto y un importe mayor que cero."


class InvalidClientData(DomainError):
    message = "Revisa los datos de la clienta."


class DuplicatedClient(DomainError):
    status_code = 409
    message = "Ya hay una clienta con ese teléfono."


class InvalidProductData(DomainError):
    message = "Revisa los datos del producto."


class NoActivePack(DomainError):
    message = "Esta clienta no tiene un bono con sesiones para este tratamiento."


class InvalidPayment(DomainError):
    message = "Elige cómo ha pagado: efectivo, tarjeta, Bizum o bono."


class CannotUndo(DomainError):
    message = "Ya no se puede deshacer: solo se puede durante los primeros minutos."


class InvalidPack(DomainError):
    message = "Revisa el bono: entre 2 y 50 sesiones y un precio válido."


class CashAlreadyClosed(DomainError):
    status_code = 409
    message = "La caja de ese día ya está cerrada."


class InvalidTimeBlock(DomainError):
    message = "Revisa las horas: el final tiene que ser después del principio."


class InvalidServiceData(DomainError):
    message = "Revisa los datos del tratamiento."


class PrivacyNotAccepted(DomainError):
    message = "Para reservar tienes que aceptar la política de privacidad."


class PushSubscriptionExpired(Exception):
    """El navegador ya no acepta avisos (se desuscribió o caducó). No llega a la API: se borra la suscripción."""


class LanguageModelUnavailable(Exception):
    """El modelo local no responde. No llega a la API: se usa el respaldo por reglas."""
