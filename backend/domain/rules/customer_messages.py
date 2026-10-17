"""Textos que leen las clientas y proveedores. Están juntos para cuidar el tono en un solo sitio."""

import random

from domain.rules import customer_messages_en
from domain.rules import spanish_format as fmt
from domain.rules.language import in_spanish, is_english


def _hi(name):
    return f", {name}" if name else ""


# ---------- recepcionista ----------


def greeting(client_first_name, assistant_name, business_name, privacy_url=""):
    hello = f"¡Hola, {client_first_name}!" if client_first_name else "¡Hola!"
    text = (
        f"{hello} Soy {assistant_name}, de {business_name} 😊 "
        "Por aquí te aviso de tus citas y me puedes preguntar lo que quieras: precios, horarios o pedirme hueco. ¿En qué te ayudo?"
    )
    if privacy_url:
        text += f"\n\nTus datos solo se usan para gestionar tus citas. Más info: {privacy_url}"
    return text


def short_greeting(client_first_name):
    return random.choice(
        [f"¡Hola{_hi(client_first_name)}! ¿Qué tal? ¿En qué te puedo ayudar?", f"¡Buenas{_hi(client_first_name)}! Cuéntame 😊"]
    )


def off_topic(business_name):
    return random.choice(
        [
            f"Uy, en eso no te puedo ayudar 😅 Yo solo llevo las cosas de {business_name}: citas, tratamientos, precios y horarios. ¿Te ayudo con algo de eso?",
            f"Eso se me escapa: aquí solo te puedo ayudar con lo de {business_name} (citas, tratamientos, precios y horarios). ¿Te busco hueco o te cuento algún tratamiento?",
        ]
    )


def empty_message():
    return "¿Me lo repites? No me ha llegado bien 😊"


def thanks_reply(client_first_name):
    return random.choice(["¡A ti! Cualquier cosa, aquí estoy 😊", f"¡De nada{_hi(client_first_name)}! Que tengas buen día."])


def prices_text(services):
    lines = [f"• {service.name}: {fmt.euros(service.price)} ({service.duration_minutes} min)" for service in services]
    return "Te paso los precios:\n" + "\n".join(lines) + "\n\nSi quieres reservar alguno, púlsalo 😊"


def ask_which_treatment():
    return random.choice(["¿Cuál te apetece?", "Elige el que quieras y te busco hueco:"])


def ask_which_category_prices():
    return "¡Claro! ¿De qué te paso los precios?"


def service_price(service):
    return f"{service.name}: {fmt.euros(service.price)}, son unos {service.duration_minutes} minutos. ¿Quieres que te busque hueco?"


def hours_text(opening_hours):
    """Convierte la lista de horarios en una frase: 'Abrimos de lunes a sábado, de 10:00 a 14:00 y de 16:00 a 20:00...'."""
    if not opening_hours:
        return "Ahora mismo no tengo el horario a mano."
    ranges_by_day = {}
    for hours in opening_hours:
        ranges_by_day.setdefault(hours.weekday, []).append(f"{hours.opens:%H:%M} a {hours.closes:%H:%M}")

    groups = []
    for weekday in range(7):
        if weekday not in ranges_by_day:
            continue
        ranges = " y de ".join(ranges_by_day[weekday])
        same_as_previous = groups and groups[-1]["ranges"] == ranges and groups[-1]["days"][-1] == weekday - 1
        if same_as_previous:
            groups[-1]["days"].append(weekday)
        else:
            groups.append({"days": [weekday], "ranges": ranges})

    parts = []
    for group in groups:
        days = group["days"]
        label = fmt.DAYS[days[0]] if len(days) == 1 else f"{fmt.DAYS[days[0]]} a {fmt.DAYS[days[-1]]}"
        parts.append(f"de {label}, de {group['ranges']}")
    text = "Abrimos " + "; ".join(parts)

    closed = [fmt.DAYS[weekday] for weekday in range(7) if weekday not in ranges_by_day]
    if closed:
        plural = [day if day.endswith("s") else day + "s" for day in closed]
        text += f". Los {' y los '.join(plural)} cerramos"
    return text + "."


def ask_which_service():
    return random.choice(["¡Claro! ¿Qué te apetece hacerte?", "¡Genial! ¿Para qué tratamiento te busco hueco?"])


