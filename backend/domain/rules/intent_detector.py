"""Reglas para entender qué quiere la clienta cuando la IA local no está disponible."""

import re
from datetime import timedelta

from domain.rules.text_normalizer import normalize_text

ASK_IF_BOT = "ask_if_bot"
TALK_TO_OWNER = "talk_to_owner"
HEALTH_QUESTION = "health_question"
CHANGE_APPOINTMENT = "change_appointment"
BOOK = "book"
PRICES = "prices"
HOURS = "hours"
RECOMMEND = "recommend"
THANKS = "thanks"
SERVICE_INFO = "service_info"
GREETING = "greeting"
UNKNOWN = "unknown"

WEEKDAYS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
WEEKDAYS_EN = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
PHONE_PATTERN = re.compile(r"(\+?\d[\d\s.-]{7,}\d)")


def is_short_message(text):
    return len(normalize_text(text).split()) <= 5 and "?" not in text


HEALTH_PATTERN = re.compile(
    r"alergi|allerg|embaraz|pregnan|lactancia|breastfeed|medicac|medication|dermatitis|psoriasis|herida|wound|diabet|marcapasos|pacemaker"
)


# Lo que solo puede decidir la dueña: descuentos y grupos, regalos, aparcamiento, servicios que no hay,
# quejas de un servicio anterior y menores. El modelo no tiene esos datos y tiende a inventarlos.
OWNER_ONLY_PATTERN = re.compile(
    r"descuento|precio especial|oferta para|grupo de|despedida|discount|special price|group of|hen party"
    r"|regalo|regalar|gift|voucher"
    r"|aparca|parking|parkear"
    r"|\bspa\b|circuito|sauna|jacuzzi"
    r"|me hicisteis|se me ha (levantado|caido|roto|despegado)|no estoy contenta|from yesterday|chipping|chipped|came off|fell off|not happy with"
    r"|mi hij[oa]|menor de edad|anos de edad|\b1[0-7] anos\b|my daughter|my son|years old|teenager"
)

# Frases en las que el modelo afirma algo sobre la agenda: eso solo lo puede decir el código, con los huecos reales
AVAILABILITY_CLAIM = re.compile(
    r"complet|lleno|no (tenemos|hay|queda)n? (nada|hueco|huecos|sitio)|mira lo que tengo|tenemos huecos"
    r"|fully booked|no (slots|availability)|here'?s what i have|let me check what we have|we have (some )?(slots|availability)"
    r"|\bopenings\b|no opening|don'?t have (any|anything)|nothing (free|available|left)|(we'?re|i'?m|we are) (all |fully )?booked"
    r"|no (free )?(time|times|space|room)\b|no tengo (nada|hueco|huecos|sitio)|no me queda"
)

# Si la clienta no nombra un tratamiento concreto pero sí de qué tipo ("cejas", "manicure"), vamos directas a esa categoría.
# El orden importa: "eyebrows waxed" es de cejas, no de depilación corporal.
CATEGORY_WORDS = [
    ("cejas_pestanas", re.compile(r"\b(eye)?brows?\b|\blash|ceja|pestan")),
    ("manos_pies", re.compile(r"manicur|pedicur|\bnails?\b|\bunas?\b|\bmanos?\b|\bhands?\b|\bfeet\b|\bfoot\b|\bpies?\b")),
    ("maquillaje", re.compile(r"make-?up|maquill")),
    ("depilacion", re.compile(r"\bwax|depil|\bcera\b")),
    ("facial", re.compile(r"facial|\bface\b|\bcara\b|\bskin\b|\bpiel\b|cutis")),
]


def category_in_text(text):
    """La categoría que nombra la clienta, o None."""
    normalized = normalize_text(text)
    for key, pattern in CATEGORY_WORDS:
        if pattern.search(normalized):
            return key
    return None


OFFERS_BOOKING = re.compile(
    r"\b(book|booking|appointment|slot|reserv|cita|hueco|when (would|does|do) .* suit|cuando te (viene|va))"
)
AFFIRMATIVE = re.compile(
    r"^(si|yes|yeah|yep|ok|okay|vale|perfect|perfecto|perfecta|genial|great|claro|sure|please|por favor|venga|dale|de acuerdo|me interesa|i'?d like that)\b"
)


