import xml.etree.cElementTree as ET


FORMAT_MAP = {
    "String": "ru.runa.wfe.var.format.StringFormat",
    "Long": "ru.runa.wfe.var.format.LongFormat",
    "Double": "ru.runa.wfe.var.format.DoubleFormat",
    "Boolean": "ru.runa.wfe.var.format.BooleanFormat",
    "Date": "ru.runa.wfe.var.format.DateFormat",
    "Executor": "ru.runa.wfe.var.format.ExecutorFormat",
    "File": "ru.runa.wfe.var.format.FileFormat",
    "List": "ru.runa.wfe.var.format.ListFormat",
}


def indent(elem, level=0):
    i = "\n" + level * "  "

    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "

        for child in elem:
            indent(child, level + 1)

        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def normalize_format(value):
    value = str(value).strip()

    if value in FORMAT_MAP:
        return FORMAT_MAP[value]

    if value.startswith("ru.runa.wfe.var.format.") and value.endswith("Format"):
        return value

    raise ValueError(f"Неизвестный тип переменной: {value}")


def build_variables_root(variables_data):
    root = ET.Element("variables")

    for variable_data in variables_data:
        name = str(variable_data["name"]).strip()
        variable_format = normalize_format(variable_data["format"])
        default_value = str(variable_data.get("default", "")).strip()
        element_format = str(variable_data.get("element_format", "")).strip()

        if not name:
            raise ValueError("Название переменной не может быть пустым")

        attributes = {
            "name": name,
            "scriptingName": name,
            "format": variable_format,
        }

        if default_value:
            attributes["defaultValue"] = default_value

        if variable_format == "ru.runa.wfe.var.format.ListFormat":
            if not element_format:
                raise ValueError(f"Для переменной-списка {name} не указан тип элемента")

            attributes["elementFormat"] = normalize_format(element_format)

        ET.SubElement(root, "variable", attributes)

    return root


def variables_builder(variables_data, filename="variables"):
    root = build_variables_root(variables_data)
    indent(root)

    xml_str = ET.tostring(root, encoding="unicode", method="xml")
    xml_str = xml_str.replace(" />", "/>")

    with open(f"./{filename}.xml", "w", encoding="utf-8") as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
        file.write(xml_str)
        file.write("\n")


def gather_variables_data():
    variables_data = []

    print("Введите количество переменных")
    variables_count = int(input())

    for i in range(variables_count):
        print(f"Введите название переменной {i + 1}")
        name = input().strip()

        print("Введите тип переменной")
        print("Доступные типы: String, Long, Double, Boolean, Date, Executor, File, List")
        variable_format = input().strip()

        variable_data = {
            "name": name,
            "format": variable_format,
            "default": "",
        }

        if variable_format == "List":
            print("Введите тип элемента списка")
            print("Доступные типы элементов: String, Long, Double, Boolean, Date, Executor, File")
            variable_data["element_format"] = input().strip()

        print("Введите значение по умолчанию или оставьте строку пустой")
        variable_data["default"] = input().strip()

        variables_data.append(variable_data)

    return variables_data
