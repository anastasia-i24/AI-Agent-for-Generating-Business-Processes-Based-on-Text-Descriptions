import os
from typing import List, Literal, Optional, Dict
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI  
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.tools import tool
from langchain.agents import create_agent


class BPMN(BaseModel):
    process_name: Optional[str] = Field(
        default=None,
        description='Название бизнес-процесса'
    )
    user_tasks: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description='Действия, которые выполняются участниками бизнес процесса.'
    )
    script_tasks: Optional[List[str]] = Field(
        default=0,
        description=''
    )
    lanes: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description='Участники бизнес процесса.'
    )
    events: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description='''События, которые происходят в течении бизнес процесса,
        обязательно включают в себя стартовое и итоговое события.'''
    )
    variables: Optional[List[str]] = Field(
        default=None,
        description='Переменные бизнес-процесса.'
    )
    sequence_flows: Optional[Dict[str, Dict[str, str, str]]] = Field(
        default=None,
        description='Переходы между узлами бизнес-процесса'
    )
    gateways: Optional[Dict[str, Dict[str, str, str]]] = Field(
        default=None,
        description='''Место, где бизнес процесс разветвляется (разные варианты)
        или сходится (разные результаты в один).'''
    )


def get_openai_api_key() -> str:
    load_dotenv()
    return os.getenv('DEEPSEEK_API_KEY')

def extract_bpmn():
    llm = ChatOpenAI(
        model="gpt-4.1-nano",
        api_key=get_openai_api_key,
        temperature=0.0,
    )

    structured_llm = llm.with_structured_output(BPMN)
    with open('prompt.txt', 'r', encoding='utf-8') as f:
        prompt = f.read()
    task = structured_llm.invoke(prompt)
    return task.model_dump()
    