def offers_booking(reply):
    """El modelo le está ofreciendo cita ("¿te busco hueco?", "would you like to book?")."""
    return bool(OFFERS_BOOKING.search(normalize_text(reply)))


ASKS_FOR_TIME = re.compile(
    r"\b(anything|any (slot|time|space)|free|available|availability|slot|appointment|can i come|book"
    r"|hueco|libre|tienes algo|teneis algo|hay algo|cita|puedo ir|reserv)"
)


def asks_for_time(text):
    """Pide hueco ("¿tienes algo el miércoles?"), no pregunta otra cosa sobre ese día ("¿abrís el miércoles?")."""
    return bool(ASKS_FOR_TIME.search(normalize_text(text)))


def is_affirmative(text):
    """Un "sí" corto: "Perfect", "vale", "yes please"."""
    t = normalize_text(text).strip(" !.,")
    return len(t.split()) <= 4 and bool(AFFIRMATIVE.search(t))


def is_owner_only(text):
    return bool(OWNER_ONLY_PATTERN.search(normalize_text(text)))


def claims_availability(text):
    return bool(AVAILABILITY_CLAIM.search(normalize_text(text)))


def is_health_question(text):
    """Alergias, embarazo, medicación... Siempre lo decide la dueña, nunca el modelo."""
    return bool(HEALTH_PATTERN.search(normalize_text(text)))


def detect_intent(text, owner_name, mentions_service, mentions_day):
    t = normalize_text(text)
    owner = normalize_text(owner_name)

    if re.search(
        r"\b(eres|seras) (un |una )?(bot|robot|maquina|persona|humana|ia)\b|hablo con (un|una) (bot|persona|maquina)|are you (a )?(bot|robot|human|real person|ai)",
        t,
    ):
        return ASK_IF_BOT
    if re.search(rf"hablar con|queja|reclam|\b{owner}\b|persona real|encargad|speak to|talk to|complain|manager", t):
        return TALK_TO_OWNER
    if is_health_question(text):
        return HEALTH_QUESTION
    if re.search(
        r"anular|cancelar|cancel|no puedo ir|no podre|can't make it|cannot make it|reschedule|cambiar (la|mi) cita|mover (la|mi) cita|change my appointment",
        t,
    ):
        return CHANGE_APPOINTMENT
    if re.search(
        r"cita|hueco|reserv|disponib|libre|pedir hora|cuando (puedo|podeis|tienes)|me apuntas|quiero (hacerme|venir|un |una )|\bbook|appointment|available|free slot|i'?d like (a|an|to)|i want (a|an|to)",
        t,
    ):
        return BOOK
    if mentions_service and mentions_day:
        return BOOK
    if re.search(r"precio|cuesta|cuanto|tarifa|\bvale\b|valen|price|how much|cost", t):
        return PRICES
    if re.search(r"horario|abr|cierr|a que hora|donde est|direccion|opening|open\b|close|hours|where are|address", t):
        return HOURS
    if re.search(
        r"recomiend|aconsej|que me (hago|pongo)|piel|seca|cansad|estres|contractur|espalda|boda|evento|recommend|suggest|skin|tired|stress|wedding|party",
        t,
    ):
        return RECOMMEND
    if is_short_message(text) and re.search(r"\bgracias\b|genial|perfecto|\bvale\b|\bok\b|thank|great|perfect|cheers", t):
        return THANKS
    # Si nombra un tratamiento ("hola, ¿hacéis masajes?") le contamos qué es y le ofrecemos hueco
    if mentions_service:
        return SERVICE_INFO
    if is_short_message(text) and re.search(r"^(hola|buenas|buenos|hey|ey|hi|hello|good (morning|afternoon|evening))", t):
        return GREETING
    return UNKNOWN


QUESTION_START = (
    r"^(tene|tien|hace|hac|hay|se puede|puedo|podeis|pode|ofrece|admit|acept|cuando|como|donde|que|cual|quien|por que|"
    r"do you|can i|is there|are there|how|what|where|when|which|who)"
)