def offer_slots_intro(service, with_price=False):
    """Siempre dice de qué tratamiento son las horas. El precio, solo si la clienta lo ha preguntado."""
    name = service.name.lower()
    if with_price:
        return f"¡Claro! El {name} son {fmt.euros(service.price)} ({service.duration_minutes} min). Tengo estos huecos:"
    return random.choice(
        [
            f"¡Claro! Para {name} tengo estos huecos:",
            f"Para {name} te puedo hacer hueco aquí:",
            f"Para {name} tengo libre esto, elige el que mejor te venga:",
        ]
    )


def service_info(service):
    """Responde a '¿hacéis masajes?' sin dar el precio si no lo pide."""
    description = f" {service.description}" if service.description else ""
    return f"¡Sí! Hacemos {service.name.lower()}.{description} Son unos {service.duration_minutes} minutos. ¿Te busco hueco?"


def day_full_intro(part_of_day=None):
    if part_of_day in ("morning", "afternoon"):
        when = "esa mañana" if part_of_day == "morning" else "esa tarde"
        return f"Uy, {when} no me queda nada libre 😕 Te dejo lo más cercano que tengo:"
    return (
        random.choice(["Ese día lo tengo completo, lo siento 😕", "Uy, ese día no me queda nada libre."])
        + " Te dejo lo más cercano que tengo:"
    )


def more_days_intro():
    return "Claro, más adelante tengo:"


def no_slots_soon(owner_name):
    return f"Ahora mismo no veo huecos en las próximas semanas. Se lo comento a {owner_name} y te escribimos, ¿vale?"


def ask_phone_for_booking(start):
    return f"¡Perfecto, {fmt.when(start)}! ¿Me dejas tu móvil? Así guardo la cita en tu ficha y podemos avisarte si hay cualquier cambio 😊"


def phone_not_understood():
    return "Perdona, no me ha llegado bien el número. ¿Me lo escribes otra vez? (por ejemplo, 600 123 456)"


def phone_needed_for_booking(business_phone):
    return f"Lo necesito para guardarte la cita y poder avisarte. Si lo prefieres, llámanos al {business_phone} y te la apuntamos."


def ask_name_for_booking(start):
    return f"¡Perfecto, {fmt.when(start)}! ¿A nombre de quién la apunto?"


def booking_confirmed(client_first_name, service_name, start, is_soon):
    after = "¡Hasta luego!" if is_soon else "El día antes te escribo para recordártelo 😊"
    return random.choice(
        [
            f"¡Hecho, {client_first_name}! Te he apuntado {fmt.when(start)} para tu cita de {service_name.lower()}. {after}",
            f"¡Listo, {client_first_name}! Te espero {fmt.when(start)} para tu cita de {service_name.lower()}. {after}",
        ]
    )


def slot_taken():
    return (
        random.choice(["Vaya, justo esa hora se me acaba de ocupar 😕", "Uy, esa hora ya no la tengo."]) + " ¿Te va bien alguna de estas?"
    )


def slot_taken_no_alternatives(owner_name):
    return f"Vaya, esa hora se acaba de ocupar y no veo nada cerca. Se lo digo a {owner_name} para que te busque un hueco."


def appointment_cancelled(start):
    return f"Hecho, te he anulado la cita de {fmt.relative_day(start)}. Cuando quieras volver, aquí me tienes 😊"


def appointment_confirmed(client_first_name, start):
    return random.choice([f"¡Genial, {client_first_name}! Nos vemos {fmt.when(start)} 😊", f"¡Perfecto! Te esperamos {fmt.when(start)}."])


def appointment_rescheduled(client_first_name, start):
    return f"¡Cambiado! Ahora te espero {fmt.when(start)}. Gracias por avisar, {client_first_name} 😊"


def which_new_time():
    return "¡Claro, sin problema! ¿Cuál te viene mejor?"


def what_to_do_with_appointment():
    return "¡No te preocupes! ¿Qué quieres hacer con tu cita?"


def appointment_not_found():
    return "No encuentro esa cita a tu nombre. ¿Me dices qué día era?"


def no_upcoming_appointments():
    return "No veo ninguna cita a tu nombre ahora mismo. ¿Me dices qué día era y lo miro?"


