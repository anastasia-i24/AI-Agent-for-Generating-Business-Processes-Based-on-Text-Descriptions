from pydantic import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI
from langchain.schema.messages import SystemMessage, HumanMessage, AIMessage

# events = [["startEvent", [48, 48], initiator, 1], ["endEvent", [48, 48], '', 2]]

# usertask - [name, [x,y], lanename, ID]
# scripttask - [name, [x,y], ID]
# events - [name, [x,y], ID]
# flows - [ID, TR, source, target]


# [[['UserTaskName1', [200, 48], 'UserTaskLaneName1', 3]],
#  [['ScriptTaskName1', [400, 48], 4]],
#  [['UserTaskLaneName1', 5]],
#  [['startEvent', [48, 48], '', 1], ['endEvent', [48, 48], '', 2]],
#  [['ID111112', 'tr111112', 'ID1', 'ID3'], ['ID111113', 'tr111113', 'ID3', 'ID4'], ['ID111114', 'tr111114', 'ID4', 'ID2']]]

class UserTask(BaseModel):
    name: str
    position: List[int] = Field(description = "x, y coordinates of the object in the space of 1274x653, object size is around 150x150")
    lanename: str
    ID: str = Field(description = "example ID3")


class ScriptTask(BaseModel):
    name: str
    position: List[int] = Field(description = "x, y coordinates of the object in the space of 1274x653, object size is around 150x150")
    ID: str = Field(description = "example ID3")

# class Event(BaseModel):
#     name: str
#     position: Point = Field(alias="[x,y]")
#     ID: str

class Flow(BaseModel):
    ID: str = Field(description = "starts from 111112, example ID111112")
    TR: str = Field(description = "starts from 111112, example tr111112, same number as ID of the same flow")
    source: str = Field(description = "Starting node identifier, follows node ID format like 'ID1', 'ID2', etc.")
    target: str = Field(description = "Ending node identifier, follows node ID format like 'ID1', 'ID2', etc.")

class Variable(BaseModel):
    name: str
    type: int = Field(description=(f"1: 'Boolean', 2: 'Long',"
                                   f" 3: 'Double', 4: 'BigDecimal',"
                                   f" 5: 'String', 6: 'Text',"
                                   f" 7: 'Date', 8: 'DateTime',"
                                   f" 9: 'Time', 10: 'File'"))

class LaneData(BaseModel):
    name: str
    ID: str = Field(description= "example: ID3")
    group: str = Field(description = "group/pool to which the lane is related")

# data = [user_data, script_data, lanes, events, flows, process_name, variables]

class BusinessProcessStructure(BaseModel):
    usertasks: List[UserTask] = Field(description = "Tasks that require human interaction and role assignment")
    scripttasks: List[ScriptTask] = Field(description = "Automated script tasks that execute code or logic")
    lanes: List[LaneData] = Field(description="Lane information containing roles, role groups/pools")
    # events: List[Event] = Field(description = "smth")
    flows: List[Flow] = Field(description = "Sequence flows connecting elements with source and target in a graph")
    process_name: str = Field(description = "Name of the process")
    variables: List[Variable] = Field(description="Process variables with name, type")
    initiator: str = Field(description="initiator of the process if applicable, else kept blank")


def llm(data):
    # print(f"выберите модель - chatgpt-4.1-mini, deepseek")
    # model = str(input())
    print(f"введите ключ OPENAI API")
    # OPENAI_API_KEY = input()

    print(f"Введите описание бизнес-процесса, включающее следующие элементы:"
          f" пользовательские задачи с указанием исполнителей (user tasks),"
          f" автоматические скриптовые задачи (script tasks),"
          f"данные по дорожкам и пулам (lane data с распределением ролей и групп задач),"
          f" потоки управления с условиями перехода c ноды на ноду (sequence flows),"
          f"название процесса,"
          f"роли участников (roles),"
          f" а также переменные процесса с их типами и значениями (process variables).")
    text = str(input())
    with open("prompt.txt", "r") as f:
        instructions = f.read()

    with open("promptFlow.txt", "r") as r:
        instructionsFlow = r.read()



    structured_llm = ChatOpenAI(model="gpt-4.1-mini", max_tokens=1000, api_key=OPENAI_API_KEY, temperature=0.5).with_structured_output(BusinessProcessStructure)
    prompt = [SystemMessage(content=instructions), HumanMessage(content=text)]

    generated_data = structured_llm.invoke(prompt)
    promptFlow = [SystemMessage(content=instructions), generated_data,HumanMessage(content=text)]
    flow_data = structured_llm.invoke(promptFlow)


    merged_data = generated_data.usertasks + generated_data.scripttasks + generated_data.lanes + [data[3]] + generated_data.flows + [generated_data.process_name] + generated_data.variables + [generated_data.initiator]

    print(merged_data)

    return merged_data