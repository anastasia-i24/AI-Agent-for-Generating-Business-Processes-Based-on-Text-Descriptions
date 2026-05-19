import os
from typing import List, Optional

from langchain.schema.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class UserTask(BaseModel):
    name: str
    position: List[int] = Field(description="x, y coordinates in 1274x653 canvas")
    lanename: str
    ID: Optional[str] = Field(default="", description="Node id, for example ID3")


class ScriptTask(BaseModel):
    name: str
    position: List[int] = Field(description="x, y coordinates in 1274x653 canvas")
    ID: Optional[str] = Field(default="", description="Node id, for example ID4")


class Flow(BaseModel):
    ID: Optional[str] = Field(default="", description="Flow id, for example ID111112")
    TR: Optional[str] = Field(default="", description="Flow name, for example tr111112")
    source: str = Field(description="Starting node id, for example ID1 or ID3")
    target: str = Field(description="Ending node id, for example ID2 or ID4")


class Variable(BaseModel):
    name: str = Field(description="Technical variable name without spaces")
    format: str = Field(description="Boolean, Long, Double, BigDecimal, String, Text, Date, DateTime, Time, File, Executor or List")
    default: str = Field(default="", description="Default value. Empty string if there is no default value")
    element_format: str = Field(default="", description="Only for List: Boolean, Long, Double, BigDecimal, String, Text, Date, DateTime, Time, File or Executor")


class LaneData(BaseModel):
    name: str
    ID: Optional[str] = Field(default="", description="Lane id")
    group: str = Field(default="", description="Group/pool to which the lane is related")


class BusinessProcessStructure(BaseModel):
    usertasks: List[UserTask] = Field(description="Human tasks with role assignment")
    scripttasks: List[ScriptTask] = Field(description="Automatic script tasks")
    lanes: List[LaneData] = Field(description="Process roles/lanes with group initializers")
    flows: List[Flow] = Field(description="Sequence flows connecting process elements")
    process_name: str = Field(default="result", description="Name of the process")
    variables: List[Variable] = Field(description="Process variables with name, type and default value")
    initiator: str = Field(default="", description="Initiator role if applicable, else blank")


FORMAT_ALIASES = {
    "bool": "Boolean",
    "boolean": "Boolean",
    "int": "Long",
    "integer": "Long",
    "long": "Long",
    "float": "Double",
    "double": "Double",
    "decimal": "BigDecimal",
    "bigdecimal": "BigDecimal",
    "str": "String",
    "string": "String",
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


def normalize_format(value, fallback="String"):
    value = str(value or fallback).strip()
    value = FORMAT_ALIASES.get(value.lower(), value)
    if value not in SUPPORTED_FORMATS:
        return fallback
    return value


def clean_id(value):
    value = str(value or "").strip()
    if not value:
        return ""
    if value.startswith("ID"):
        return value
    return f"ID{value}"


def normalize_llm_result(generated_data, base_data):
    user_data = []
    script_data = []
    lane_data = []
    flows = []
    variables = {}
    events = base_data[3]
    id_map = {"ID1": "ID1", "ID2": "ID2"}

    current_id = 3

    for task in generated_data.usertasks:
        old_id = clean_id(task.ID) or f"ID{current_id}"
        id_map[old_id] = f"ID{current_id}"
        user_data.append([task.name, task.position, task.lanename, current_id])
        current_id += 1

    for task in generated_data.scripttasks:
        old_id = clean_id(task.ID) or f"ID{current_id}"
        id_map[old_id] = f"ID{current_id}"
        script_data.append([task.name, task.position, current_id])
        current_id += 1

    known_lanes = []
    for task in user_data:
        if task[2] not in known_lanes:
            known_lanes.append(task[2])

    for lane in generated_data.lanes:
        if lane.name not in known_lanes:
            known_lanes.append(lane.name)

    for index, lane_name in enumerate(known_lanes):
        lane_data.append([lane_name, current_id + index])

    group_by_lane = {lane.name: lane.group for lane in generated_data.lanes}
    for lane_name in known_lanes:
        variables[lane_name] = {
            "format": "Executor",
            "editor": group_by_lane.get(lane_name, "0") or "0",
        }

    flow_number = 111112
    for flow in generated_data.flows:
        source = id_map.get(clean_id(flow.source), clean_id(flow.source))
        target = id_map.get(clean_id(flow.target), clean_id(flow.target))
        flows.append([f"ID{flow_number}", f"tr{flow_number}", source, target])
        flow_number += 1

    if not any(flow[2] == "ID1" for flow in flows):
        first_node = None
        if user_data:
            first_node = f"ID{user_data[0][3]}"
        elif script_data:
            first_node = f"ID{script_data[0][2]}"
        if first_node:
            flows.insert(0, [f"ID{flow_number}", f"tr{flow_number}", "ID1", first_node])
            flow_number += 1

    if not any(flow[3] == "ID2" for flow in flows):
        last_node = None
        if script_data:
            last_node = f"ID{script_data[-1][2]}"
        elif user_data:
            last_node = f"ID{user_data[-1][3]}"
        if last_node:
            flows.append([f"ID{flow_number}", f"tr{flow_number}", last_node, "ID2"])

    for variable in generated_data.variables:
        variable_format = normalize_format(variable.format)
        item = {
            "format": variable_format,
            "default": variable.default or "",
        }
        if variable_format == "List":
            item["element_format"] = normalize_format(variable.element_format, fallback="String")
        variables[variable.name] = item

    process_name = generated_data.process_name or "result"
    initiator = generated_data.initiator or ""

    return [user_data, script_data, lane_data, events, flows, variables, process_name, initiator]


def read_multiline_text():
    print("Введите текстовое описание бизнес-процесса.")
    print("Для завершения ввода напишите END на отдельной строке.")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def llm(data):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Введите ключ OPENAI API")
        api_key = input().strip()

    process_text = read_multiline_text()

    with open("prompt.txt", "r", encoding="utf-8") as file:
        instructions = file.read()

    structured_llm = ChatOpenAI(
        model="gpt-4.1-mini",
        max_tokens=3000,
        api_key=api_key,
        temperature=0.2,
    ).with_structured_output(BusinessProcessStructure)

    prompt = [SystemMessage(content=instructions), HumanMessage(content=process_text)]
    generated_data = structured_llm.invoke(prompt)
    normalized_data = normalize_llm_result(generated_data, data)

    print("Структурированные данные бизнес-процесса получены от LLM")
    print(normalized_data)

    return normalized_data
