from bs4 import BeautifulSoup
from core.data_generator import generate_value

def parse_form(html, user_number=None):
    soup = BeautifulSoup(html, "html.parser")
    form_data = {}

    # INPUTS
    for input_tag in soup.find_all("input"):
        name = input_tag.get("name")
        if not name:
            continue

        input_type = input_tag.get("type", "text")

        if input_type == "hidden":
            form_data[name] = input_tag.get("value", "")
        elif input_type == "checkbox":
            form_data[name] = "on"
        else:
            form_data[name] = generate_value(name, input_type, user_number)

    # TEXTAREAS
    for textarea in soup.find_all("textarea"):
        name = textarea.get("name")
        if name:
            form_data[name] = generate_value(name, "textarea", user_number)

    # SELECTS
    for select in soup.find_all("select"):
        name = select.get("name")
        if name:
            options = select.find_all("option")
            if options:
                form_data[name] = options[0].get("value")

    return form_data
