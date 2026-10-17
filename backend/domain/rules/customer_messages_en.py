"""English versions of the messages clients read (same function names as customer_messages).

They are used when the client writes from the website in English. Owner and supplier messages stay in Spanish.
"""

import random

from domain.rules import spanish_format as fmt
from domain.rules.language import service_description, service_name


def _hi(name):
    return f", {name}" if name else ""


def _lower(service):
    return service_name(service).lower()


# ---------- receptionist ----------


def greeting(client_first_name, assistant_name, business_name, privacy_url=""):
    hello = f"Hi, {client_first_name}!" if client_first_name else "Hi!"
    text = (
        f"{hello} I’m {assistant_name}, from {business_name} 😊 "
        "I’ll remind you of your appointments and you can ask me anything: prices, opening hours or booking a slot. How can I help?"
    )
    if privacy_url:
        text += f"\n\nYour data is only used to manage your appointments. More info: {privacy_url}"
    return text


def short_greeting(client_first_name):
    return random.choice([f"Hi{_hi(client_first_name)}! How are you? How can I help?", f"Hello{_hi(client_first_name)}! Tell me 😊"])


def off_topic(business_name):
    return random.choice(
        [
            f"Oops, I can’t help with that 😅 I only handle things for {business_name}: appointments, treatments, prices and opening hours. Can I help with any of those?",
            f"That’s beyond me: here I can only help with {business_name} (appointments, treatments, prices and opening hours). Shall I find you a slot or tell you about a treatment?",
        ]
    )


def empty_message():
    return "Could you say that again? It didn’t come through 😊"


def thanks_reply(client_first_name):
    return random.choice(["You’re welcome! I’m here if you need anything 😊", f"No problem{_hi(client_first_name)}! Have a lovely day."])


def prices_text(services):
    lines = [f"• {service_name(service)}: {fmt.euros(service.price)} ({service.duration_minutes} min)" for service in services]
    return "Here are the prices:\n" + "\n".join(lines) + "\n\nIf you’d like to book one, just tap it 😊"


def ask_which_treatment():
    return random.choice(["Which one would you like?", "Pick the one you want and I’ll find you a slot:"])


def ask_which_category_prices():
    return "Of course! Which prices would you like to see?"


def service_price(service):
    return (
        f"{service_name(service)}: {fmt.euros(service.price)}, it takes about {service.duration_minutes} minutes. Shall I find you a slot?"
    )


def hours_text(opening_hours):
    """'Open Monday to Saturday, 10:00–14:00 and 16:00–20:00. Closed on Sundays.'"""
    if not opening_hours:
        return "I don’t have the opening hours to hand right now."
    ranges_by_day = {}
    for hours in opening_hours:
        ranges_by_day.setdefault(hours.weekday, []).append(f"{hours.opens:%H:%M}–{hours.closes:%H:%M}")

    groups = []
    for weekday in range(7):
        if weekday not in ranges_by_day:
            continue
        ranges = " and ".join(ranges_by_day[weekday])
        same_as_previous = groups and groups[-1]["ranges"] == ranges and groups[-1]["days"][-1] == weekday - 1
        if same_as_previous:
            groups[-1]["days"].append(weekday)
        else:
            groups.append({"days": [weekday], "ranges": ranges})

    parts = []
    for group in groups:
        days = group["days"]
        label = fmt.DAYS_EN[days[0]] if len(days) == 1 else f"{fmt.DAYS_EN[days[0]]} to {fmt.DAYS_EN[days[-1]]}"
        parts.append(f"{label}, {group['ranges']}")
    text = "Open " + "; ".join(parts)

    closed = [fmt.DAYS_EN[weekday] + "s" for weekday in range(7) if weekday not in ranges_by_day]
    if closed:
        text += f". Closed on {' and '.join(closed)}"
    return text + "."


def ask_which_service():
    return random.choice(["Of course! What would you like to have done?", "Great! Which treatment shall I find you a slot for?"])


def offer_slots_intro(service, with_price=False):
    name = _lower(service)
    if with_price:
        return f"Of course! The {name} is {fmt.euros(service.price)} ({service.duration_minutes} min). I have these slots:"
    return random.choice(
        [
            f"Of course! For {name} I have these slots:",
            f"I can fit you in for {name} here:",
            f"For {name} I have these free, pick the one that suits you best:",
        ]
    )


def service_info(service):
    description = f" {service_description(service)}" if service_description(service) else ""
    return f"Yes! We do {_lower(service)}.{description} It takes about {service.duration_minutes} minutes. Shall I find you a slot?"


def day_full_intro(part_of_day=None):
    if part_of_day in ("morning", "afternoon"):
        return f"Oops, nothing free that {part_of_day} 😕 Here’s the closest I have:"
    return random.choice(["That day is fully booked, sorry 😕", "Oops, I have nothing free that day."]) + " Here’s the closest I have:"


def more_days_intro():
    return "Sure, later on I have:"


def no_slots_soon(owner_name):
    return f"I can’t see any free slots in the next few weeks. I’ll let {owner_name} know and we’ll get back to you, OK?"


