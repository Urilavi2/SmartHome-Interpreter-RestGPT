import json
import os
import sys
from tabnanny import verbose

from langchain_community.agent_toolkits.openapi.toolkit import RequestsToolkit
from langchain_community.utilities.requests import TextRequestsWrapper
from langchain_core.tools import tool
import requests

ALLOW_DANGEROUS_REQUEST = True


def http_toolkit():
    toolkit = RequestsToolkit(
        requests_wrapper=TextRequestsWrapper(),
        allow_dangerous_requests=ALLOW_DANGEROUS_REQUEST,
    )
    tools = toolkit.get_tools()
    return tools


def split_args():
    arguments = sys.argv[1:]
    args = []
    kwargs = {}
    for arg in arguments:
        if "=" in arg:  # Keyword argument
            key, value = arg.split("=", 1)
            kwargs[key] = value
        else:  # Positional argument
            args.append(arg)
    return args, kwargs