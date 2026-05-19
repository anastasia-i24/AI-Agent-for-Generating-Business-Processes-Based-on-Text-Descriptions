import xml.etree.cElementTree as ET

from beautiful_xml import indent


FORMAT_ALIASES = {
    "1": "Boolean",
    "2": "Long",
    "3": "Double",
    "4": "BigDecimal",
    "5": "String",
    "6": "Text",
    "7": "Date",
    "8": "DateTime",
    "9": "Time",
    "10": "File",
    1: "Boolean",
    2: "Long",
    3: "Double",
    4: "BigDecimal",
    5: "String",
    6: "Text",
    7: "Date",
    8: "DateTime",
    9: "Time",
    10: "File",
    "boolean": "Boolean",
    "bool": "Boolean",
    "long": "Long",
    "int": "Long",
    "integer": "Long",
    "double": "Double",
    "float": "Double",
    "bigdecimal": "BigDecimal",
    "decimal": "BigDecimal",
    "string": "String",
    "str": "String",
    "text": "Text",
    "date": "Date",
    "datetime": "DateTime",
    "time": "Time",
    "file": "File",
    "executor": "Executor",
    "list": "List",
}


SUPPORTED_FORMATS = {
    "Boolean",
    "Long",
    "Double",
    "BigDecimal",
    "String",
    "Text",
    "Date",
    "DateTime",
    "Time",
    "File",
    "Executor",
    "List",
}


LIST_ELEMENT_FORMATS = {
    "Boolean",
    "Long",
    "Double",
    "BigDecimal",
    "String",
    "Text",
    "Date",
    "DateTime",
    "Time",
    "File",
    "Executor",
}


def normalize_format(value):
    value = str(value).strip()

    if value.startswith("ru.runa.wfe.var.format.") and value.endswith("Format"):
        value = value.replace("ru.runa.wfe.var.format.", "")[:-6]

    alias_key = value.lower()
    value = FORMAT_ALIASES.get(value, FORMAT_ALIASES.get(alias_key, value))

    if value not in SUPPORTED_FORMATS:
        raise ValueError(f"Неизвестный тип переменной: {value}")

    return value


def get_item_value(item, key, default=""):
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def normalize_variables(variables_data):
    normalized = []

    if isinstance(variables_data, dict):
        source = []
        for name, item in variables_data.items():
            current = dict(item)
            current["name"] = name
            source.append(current)
    else:
        source = variables_data or []

    for item in source:
        name = str(get_item_value(item, "name", "")).strip()
        if not name:
            continue

        raw_format = get_item_value(item, "format", get_item_value(item, "type", "String"))
        variable_format = normalize_format(raw_format)
        default_value = str(get_item_value(item, "default", get_item_value(item, "default_value", ""))).strip()
        editor = str(get_item_value(item, "editor", "")).strip()
        element_format = str(get_item_value(item, "element_format", get_item_value(item, "elementFormat", ""))).strip()

        variable = {
            "name": name,
            "format": variable_format,
            "default": default_value,
            "editor": editor,
            "element_format": element_format,
        }

        if variable_format == "List":
            if not element_format:
                element_format = "String"
            element_format = normalize_format(element_format)
            if element_format not in LIST_ELEMENT_FORMATS:
                raise ValueError(f"Неподдерживаемый тип элемента списка: {element_format}")
            variable["element_format"] = element_format

        normalized.append(variable)

    return normalized


def variables(path, variables_data):
    root = ET.Element("variables")

    for item in normalize_variables(variables_data):
        name = item["name"]
        variable_format = item["format"]

        attributes = {
            "name": name,
            "scriptingName": name,
            "format": f"ru.runa.wfe.var.format.{variable_format}Format",
        }

        if item["default"]:
            attributes["defaultValue"] = item["default"]

        if variable_format == "Executor":
            attributes["swimlane"] = "true"
            if item["editor"] and item["editor"] != "0":
                attributes["editor"] = item["editor"]

        if variable_format == "List":
            attributes["elementFormat"] = f"ru.runa.wfe.var.format.{item['element_format']}Format"

        ET.SubElement(root, "variable", attributes)

    indent(root)
    xml_str = ET.tostring(root, encoding="unicode", method="xml")
    xml_str = xml_str.replace(" />", "/>")

    with open(path, "w", encoding="utf-8") as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
        file.write(xml_str)
        file.write("\n")