def ask_phone_for_booking(start):
    return f"Perfect, {fmt.when(start)}! Could you give me your mobile number? That way I save the appointment to your profile and we can let you know about any change 😊"


def phone_not_understood():
    return "Sorry, I didn’t catch the number. Could you type it again? (e.g. 600 123 456)"


def phone_needed_for_booking(business_phone):
    return f"I need it to save your appointment and keep you posted. If you prefer, call us on {business_phone} and we’ll book you in."


def ask_name_for_booking(start):
    return f"Perfect, {fmt.when(start)}! What name shall I put it under?"


def booking_confirmed(client_first_name, service_name_text, start, is_soon):
    after = "See you soon!" if is_soon else "I’ll message you the day before to remind you 😊"
    return random.choice(
        [
            f"Done, {client_first_name}! You’re booked {fmt.when(start)} for your {service_name_text.lower()}. {after}",
            f"All set, {client_first_name}! See you {fmt.when(start)} for your {service_name_text.lower()}. {after}",
        ]
    )


def slot_taken():
    return random.choice(["Oh, that time has just been taken 😕", "Oops, that time is no longer free."]) + " Would one of these work?"


def slot_taken_no_alternatives(owner_name):
    return f"Oh, that time has just been taken and I can’t see anything close. I’ll ask {owner_name} to find you a slot."


def appointment_cancelled(start):
    return f"Done, I’ve cancelled your appointment {fmt.relative_day(start)}. Whenever you want to come back, I’m here 😊"


def appointment_confirmed(client_first_name, start):
    return random.choice([f"Great, {client_first_name}! See you {fmt.when(start)} 😊", f"Perfect! We’ll see you {fmt.when(start)}."])


def appointment_rescheduled(client_first_name, start):
    return f"Changed! I’ll now see you {fmt.when(start)}. Thanks for letting us know, {client_first_name} 😊"


def which_new_time():
    return "Of course, no problem! Which one suits you better?"


def what_to_do_with_appointment():
    return "Don’t worry! What would you like to do with your appointment?"


def appointment_not_found():
    return "I can’t find that appointment under your name. Which day was it?"


def no_upcoming_appointments():
    return "I can’t see any appointment under your name right now. Tell me which day it was and I’ll check."


def maybe_later():
    return random.choice(["No problem! I’m here whenever you like 😊", "OK! Message me whenever you want."])


def service_not_available():
    return "Sorry, that service is no longer available."


def button_not_understood():
    return "Sorry, I didn’t get that. Could you type it?"


def i_am_virtual_assistant(business_name, owner_name):
    return (
        f"I’m the virtual assistant of {business_name} 😊 I help with appointments, prices and questions, "
        f"and if you need anything else, {owner_name} reads the messages and replies herself."
    )


def recommendation(topic, service):
    if topic == "event":
        opening = "How exciting! To look perfect I’d recommend:"
    elif topic == "relax":
        opening = random.choice(
            ["I hear you, those weeks take their toll. This would be perfect:", "Sorry to hear that. For that I’d recommend:"]
        )
    else:
        opening = "I’d recommend:"
    description = f" {service_description(service)}" if service_description(service) else ""
    return (
        f"{opening} {service_name(service)}.{description} It takes {service.duration_minutes} minutes and costs "
        f"{fmt.euros(service.price)}. Shall I find you a slot?"
    )


def ask_what_they_want():
    return "Tell me a bit about what you’d like (skin care, nails, relaxing...) and I’ll tell you what would suit you best 😊"


def ask_to_book_with_buttons():
    return "Shall I book it? Pick the time you prefer:"


# ---------- when the receptionist passes the question to the owner ----------


def handoff_telegram(owner_name, client_first_name):
    return random.choice(
        [
            f"I’d rather {owner_name} tells you about this, she knows best 😊 I’ve passed your message on and she’ll reply here as soon as she can.",
            f"Good question{_hi(client_first_name)}. I’ll pass it to {owner_name} and she’ll reply here shortly.",
        ]
    )


def handoff_web(owner_name):
    return f"Let me check with {owner_name} and I’ll reply here in a moment 😊"


def added_to_question(owner_name):
    return f"I’ll add that to what I passed on to {owner_name}, and she’ll answer it all together 😊"


def not_understood():
    return random.choice(
        [
            "Sorry, I didn’t quite get that 😅 Could you tell me a bit more about what you need?",
            "Hmm, I’m not sure I follow. What would you like to know or book?",
        ]
    )


def handoff_ask_phone():
    return "If you have to go, leave me your phone number and we’ll message you."


def talk_to_owner(owner_name, client_first_name):
    return f"Of course{_hi(client_first_name)}. I’ll pass your message to {owner_name} and she’ll write to you as soon as she can 😊"


def health_question(owner_name):
    return f"That’s important and I’d rather {owner_name} assesses it before recommending anything. I’ve passed your question on."


def phone_saved():
    return "Thanks! Noted. If I don’t catch you here, we’ll message that number 😊"


def phone_refused():
    return "No problem! I’ll reply here as soon as I know 😊"
