from langchain_community.agent_toolkits.openapi.toolkit import RequestsToolkit
from langchain_community.utilities.requests import TextRequestsWrapper
from langchain_core.tools import tool

ALLOW_DANGEROUS_REQUEST = True

def http_toolkit():
    toolkit = RequestsToolkit(
        requests_wrapper=TextRequestsWrapper(headers={}),
        allow_dangerous_requests=ALLOW_DANGEROUS_REQUEST,
    )

    tools = toolkit.get_tools()
    return tools

@tool
def python_code_execution(code: str) -> dict:
    """Execute python code to extract a specific argument from JSON"""
    exec_scope = {}
    if code:
        try:
            exec(code, exec_scope)
            return exec_scope
        except Exception as e:
            print("ERROR!", e)
            exit(2)