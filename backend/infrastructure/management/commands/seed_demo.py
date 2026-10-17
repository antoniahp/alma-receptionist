from datetime import datetime, time, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from domain.entities import (
    Appointment,
    CashClosing,
    Client,
    ClientPack,
    Conversation,
    Expense,
    HelpRequest,
    Notification,
    OpeningHours,
    Product,
    PurchaseOrder,
    PurchaseOrderLine,
    Service,
    ServiceProduct,
    StockMovement,
    Supplier,
    TimeBlock,
    payment,
)

# Nombres y descripciones en inglés para la web en inglés
SERVICES_EN = {
    "higiene": ("Personalised facial cleanse", "Deep cleanse with extractions, mask and serum tailored to your skin."),
    "acne": ("Acne treatment", "Cleansing and soothing treatment for blemish-prone or oily skin."),
    "drenaje": ("Facial lymphatic drainage", "Gentle massage that reduces puffiness and decongests the face."),
    "contorno": ("Eye contour treatment", "For dark circles and puffiness: massage and a dedicated cream."),
    "masaje_facial": ("Facial massage", "Relaxing massage for face, neck and décolleté."),
    "peeling": ("Facial peel", "Exfoliation for smoother, brighter skin."),
    "mascarilla": ("Anti-stress mask", "Moisturising mask for tired skin."),
    "decoloracion": ("Facial hair bleaching", "Lightens hair on the upper lip or face."),
    "semi": ("Gel manicure", "Cuticle care, shaping and gel polish that lasts about three weeks."),
    "francesa": ("French gel manicure", "The classic white tip, in gel polish."),
    "tradicional": ("Classic manicure", "Cuticle care, shaping and regular polish."),
    "laca": ("Gel-effect polish", "Colour change with gel-effect polish."),
    "decoracion": ("Hand-painted nail art", "Hand-painted designs and details."),
    "pie": ("Pedicure", "Full pedicure: hard skin, cuticles, nails and polish."),
    "axilas": ("Underarm wax", ""),
    "ingles": ("Bikini wax", ""),
    "integral": ("Full Brazilian wax", ""),
    "brazos": ("Arm wax", ""),
    "media": ("Half leg wax", ""),
    "piernas": ("Full leg wax", ""),
    "labio": ("Upper lip wax", ""),
    "cara": ("Full face wax", ""),
    "pinzas": ("Eyebrow tweezing", ""),
    "diseno": ("Brow shaping", "We find the brow shape that suits your face best."),
    "laminado": ("Brow lamination", "Groomed, fuller brows for weeks."),
    "tinte": ("Brow or lash tint", ""),
    "permanente": ("Lash lift", "Curled lashes without a curler, for about six weeks."),
    "extensiones": ("Eyelash extensions", "Lash by lash, with a natural look."),
    "dia": ("Day make-up", "Natural, for a meeting or a photo."),
    "noche": ("Evening make-up", "For a party, a dinner or as a wedding guest."),
    "novia": ("Bridal make-up", "Includes a trial before the wedding day."),
    "cursillo": ("Self make-up lesson", "One-to-one class to learn to do your make-up with your own products."),
}

# Formas de pago repartidas como en un centro real: más tarjeta y Bizum que efectivo
PAYMENT_CYCLE = [payment.CARD, payment.CASH, payment.BIZUM, payment.CARD, payment.CASH]


