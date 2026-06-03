import os
import json
from llm.generate_ids import generate_ids_exept_flows, generate_flow_ids
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI


class Event(BaseModel):
    name: str = Field(description='Название события')
    type: str = Field(description='Тип события, start или end')
    lane: str = Field(description='инициализатор события типа \"start\" или пустая строка для события типа \"end\"')

class Lane(BaseModel):
    name: str = Field(description='Название роли - участника бизнес-процесса')

class UserTask(BaseModel):
    name: str = Field(description='Название пользовательского действия')
    lane: str = Field(description='Участник бизнес-процесса, который выполняет действие. Должен быть только из списка lanes')

class ScriptTask(BaseModel):
    name: str = Field(description='Название скрипта')

class Variable(BaseModel):
    name: str = Field(description='Название переменной бизнес-процесса')
    format: str = Field(description='Формат переменной, определяется по смыслу: даты → Date, файлы → File, текст → Text, числа → Long, да/нет → Boolean, остальное → String.')

class Gateway(BaseModel):
    name: str = Field(description='Название шлюза')
    type: str = Field(description='Тип шлюза: exclusive или parallel. Если в тексте есть условия (\"если\", \"иначе\", \"в случае\"), тип должен быть \"exclusive\". Если есть параллельные ветки (\"одновременно\", \"параллельно\"), тип \"parallel\".')
    conditions: Optional[str] = Field(default_factory=str, description="Поле \"conditions\" нужно только для exclusive шлюзов. Для них добавь Groovy-код вида: if (условие) return 'название_перехода_1'; return 'название_перехода_2';")

class BPMN(BaseModel):
    process_name: str = Field(description='Название бизнес-процесса')
    events: List[Event] = Field(description='Список стартового и конечных событий. СТАРТОВОЕ СОБЫТИЕ: - начало процесса; - не действие. КОНЕЧНОЕ СОБЫТИЕ: - завершение процесса; - не действие. По умолчанию процесс содержит: - 1 start; - 1..N end. Если сомневаешься — не создавай событие.')
    lanes: Optional[List[Lane]] = Field(default_factory=list, description='Список ролей - активных одушевленных участников бизнес-процесса.')
    user_tasks: Optional[List[UserTask]] = Field(default_factory=list, description='Список пользовательских действий - действий, которые выполняются участниками бизнес-процесса из списка lanes')
    script_tasks: Optional[List[ScriptTask]] = Field(default_factory=list, description='Список скриптов - автоматических задач, выполняющихся без участия участников бизнес-процесса')
    variables: Optional[List[Variable]] = Field(default_factory=list, description='Список переменных - неодушевленных объектов, которые фигурируют в бизнес-процессе')
    gateways: Optional[List[Gateway]] = Field(default_factory=list, description='Список шлюзов - мест, где бизнес-процесс разветвляется (разные варианты) или сходится (разные результаты в один)')


class Flow(BaseModel):
    name: str = Field(description='Название перехода')
    sourceRef: int = Field(description='id элемента, из которого исходит переход')
    targetRef: int = Field(description='id элемента, в которорый входит переход')

class Flows(BaseModel):
    flows: List[Flow] = Field(description='Переходы, соединяющие все элементы бизнес-процесса. Каждый узел, кроме start, должен иметь входящий переход. Каждый узел, кроме end, должен иметь исходящий переход. Для gateways должнл по одному переходу на каждую ветку (входящих или исходящих).')


def llm(text, temp): 
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=os.getenv('OPENAI_API_KEY'),
        temperature=temp,
    )

    with open(f'llm/dataset.jsonl', 'r', encoding='utf-8') as f:
        dataset = f.readlines()

    with open('llm/prompt.json', 'r') as file:
        prompts = json.load(file)

    # все элементы, кроме переходов
    structured_llm = llm.with_structured_output(BPMN)
    model = structured_llm.invoke(prompts['BPMN'].format(text=text, examples=dataset))
    data = model.model_dump()

    # переходы
    data, ID = generate_ids_exept_flows(data)
    structured_llm = llm.with_structured_output(Flows)
    model = structured_llm.invoke(prompts['Flows'].format(
        text=text,
        examples=dataset,
        events=json.dumps(data['events']),
        user_tasks=json.dumps(data['user_tasks']),
        script_tasks=json.dumps(data['script_tasks']),
        gateways=json.dumps(data['gateways'])
    ))
    data['flows'] = generate_flow_ids(ID, model.model_dump()['flows'])

    return data