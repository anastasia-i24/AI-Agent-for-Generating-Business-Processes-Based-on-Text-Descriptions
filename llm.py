import os
import json
from generate_ids import generate_ids_exept_flows, generate_flow_ids
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI  


class BPMN(BaseModel):
    process_name: Optional[str] = Field(
        default=None,
        description='Название бизнес-процесса'
    )
    user_tasks: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description='Действия, которые выполняются участниками бизнес-процесса.'
    )
    script_tasks: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description='Действия, которые выполняются автоматически, без вмешательства участников бизнес-процесса.'
    )
    lanes: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description='Участники бизнес-процесса.'
    )
    events: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description='''События, которые происходят в течении бизнес-процесса,
        обязательно включают в себя стартовое и итоговые события.'''
    )
    variables: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description='Переменные бизнес-процесса: все объекты, упоминающиеся в описании бизнес-процесса'
    )
    gateways: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description='''Место, где бизнес-процесс разветвляется (разные варианты)
        или сходится (разные результаты в один).'''
    )


class Flows(BaseModel):
    flows: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description='Переходы между элементами-узлами бизнес-процесса.'
    )


class Groovy(BaseModel):
    groovy: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description='Шлюзы с добавлением условия разветвления.'
    )


def llm(text, temp): 
    llm = ChatOpenAI(
        model="gpt-4.1-nano",
        api_key=os.getenv('API_KEY'),
        temperature=temp,
    )

    with open(f'dataset.jsonl', 'r', encoding='utf-8') as f:
        dataset = f.readlines()

    context = f"INPUT:\n {text}\nПримеры:\n{''.join(dataset)}"    

    #1 этап
    prompt_1 = get_prompt(1, context)
    first_stage = llm.with_structured_output(BPMN)
    bpmn = first_stage.invoke(prompt_1)
    elements_without_flows = bpmn.model_dump()

    #2 этап
    data, ID = generate_ids_exept_flows(elements_without_flows)
    context += '\nПолученные данные:\n' + json.dumps(data, ensure_ascii=False, indent=2)
    print(data)
    prompt_2 = get_prompt(2, context)
    second_stage = llm.with_structured_output(Flows)
    flows = second_stage.invoke(prompt_2)
    data['flows'] = generate_flow_ids(ID, flows.model_dump()['flows'])

    print(data['flows'])

    #3 этап
    context += '\nПолученные переходы:\n' + json.dumps(data['flows'], ensure_ascii=False, indent=2)
    prompt_3 = get_prompt(3, context)
    third_stage = llm.with_structured_output(Groovy)
    groovy = third_stage.invoke(prompt_3)
    data['gateways'] = groovy.model_dump()['gateways']

    return data


def get_prompt(stage, context):
    with open(f'prompts/prompt_{stage}.txt', 'r', encoding='utf-8') as f:
        prompt = f.read()
    return context + '\n' + prompt 