from faker import Faker
import random

fake = Faker("es_ES")

def generate_value(field_name, input_type="text", user_number=None):

    field = field_name.lower()

    # ── Teléfono ───────────────────────────────────────────────────────────────
    if "phone" in field or "tel" in field or "movil" in field or "telefono" in field:
        return user_number if user_number else "+34" + fake.msisdn()[3:12]

    # ── DNI español ───────────────────────────────────────────────────────────
    if "dni" in field or "nif" in field:
        number = str(random.randint(10000000, 99999999))
        letters = "TRWAGMYFPDXBNJZSQVHLCKE"
        letter = letters[int(number) % 23]
        return f"{number}{letter}"

    # ── Dirección completa ────────────────────────────────────────────────────
    if "address" in field or "direccion" in field:
        return (
            f"{fake.street_name()} {random.randint(1, 100)}, "
            f"{random.randint(1, 10)}{random.choice('ABCDEF')}, "
            f"{fake.postcode()} {fake.city()}, España"
        )

    # ── Campos individuales de dirección ──────────────────────────────────────
    if "street" in field:
        return fake.street_name()
    if "postal" in field or "zip" in field or "cp" in field:
        return fake.postcode()
    if "city" in field or "localidad" in field or "ciudad" in field:
        return fake.city()
    if "province" in field or "provincia" in field:
        return fake.province()
    if "country" in field or "pais" in field:
        return "España"
    if "floor" in field or "piso" in field:
        return str(random.randint(1, 10))
    if "apartment" in field or "apto" in field:
        return random.choice(list("ABCDEF"))
    if "number" in field or "portal" in field or "numero" in field:
        return str(random.randint(1, 100))

    # ── Datos personales ──────────────────────────────────────────────────────
    if "name" in field or "nombre" in field:
        return fake.first_name()
    if "surname" in field or "apellido" in field or "lastname" in field:
        return fake.last_name()
    if "email" in field or "correo" in field:
        return fake.email()

    # ── Textarea / mensajes ───────────────────────────────────────────────────
    if input_type == "textarea" or "message" in field or "comment" in field or "mensaje" in field:
        return fake.text(max_nb_chars=120)

    # ── Default ───────────────────────────────────────────────────────────────
    return fake.word()