def maybe_later():
    return random.choice(["¡Sin problema! Aquí estoy cuando te apetezca 😊", "¡Vale! Cuando quieras me escribes."])


def service_not_available():
    return "Ese servicio ya no está disponible, perdona."


def button_not_understood():
    return "Perdona, no he entendido eso. ¿Me lo escribes?"


def i_am_virtual_assistant(business_name, owner_name):
    return (
        f"Soy la asistente virtual de {business_name} 😊 Te ayudo con citas, precios y dudas, "
        f"y si necesitas algo más, {owner_name} lee los mensajes y te contesta ella."
    )


def recommendation(topic, service):
    if topic == "event":
        opening = "¡Qué ilusión! Para ir perfecta te recomendaría:"
    elif topic == "relax":
        opening = random.choice(
            ["Uf, te entiendo, esas semanas pasan factura. Te vendría genial esto:", "Vaya, lo siento. Para eso te recomendaría:"]
        )
    else:
        opening = "Yo te recomendaría:"
    description = f" {service.description}" if service.description else ""
    return f"{opening} {service.name}.{description} Son {service.duration_minutes} minutos y {fmt.euros(service.price)}. ¿Te busco hueco?"


def ask_what_they_want():
    return "Cuéntame un poco qué te gustaría (cuidar la piel, uñas, relajarte...) y te digo qué te iría mejor 😊"


def ask_to_book_with_buttons():
    return "¿Te la reservo? Elige la hora que prefieras:"


# ---------- cuando la recepcionista pasa la pregunta a la dueña ----------


def handoff_telegram(owner_name, client_first_name):
    return random.choice(
        [
            f"Esto prefiero que te lo cuente {owner_name}, que lo sabe mejor que yo 😊 Ya le he pasado tu mensaje y te escribe por aquí en cuanto pueda.",
            f"Buena pregunta{_hi(client_first_name)}. Se la paso a {owner_name} y te contesta ella por aquí en un ratito.",
        ]
    )


def handoff_web(owner_name):
    return f"Déjame que lo consulte con {owner_name} y te contesto por aquí en un momento 😊"


def added_to_question(owner_name):
    return f"Se lo añado a lo que le he pasado a {owner_name} y te contesta todo junto 😊"


def not_understood():
    return random.choice(
        [
            "Perdona, no te he entendido 😅 ¿Me cuentas un poco más qué necesitas?",
            "Uy, no sé si te sigo. ¿Qué te gustaría saber o reservar?",
        ]
    )


def handoff_ask_phone():
    return "Si tienes que irte, déjame tu teléfono y te escribimos."


def talk_to_owner(owner_name, client_first_name):
    return f"Claro{_hi(client_first_name)}. Le paso tu mensaje a {owner_name} y te escribe ella en cuanto pueda 😊"


def health_question(owner_name):
    return f"Eso es importante y prefiero que lo valore {owner_name} antes de recomendarte nada. Ya le he pasado tu pregunta."


def phone_saved():
    return "¡Gracias! Lo apunto. Si no te pillo por aquí, te escribimos a ese número 😊"


def phone_refused():
    return "¡Sin problema! Te contesto por aquí en cuanto lo sepa 😊"


# ---------- avisos ----------


@in_spanish
def reminder_text(appointment, business_name):
    opening = random.choice(["¡Hola, {name}!", "Hola, {name} 😊", "¡Buenas, {name}!"]).format(name=appointment.client.first_name)
    return (
        f"{opening} Te escribo para recordarte que {fmt.when(appointment.start)} te esperamos en {business_name} "
        f"para tu cita de {appointment.service.name.lower()}.\n\n"
        "¿Nos confirmas que vienes? Si te ha surgido algo, no pasa nada: dímelo y te busco otro hueco."
    )


@in_spanish
def review_request(client_first_name, business_name, review_url):
    return (
        f"¡Hola{_hi(client_first_name)}! Gracias por confiar en {business_name} 💚 "
        f"Si estás contenta, nos ayudaría muchísimo que dejaras una reseña en Google: {review_url}\n"
        "Y si algo se puede mejorar, cuéntamelo por aquí."
    )


