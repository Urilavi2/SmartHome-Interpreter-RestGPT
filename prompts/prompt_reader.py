import os
from langchain_core.prompts import ChatPromptTemplate
import json
from utils.sawgger_interpreter import reduce_openapi_spec, ReducedOpenAPISpec


def _format_endpoints(api_ref: ReducedOpenAPISpec) -> str:
    api_name_desc = [f"{endpoint[0]} {endpoint[1].split('.')[0] if endpoint[1] is not None else ''}" for endpoint in
                     api_ref.endpoints]
    api_name_desc = '\n'.join(api_name_desc)
    api_name_desc = api_name_desc.replace('{', '{{').replace('}', '}}')
    return api_name_desc

def _fetch_api_ref(path: str) -> ReducedOpenAPISpec:
    with open(path) as f:
        raw_tmdb_api_spec = json.load(f)
    api_spec = reduce_openapi_spec(raw_tmdb_api_spec, only_required=False)
    return api_spec

def _read_prompt(prompt_type: str) -> str:
    options = ["planner", "api_selector", "caller", "replanner", "parser"]
    prompt_type = prompt_type.lower()
    if prompt_type not in options:
        raise ValueError(f"Invalid prompt type: {prompt_type}")
    with open(f"prompts/{prompt_type}_prompt.txt", "r") as f:
        return f.read()

def _create_api_reference(swagger_path:str) -> ReducedOpenAPISpec:
    if swagger_path is None:
        raise ValueError("SWAGGER_PATH is not set. Please set the SWAGGER_PATH environment variable.")
    if not os.path.exists(swagger_path):
        raise FileNotFoundError(f"Swagger file not found at {swagger_path}.")
    if not swagger_path.endswith('.json'):
        raise ValueError(f"Invalid Swagger file format: {swagger_path}. Expected a .json file.")
    return _fetch_api_ref(swagger_path)


def _create_endpoint_desc(api_ref:ReducedOpenAPISpec) -> str:
    return _format_endpoints(api_ref)

def _create_planner_ChatPromptTemplate():
      return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""{_read_prompt(prompt_type='planner')}""",
            ),
            ("placeholder", "{messages}"),
        ]
    )

def _create_api_selector_ChatPromptTemplate(endpoints: str) -> ChatPromptTemplate:
    api_selector_prompt = ChatPromptTemplate.from_template(_read_prompt(prompt_type="api_selector"))
    api_selector_prompt = ChatPromptTemplate.format_prompt(api_selector_prompt, endpoints=endpoints)
    api_selector_prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             api_selector_prompt.messages[0].content
             ),
            ("placeholder", "{messages}"),
        ]
    )
    return api_selector_prompt

def _create_caller_ChatPromptTemplate(api_docs='', task='', api_url='', background=''):
    caller_prompt = ChatPromptTemplate.from_template(_read_prompt(prompt_type="caller"))
    caller_prompt = ChatPromptTemplate.format_prompt(caller_prompt,
                                                     api_docs=api_docs,
                                                     task=task,
                                                     api_url=api_url,
                                                     background=background,
                                                     )
    caller_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                caller_prompt.messages[0].content,
            ),
            ("placeholder", "{messages}"),
        ]
    )
    return caller_prompt

def _create_parser_ChatPromptTemplate():
    parser_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""{_read_prompt(prompt_type='parser')}""",
            ),
            ("placeholder", "{messages}"),
        ]
    )
    return parser_prompt

def _create_replanner_ChatPromptTemplate():

    replanner_prompt = ChatPromptTemplate.from_template(f"""{_read_prompt(prompt_type='replanner')}""")
    return replanner_prompt

class Prompts:
    def __init__(self):
        self.api_ref = _create_api_reference(swagger_path=os.environ.get('SWAGGER_PATH', None))
        self.endpoint_desc = _create_endpoint_desc(api_ref=self.api_ref)
        self.planner = _create_planner_ChatPromptTemplate()
        self.api_selector = _create_api_selector_ChatPromptTemplate(endpoints=self.endpoint_desc)
        self.api_url = self.api_ref.servers[0]['url']
        self.caller = _create_caller_ChatPromptTemplate(api_docs='', task='', api_url=self.api_url, background='')
        self.parser = _create_parser_ChatPromptTemplate()
        self.replanner = _create_replanner_ChatPromptTemplate()

    def change_caller_prompt(self, api_docs=None, task=None, api_url=None, background=None):
        if api_url is None:
            api_url = self.api_ref.servers[0]['url']
        if task is None:
            task = ''
        if background is None:
            background = ''
        if api_docs is None:
            api_docs = ''
        self.caller = _create_caller_ChatPromptTemplate(api_docs=api_docs, task=task, api_url=api_url, background=background)