def is_question(text):
    """¿Es una pregunta de verdad ('¿tenéis piscina?', 'hacéis micropigmentación')? Una palabra suelta ('playa') no lo es:
    no tiene sentido molestar a la dueña con eso."""
    t = normalize_text(text)
    return "?" in text or re.search(QUESTION_START, t) is not None or len(t.split()) >= 4


def asks_price(text):
    """¿Pregunta cuánto cuesta? Solo entonces se le dice el precio al ofrecerle huecos."""
    return bool(re.search(r"precio|cuesta|cuanto (vale|es|sale|cobr)|tarifa|valen|price|how much|cost", normalize_text(text)))


def recommendation_topic(text):
    t = normalize_text(text)
    if re.search(r"piel|seca|granit|poros|cara|acne|skin|spots|pores|face", t):
        return "skin"
    if re.search(r"cansad|estres|contractur|espalda|relaj|duele|tired|stress|relax|back", t):
        return "relax"
    if re.search(r"boda|evento|fiesta|wedding|party|event", t):
        return "event"
    return None


def parse_day(text, today):
    """'mañana', 'hoy', 'el viernes'... Devuelve la fecha o None."""
    t = normalize_text(text)
    if "day after tomorrow" in t or "pasado manana" in t:
        return today + timedelta(days=2)
    if "tomorrow" in t or ("manana" in t and not re.search(r"por la manana|de manana", t)):
        return today + timedelta(days=1)
    if re.search(r"\bhoy\b|\btoday\b", t):
        return today
    for index, (name, name_en) in enumerate(zip(WEEKDAYS, WEEKDAYS_EN, strict=True)):
        if re.search(rf"\b({name}|{name_en})\b", t):
            days_ahead = (index - today.weekday()) % 7
            return today + timedelta(days=days_ahead or 7)
    return None


def parse_part_of_day(text):
    t = normalize_text(text)
    if re.search(r"por la manana|de manana|temprano|morning|early", t):
        return "morning"
    if "tarde" in t or "afternoon" in t or "evening" in t:
        return "afternoon"
    return None


def normalize_part_of_day(value):
    """La IA puede decir 'mañana' o 'tarde'; lo pasamos a morning/afternoon."""
    value = normalize_text(value or "")
    if value in ("morning", "manana"):
        return "morning"
    if value in ("afternoon", "tarde"):
        return "afternoon"
    return None


def extract_phone(text):
    match = PHONE_PATTERN.search(text or "")
    if not match:
        return None
    return re.sub(r"[^\d+]", "", match.group(1))


def is_refusal(text):
    return re.search(r"\b(no|prefiero no|mejor no|luego|no thanks|later)\b", normalize_text(text)) is not None


def clean_name(text):
    """'Me llamo Marta Ruiz' -> 'Marta Ruiz'. Devuelve None si no parece un nombre."""
    name = re.sub(
        r"^(soy|me llamo|a nombre de|de|i'?m|i am|my name is|it'?s|under)\s+", "", (text or "").strip(), flags=re.IGNORECASE
    ).strip(" .!")
    # Un nombre lleva letras y no cifras: "611 111 111" no es un nombre
    if 1 < len(name) <= 60 and len(name.split()) <= 4 and not re.search(r"\d", name) and re.search(r"[^\W\d_]{2}", name):
        return name.title()
    return None


OWNER_HANDOFF_VERBS = r"(pas|coment|pregunt|consult|dig|avis|escrib|contest|llam|lo mir|lo vea|te cuente)"
FALSE_ACTION_CLAIM = r"\b(te )?(he|dejo) (reservad|apuntad|cogid|anulad)"


def mentions_owner_handoff(text, owner_name):
    """¿La respuesta dice que algo lo resolverá la dueña? ('se lo paso a Cris', 'pregúntale a Cris'...)."""
    t = normalize_text(text)
    return normalize_text(owner_name) in t and re.search(OWNER_HANDOFF_VERBS, t) is not None


def claims_false_action(text):
    """¿El texto dice que se ha reservado o anulado algo? Solo es válido si de verdad se hizo."""
    return re.search(FALSE_ACTION_CLAIM, normalize_text(text)) is not None