@in_spanish
def reactivation_text(candidate, slots):
    weeks = max(1, round(candidate.days_since / 7))
    every = max(1, round(candidate.service.repeat_every_days / 7))
    options = " o ".join(fmt.when(slot) for slot in slots[:2])
    text = (
        f"¡Hola, {candidate.client.first_name}! ¿Qué tal estás? Ya han pasado {weeks} semana{'s' if weeks > 1 else ''} "
        f"desde tu {candidate.service.name.lower()} y, para que te dure el resultado, lo ideal es repetir cada "
        f"{every} semana{'s' if every > 1 else ''}. "
    )
    if options:
        return text + f"Tengo hueco {options}. ¿Te guardo alguno?"
    return text + "¿Quieres que te busque un hueco?"


# ---------- dueña ----------


@in_spanish
def owner_new_booking(source_label, client_name, service_name, start):
    return f"📅 Nueva cita por {source_label}: {client_name} · {service_name} · {fmt.day_long(start)} a las {fmt.hour(start)}"


@in_spanish
def owner_cancelled(client_name, service_name, start):
    return f"❌ {client_name} ha anulado su cita de {service_name} ({fmt.day_long(start)} {fmt.hour(start)})"


@in_spanish
def owner_rescheduled(client_name, service_name, old_start, new_start):
    return (
        f"🔄 {client_name} ha cambiado su {service_name} de {fmt.day_short(old_start)} {fmt.hour(old_start)} "
        f"a {fmt.day_short(new_start)} {fmt.hour(new_start)}"
    )


@in_spanish
def owner_help_alert(client_name, question, channel, contact):
    channel_label = "Telegram" if channel == "telegram" else "la web"
    text = f"🙋 {client_name} tiene una pregunta que no he sabido contestar:\n\n«{question[:600]}»\n\nEscribió por {channel_label}"
    if contact:
        text += f" · Tel. {contact}"
    return text + "\n\n👉 Responde a este mensaje (o desde el panel) y le llega en su chat como si contestara yo."


@in_spanish
def owner_phone_left(client_name, phone):
    return f"📞 {client_name} ha dejado su teléfono por si cierra el chat: {phone}"


@in_spanish
def owner_reply_how_to(pending_count):
    pending = f"Tienes {pending_count} pregunta(s) esperando." if pending_count else "Ahora mismo no hay preguntas pendientes."
    return "Para contestar a una clienta, mantén pulsado su aviso y elige «Responder». " + pending


@in_spanish
def signed_by_owner(owner_name, text):
    return f"Soy {owner_name} 😊 {text}"


# ---------- proveedores ----------


@in_spanish
def order_email(business, supplier, lines):
    """lines: lista de (producto, unidades)."""
    items = []
    for product, units in lines:
        reference = f" (ref. {product.reference})" if product.reference else ""
        items.append(f"- {units} × {product.name}{reference}")
    hello = f"Hola {supplier.contact_name}:" if supplier.contact_name else "Hola:"
    body = (
        f"{hello}\n\n"
        f"Os escribimos desde {business['name']}. Queremos haceros el siguiente pedido:\n\n" + "\n".join(items) + "\n\n"
        "¿Nos podéis confirmar el precio actual y el plazo de entrega? Si pudiera llegar esta semana, nos vendría genial.\n\n"
        f"Muchas gracias,\n{business['owner']}\n{business['name']} · {business['phone']}"
    )
    subject = f"Pedido de {business['name']}"
    return subject, body


# ---------- inglés ----------
# Si la clienta habla en inglés (web en inglés), cada texto de arriba que tenga versión en
# customer_messages_en se cambia por esa. Las funciones de la dueña y de proveedores siguen en español.


def _bilingual(spanish_function):
    english_function = getattr(customer_messages_en, spanish_function.__name__)

    def choose(*args, **kwargs):
        return (english_function if is_english() else spanish_function)(*args, **kwargs)

    choose.__name__ = spanish_function.__name__
    choose.__doc__ = spanish_function.__doc__
    return choose


for _name in [name for name in dir(customer_messages_en) if not name.startswith("_") and callable(getattr(customer_messages_en, name))]:
    if _name in globals() and _name not in ("random", "fmt", "service_name", "service_description"):
        globals()[_name] = _bilingual(globals()[_name])
