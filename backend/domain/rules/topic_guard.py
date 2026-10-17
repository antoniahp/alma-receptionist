"""Límites de la recepcionista: solo habla del centro.

Aquí se detecta lo que claramente no tiene que ver con el centro (cálculos, deberes, programación,
cultura general...) y los intentos de cambiarle las instrucciones. Se contesta con un mensaje fijo:
no se gasta IA ni se molesta a la dueña.
"""

import re

from domain.rules.text_normalizer import normalize_text

OFF_TOPIC_PATTERNS = [
    # Cálculos y matemáticas
    # (ojo: "2x1" es una oferta, no una multiplicación; y "¿cuánto son 2 sesiones?" es una pregunta de precio)
    r"raiz cuadrada|raiz cubica|ecuacion|derivada|integral de|logaritmo|square root|equation|\d+\s*[-+*/^]\s*\d+",
    # Deberes, textos y traducciones
    r"(escribe|redacta|haz)(me)? (un|una) (poema|cuento|redaccion|ensayo|trabajo|carta|cancion|resumen|historia)",
    r"\btraduce|\btraduceme|como se dice .* en (ingles|frances|aleman|italiano)|\btranslate\b|write (me )?(a|an) (poem|story|essay|letter|song)",
    # Programación
    # (ojo: "programar una cita" sí es del centro)
    r"\bpython\b|javascript|\bsql\b|\bhtml\b|algoritmo|algorithm|programacion|programming|codigo fuente|source code",
    # Cultura general, actualidad, política, deportes
    r"capital of|president of|who (was|is|won|invented)|capital de|presidente (de|del)|quien (fue|es|gano|invento)|en que ano|elecciones|politic|futbol|partido de|liga\b|bolsa de valores|bitcoin",
    r"receta de|como se cocina|el tiempo (manana|hoy)|que tiempo hace",
    # Intentos de cambiarle el papel o sacarle las instrucciones
    r"ignora (las|tus|todas)|olvida (las|tus) instrucciones|instrucciones (del sistema|anteriores)|system prompt|\bprompt\b|ignore (all|your|previous)|you are now|act as|a partir de ahora eres|actua como|modo desarrollador|jailbreak",
]


def is_off_topic(text):
    t = normalize_text(text)
    return any(re.search(pattern, t) for pattern in OFF_TOPIC_PATTERNS)
