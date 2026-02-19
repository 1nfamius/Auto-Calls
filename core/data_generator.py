from faker import Faker
import random

fake = Faker("es_ES")

def generate_value(field_name, input_type="text", user_number=None):
    field = field_name.lower()

    # Teléfono fijo
    if "phone" in field or "tel" in field:
        return user_number if user_number else "+34" + fake.msisdn()[3:12]

    # DNI español
    if "dni" in field:
        number = str(random.randint(10000000, 99999999))
        letters = "TRWAGMYFPDXBNJZSQVHLCKE"
        letter = letters[int(number) % 23]
        return f"{number}{letter}"

    # Dirección completa
    if "address" in field or "direccion" in field:
        street = fake.street_name()
        number = random.randint(1, 100)
        floor = random.randint(1, 10)
        apt = random.choice(["A","B","C","D","E"])
        city = fake.city()
        postal = fake.postcode()
        return f"{street} {number}, {floor}{apt}, {postal} {city}, España"

    # Campos individuales de dirección
    if "street" in field:
        return fake.street_name()
    if "postal" in field or "zip" in field:
        return fake.postcode()
    if "city" in field or "localidad" in field:
        return fake.city()
    if "province" in field:
        return fake.province()
    if "country" in field or "pais" in field:
        return "España"
    if "floor" in field or "piso" in field:
        return str(random.randint(1, 10))
    if "apartment" in field or "apto" in field:
        return random.choice(["A","B","C","D","E","F"])
    if "number" in field or "portal" in field:
        return str(random.randint(1, 100))

    # Nombre, apellido, email
    if "name" in field or "nombre" in field:
        return fake.first_name()
    if "surname" in field or "apellido" in field:
        return fake.last_name()
    if "email" in field:
        return fake.email()

    # Número genérico
    if input_type == "number":
        return random.randint(1, 100)

    # Textarea o mensajes
    if input_type == "textarea" or "message" in field or "comment" in field:
        return fake.text(max_nb_chars=100)

    # Default
    return fake.word()