class Command(BaseCommand):
    help = "Carga datos de ejemplo de un centro de estética (fechas relativas a hoy)."

    def add_arguments(self, parser):
        parser.add_argument("--keep", action="store_true", help="No borrar los datos existentes")
        parser.add_argument("--if-empty", action="store_true", help="Solo cargar si todavía no hay servicios")

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["if_empty"] and Service.objects.exists():
            self.stdout.write("Ya hay datos: no se cargan los de ejemplo.")
            return
        if not opts["keep"]:
            for model in (
                CashClosing,
                TimeBlock,
                Expense,
                HelpRequest,
                Notification,
                Conversation,
                StockMovement,
                PurchaseOrder,
                Appointment,
                ClientPack,
                ServiceProduct,
                Service,
                Product,
                Supplier,
                Client,
                OpeningHours,
            ):
                model.objects.all().delete()

        for wd in range(6):  # lunes a sábado
            OpeningHours.objects.create(weekday=wd, opens=time(10), closes=time(14))
            OpeningHours.objects.create(weekday=wd, opens=time(16), closes=time(20))

        # Marcas reales del sector. Los correos se dejan vacíos a propósito: la dueña pone el de su comercial
        # en el panel (Productos) antes del primer pedido, así nunca se envía nada a una dirección inventada.
        germaine = Supplier.objects.create(name="Germaine de Capuccini")
        opi = Supplier.objects.create(name="OPI")
        starpil = Supplier.objects.create(name="Starpil")
        refectocil = Supplier.objects.create(name="Refectocil")
        nagaraku = Supplier.objects.create(name="Nagaraku")
        laroche = Supplier.objects.create(name="La Roche-Posay")

        # Productos: cuántos usos da cada unidad, cuántos usos quedan y el mínimo por debajo del cual hay que pedir.
        # Los precios son aproximados: el comparador de precios del panel sirve para revisarlos.
        P = {}
        for key, name, ref, sup, price, upu, stock, mn in [
            (
                "mascarilla",
                "Germaine de Capuccini Purexpert mascarilla exfoliante purificante 75 ml",
                "GDC-PUR-75",
                germaine,
                "32.00",
                10,
                6,
                4,
            ),
            ("serum", "Germaine de Capuccini sérum vitamina C", "GDC-SVC", germaine, "45.00", 8, 9, 3),
            ("exfoliante", "Germaine de Capuccini gel exfoliante facial", "GDC-EXF", germaine, "28.00", 15, 12, 4),
            ("contorno", "Germaine de Capuccini contorno de ojos", "GDC-CO", germaine, "38.00", 10, 3, 3),
            ("aceite", "Germaine de Capuccini crema de masaje facial", "GDC-MAS", germaine, "30.00", 20, 14, 5),
            ("esmalte", "OPI GelColor esmalte semipermanente 15 ml", "OPI-GC-15", opi, "17.00", 10, 18, 6),
            ("quita", "OPI Expert Touch quitaesmalte 450 ml", "OPI-ET-450", opi, "12.00", 30, 26, 8),
            ("cera", "Starpil cera tibia natural 800 ml", "STP-NAT-800", starpil, "11.00", 25, 20, 10),
            ("tinte", "Refectocil tinte de cejas y pestañas 15 ml", "RFC-T-15", refectocil, "8.00", 15, 10, 4),
            ("laminado", "Refectocil kit lifting de pestañas", "RFC-LIFT", refectocil, "45.00", 36, 20, 6),
            ("pestanas", "Nagaraku pestañas para extensiones pelo a pelo", "NGK-CLS", nagaraku, "12.00", 4, 2, 2),
            ("effaclar", "La Roche-Posay Effaclar gel limpiador purificante 400 ml", "LRP-EFF-400", laroche, "17.00", 40, 30, 8),
            ("cicaplast", "La Roche-Posay Cicaplast Baume B5 100 ml", "LRP-CIC-100", laroche, "14.00", 25, 6, 5),
        ]:
            P[key] = Product.objects.create(
                name=name, reference=ref, supplier=sup, unit_price=Decimal(price), uses_per_unit=upu, stock_uses=stock, min_uses=mn
            )

        # Carta de un centro pequeño: nada que necesite cabina de spa ni aparatos grandes
        F, M, D, CP, MQ = Service.FACIAL, Service.HANDS_FEET, Service.WAXING, Service.BROWS_LASHES, Service.MAKEUP
        S = {}
        for key, category, name, desc, kw, dur, price, every, uses in [
            # Facial
            (
                "higiene",
                F,
                "Higiene facial personalizada",
                "Limpieza profunda con extracción, mascarilla y sérum adaptados a tu piel.",
                "limpieza,higiene,facial,poros,puntos negros,cutis",
                75,
                "45",
                30,
                {"exfoliante": 1, "mascarilla": 1, "serum": 1},
            ),
            (
                "acne",
                F,
                "Tratamiento acné",
                "Limpieza y tratamiento calmante para pieles con granitos o tendencia grasa.",
                "acne,granitos,granos,piel grasa",
                75,
                "50",
                21,
                {"effaclar": 1, "exfoliante": 1, "mascarilla": 1},
            ),
            (
                "drenaje",
                F,
                "Drenaje linfático facial",
                "Masaje suave que deshincha y descongestiona la cara.",
                "drenaje,linfatico,hinchazon,retencion",
                45,
                "50",
                None,
                {"aceite": 1},
            ),
            (
                "contorno",
                F,
                "Tratamiento contorno de ojos",
                "Para ojeras y bolsas: masaje y crema específica.",
                "ojeras,bolsas,contorno",
                35,
                "40",
                None,
                {"contorno": 1},
            ),
            (
                "masaje_facial",
                F,
                "Masaje facial",
                "Masaje relajante de cara, cuello y escote.",
                "masaje,relajar,relax",
                20,
                "20",
                None,
                {"aceite": 1},
            ),
            (
                "peeling",
                F,
                "Peeling facial",
                "Exfoliación para una piel más lisa y luminosa.",
                "peeling,exfoliacion,exfoliar",
                15,
                "20",
                None,
                {"exfoliante": 1},
            ),
            (
                "mascarilla",
                F,
                "Mascarilla antiestrés",
                "Mascarilla hidratante para la piel cansada.",
                "mascarilla",
                10,
                "10",
                None,
                {"mascarilla": 1},
            ),
            (
                "decoloracion",
                F,
                "Decoloración facial",
                "Aclara el vello del labio o la cara.",
                "decoloracion,decolorar",
                10,
                "10",
                None,
                {"cicaplast": 1},
            ),
            # Manos y pies
            (
                "semi",
                M,
                "Manicura semipermanente",
                "Limpieza de cutícula, forma y esmalte semipermanente que aguanta unas tres semanas.",
                "manicura,uñas,unas,esmalte,semipermanente",
                45,
                "25",
                21,
                {"esmalte": 1, "quita": 1},
            ),
            (
                "francesa",
                M,
                "Manicura francesa semipermanente",
                "La clásica punta blanca, en semipermanente.",
                "francesa",
                50,
                "35",
                21,
                {"esmalte": 2, "quita": 1},
            ),
            (
                "tradicional",
                M,
                "Manicura tradicional",
                "Cutícula, forma y esmalte normal.",
                "tradicional,manicura normal",
                30,
                "20",
                None,
                {"quita": 1},
            ),
            (
                "laca",
                M,
                "Laca especial gel",
                "Cambio de color en esmalte de efecto gel.",
                "laca,cambio de color",
                15,
                "15",
                None,
                {"esmalte": 1},
            ),
            (
                "decoracion",
                M,
                "Decoración de uñas a mano",
                "Dibujos y detalles hechos a mano.",
                "decoracion,dibujos,nail art",
                10,
                "10",
                None,
                {},
            ),
            (
                "pie",
                M,
                "Estética del pie",
                "Pedicura completa: durezas, cutícula, uñas y esmaltado.",
                "pedicura,pies,pie,durezas",
                50,
                "30",
                30,
                {"quita": 1},
            ),
            # Depilación (cera)
            ("axilas", D, "Depilación axilas", "", "axila,axilas", 10, "6", None, {"cera": 1}),
            ("ingles", D, "Depilación ingles", "", "ingle,ingles", 10, "8", None, {"cera": 1}),
            ("integral", D, "Depilación íntima integral", "", "integral,intima,brasileña", 15, "15", None, {"cera": 1}),
            ("brazos", D, "Depilación brazos", "", "brazos", 20, "20", None, {"cera": 2}),
            ("media", D, "Depilación media pierna", "", "media pierna", 15, "15", 28, {"cera": 2}),
            ("piernas", D, "Depilación piernas enteras", "", "piernas enteras,pierna entera,piernas", 25, "25", 28, {"cera": 3}),
            ("labio", D, "Depilación labio superior", "", "labio,bigote", 5, "4", None, {"cera": 1}),
            ("cara", D, "Depilación facial completa", "", "cara completa,depilacion facial", 10, "10", None, {"cera": 1, "cicaplast": 1}),
            ("pinzas", D, "Depilación de cejas con pinzas", "", "pinzas", 10, "8", None, {}),
            # Cejas y pestañas
            (
                "diseno",
                CP,
                "Diseño de cejas",
                "Te damos la forma que mejor va con tu cara.",
                "cejas,diseño de cejas",
                15,
                "15",
                30,
                {"cera": 1},
            ),
            (
                "laminado",
                CP,
                "Laminado de cejas",
                "Cejas peinadas y con volumen durante semanas.",
                "laminado",
                20,
                "20",
                42,
                {"laminado": 1},
            ),
            ("tinte", CP, "Tinte de cejas o pestañas", "", "tinte,teñir", 15, "15", None, {"tinte": 1}),
            (
                "permanente",
                CP,
                "Permanente de pestañas",
                "Pestañas curvadas sin rizador, unas seis semanas.",
                "permanente,rizar pestañas,lifting,lash lift",
                45,
                "45",
                42,
                {"laminado": 1},
            ),
            (
                "extensiones",
                CP,
                "Extensiones de pestañas",
                "Pestaña a pestaña, con efecto natural.",
                "extensiones,pestañas",
                90,
                "90",
                21,
                {"pestanas": 1},
            ),
            # Maquillaje
            ("dia", MQ, "Maquillaje de día", "Natural, para una reunión o una foto.", "maquillaje,maquillar", 30, "30", None, {}),
            (
                "noche",
                MQ,
                "Maquillaje de noche",
                "Para una fiesta, una cena o de invitada a una boda.",
                "noche,fiesta,evento,invitada",
                40,
                "40",
                None,
                {},
            ),
            ("novia", MQ, "Maquillaje de novia", "Incluye una prueba antes del día de la boda.", "novia", 45, "45", None, {}),
            (
                "cursillo",
                MQ,
                "Cursillo de automaquillaje",
                "Clase individual para aprender a maquillarte con tus productos.",
                "cursillo,curso,aprender a maquillarme",
                120,
                "120",
                None,
                {},
            ),
        ]:
            S[key] = Service.objects.create(
                category=category,
                name=name,
                description=desc,
                name_en=SERVICES_EN.get(key, ("", ""))[0],
                description_en=SERVICES_EN.get(key, ("", ""))[1],
                keywords=kw,
                duration_minutes=dur,
                price=Decimal(price),
                repeat_every_days=every,
            )
            for product_key, product_uses in uses.items():
                ServiceProduct.objects.create(service=S[key], product=P[product_key], uses=product_uses)

        C = {}
        for name, phone in [
            ("Laura Gómez", "611 111 111"),
            ("Marta Ruiz", "622 222 222"),
            ("Sofía Díaz", "633 333 333"),
            ("Elena Navarro", "644 444 444"),
            ("Carmen López", "655 555 555"),
            ("Lucía Romero", "666 666 666"),
            ("Ana Torres", "677 777 777"),
            ("Paula Moreno", "688 888 888"),
            ("Irene Castro", "699 999 999"),
            ("Nuria Vidal", "600 000 001"),
        ]:
            C[name.split()[0]] = Client.objects.create(name=name, phone=phone)

        today = timezone.localdate()

        def at(day, hhmm):
            h, m = map(int, hhmm.split(":"))
            return timezone.make_aware(datetime.combine(day, time(h, m)))

        def open_day(offset):
            d = today + timedelta(days=offset)
            while d.weekday() == 6:
                d += timedelta(days=1 if offset >= 0 else -1)
            return d

        past = [
            ("Laura", "semi", -22, "17:00"),
            ("Marta", "higiene", -32, "11:00"),
            ("Sofía", "piernas", -29, "18:00"),
            ("Elena", "higiene", -14, "10:00"),
            ("Carmen", "semi", -20, "18:30"),
            ("Lucía", "diseno", -7, "12:00"),
        ]
        # Carmen tiene un bono de 5 sesiones de semipermanente (ya ha usado una)
        carmen_pack = ClientPack.objects.create(
            client=C["Carmen"],
            service=S["semi"],
            sessions_total=5,
            sessions_used=1,
            price=S["semi"].price * 4,
            payment_method=payment.CARD,
            sold_at=at(open_day(-20), "18:00"),
        )
        for number, (who, svc, off, hhmm) in enumerate(past):
            with_pack = who == "Carmen" and svc == "semi"
            Appointment.objects.create(
                client=C[who],
                service=S[svc],
                start=at(open_day(off), hhmm),
                status=Appointment.COMPLETED,
                source=Appointment.SOURCE_OWNER,
                price=S[svc].price,
                payment_method=payment.PACK if with_pack else PAYMENT_CYCLE[number % len(PAYMENT_CYCLE)],
                pack=carmen_pack if with_pack else None,
            )

        future = [
            ("Lucía", "contorno", 0, "18:00"),
            ("Carmen", "semi", 0, "19:00"),
            ("Ana", "higiene", 1, "10:30"),
            ("Paula", "extensiones", 1, "17:00"),
            ("Irene", "pie", 1, "12:00"),
            ("Elena", "semi", 2, "11:00"),
            ("Nuria", "laminado", 4, "10:00"),
        ]
        for who, svc, off, hhmm in future:
            Appointment.objects.create(
                client=C[who], service=S[svc], start=at(open_day(off), hhmm), source=Appointment.SOURCE_WEB, price=S[svc].price
            )

        # Una tarde bloqueada para que se vea cómo queda en la agenda
        TimeBlock.objects.create(start=at(open_day(3), "16:00"), end=at(open_day(3), "20:00"), reason="Formación")

        self.create_history(today, C, S, P, at)

        self.stdout.write(self.style.SUCCESS("Datos de ejemplo cargados."))
        # En la demo pública se crea el usuario de prueba (DEMO_USERNAME / DEMO_PASSWORD) con su contraseña de siempre
        if settings.DEMO_MODE:
            user_model = get_user_model()
            user, _ = user_model.objects.get_or_create(username=settings.DEMO_USERNAME, defaults={"first_name": settings.BUSINESS["owner"]})
            user.set_password(settings.DEMO_PASSWORD)
            user.save()
            self.stdout.write(f"Usuario de la demo: {settings.DEMO_USERNAME}")
        # El usuario de pruebas en local: en producción se usa OWNER_USERNAME/OWNER_PASSWORD (ensure_owner)
        elif settings.DEBUG:
            user_model = get_user_model()
            user, created = user_model.objects.get_or_create(
                username="cris", defaults={"first_name": "Cris", "is_staff": True, "is_superuser": True}
            )
            if created:
                user.set_password("alma1234")
                user.save()
            self.stdout.write("Usuario del panel en local: cris / alma1234")

    def create_history(self, today, clients, services, products, at):
        """Seis meses de actividad para que la pestaña Cuentas tenga datos.

        Solo se usan servicios sin "repetir cada", para no llenar de avisos la pestaña Recordatorios.
        """
        one_off = [service for service in services.values() if service.repeat_every_days is None]
        client_list = list(clients.values())
        hours = ["10:30", "12:00", "17:00"]
        index = 0
        day = today - timedelta(days=180)
        while day <= today - timedelta(days=40):
            if day.weekday() != 6:
                for hhmm in hours:
                    service = one_off[index % len(one_off)]
                    Appointment.objects.create(
                        client=client_list[index % len(client_list)],
                        service=service,
                        start=at(day, hhmm),
                        status=Appointment.COMPLETED,
                        source=Appointment.SOURCE_OWNER,
                        price=service.price,
                        payment_method=PAYMENT_CYCLE[index % len(PAYMENT_CYCLE)],
                    )
                    index += 1
            day += timedelta(days=1)

        # Gastos fijos de cada mes
        month = today.replace(day=1)
        for _ in range(6):
            Expense.objects.create(concept="Alquiler del local", category=Expense.RENT, amount=Decimal("650"), date=month)
            Expense.objects.create(concept="Cuota de autónomos", category=Expense.SELF_EMPLOYED, amount=Decimal("300"), date=month)
            Expense.objects.create(concept="Fibra y teléfono", category=Expense.UTILITIES, amount=Decimal("35"), date=month)
            light = Decimal("80") + Decimal(month.month % 4) * Decimal("9.5")
            Expense.objects.create(concept="Luz", category=Expense.UTILITIES, amount=light, date=month + timedelta(days=9))
            month = (month - timedelta(days=1)).replace(day=1)

        # Pedidos ya recibidos en meses anteriores
        for days_ago, product_keys in [
            (150, ["esmalte", "quita"]),
            (110, ["cera", "tinte"]),
            (75, ["mascarilla", "serum"]),
            (45, ["esmalte", "cera"]),
        ]:
            sent_at = at(today - timedelta(days=days_ago), "10:00")
            supplier = products[product_keys[0]].supplier
            order = PurchaseOrder.objects.create(
                supplier=supplier, status=PurchaseOrder.RECEIVED, sent_at=sent_at, received_at=sent_at + timedelta(days=3)
            )
            for key in product_keys:
                product = products[key]
                if product.supplier_id == supplier.id:
                    PurchaseOrderLine.objects.create(order=order, product=product, units=3, unit_price=product.unit_price)
