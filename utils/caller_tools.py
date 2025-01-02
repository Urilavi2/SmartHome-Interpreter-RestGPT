import json
import os
from utils.sawgger_interpreter import fix_json_error, ReducedOpenAPISpec
import requests
import re
from langchain_core.tools import tool
from typing import Annotated, Tuple
from langchain_community.utilities import TextRequestsWrapper
from logging import getLogger
from datetime import datetime
import logging

PROTOTYPE_level = 99
logging.addLevelName(PROTOTYPE_level, "PROTOTYPE")
logging.basicConfig(level=PROTOTYPE_level,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f"logs/{datetime.now().strftime('%H%M%S%d%m%Y')}.log"),
                    ])

def proto(self, message, *args, **kwargs):
    if self.isEnabledFor(PROTOTYPE_level):
        self._log(PROTOTYPE_level, message, args, **kwargs)

logging.Logger.proto = proto
logger = getLogger(__name__)

@tool
def get_response(action: Annotated[str, "HTTP method (GET, POST, PUT, DELETE)"], action_input: Annotated[str, "JSON string with request details"]):
    """
        Executes an HTTP request based on the action and input provided.

        Parameters:
            action: HTTP method (GET, POST, PUT, DELETE).
            action_input: JSON string containing request details (url, params, data, description).

        Returns:
            A tuple containing:
            - Response text from the request.
            - Request parameters if available.
            - Request body if available.
            - Description from the input data.
            - Query or instructions if available.
        """
    action_input = action_input.strip().strip('`')
    left_bracket = action_input.find('{')
    right_bracket = action_input.rfind('}')
    action_input = action_input[left_bracket:right_bracket + 1]
    try:
        data = json.loads(action_input)
    except json.JSONDecodeError as e:
        raise e
    access_token = os.environ["TMDB_ACCESS_TOKEN"]
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    requests_wrapper = TextRequestsWrapper(headers=headers)
    desc = data.get("description", "No description")
    query = data.get("output_instructions", None)

    params, request_body = None, None
    logger.proto(f"HTTP request to {action} {action_input["url"]}")
    if action == "GET":
        if 'params' in data:
            params = data.get("params")
            response = requests_wrapper.get(data.get("url"), params=params)
        else:
            response = requests_wrapper.get(data.get("url"))
    elif action == "POST":
        params = data.get("params")
        request_body = data.get("data")
        response =requests_wrapper.post(data["url"], params=params, data=request_body)
    elif action == "PUT":
        params = data.get("params")
        request_body = data.get("data")
        response = requests_wrapper.put(data["url"], params=params, data=request_body)
    elif action == "DELETE":
        params = data.get("params")
        request_body = data.get("data")
        response = requests_wrapper.delete(data["url"], params=params, json=request_body)
    else:
        raise NotImplementedError

    if isinstance(response, requests.models.Response):
        if response.status_code != 200:
            return response.text
        response_text = response.text
    elif isinstance(response, str):
        response_text = response
    else:
        raise NotImplementedError

    return response_text, params, request_body, desc, query

@tool
def get_matched_endpoint(api_spec: Annotated['ReducedOpenAPISpec', "API specification object"], plan: Annotated[str, "API plan to match endpoints"]):
    """
        Matches API endpoints from the specification with those described in the plan.

        Parameters:
            api_spec: API specification object containing available endpoints.
            plan: String describing API calls (methods and routes).

        Returns:
            A list of matched endpoints if found, otherwise None.
        """
    pattern = r"\b(GET|POST|PATCH|DELETE|PUT)\s+(/\S+)*"
    matches = re.findall(pattern, plan)
    plan_endpoints = [
        "{method} {route}".format(method=method, route=route.split("?")[0])
        for method, route in matches
    ]
    spec_endpoints = [item[0] for item in api_spec.endpoints]

    matched_endpoints = []

    for plan_endpoint in plan_endpoints:
        if plan_endpoint in spec_endpoints:
            matched_endpoints.append(plan_endpoint)
            continue
        for name in spec_endpoints:
            arg_list = re.findall(r"[{](.*?)[}]", name)
            pattern = name.format(**{arg: r"[^/]+" for arg in arg_list}) + '$'
            if re.match(pattern, plan_endpoint):
                matched_endpoints.append(name)
                break
    if len(matched_endpoints) == 0:
        return None
        # raise ValueError(f"Endpoint {plan_endpoint} not found in API spec.")

    return matched_endpoints

@tool
def get_action_and_input(
    llm_output: Annotated[str, "Raw output from the language model"]
) -> Tuple[str, str]:
    """
    Extracts the HTTP action and input to the HTTP request from the language model output.

    Parameters:
        llm_output: Raw string output from the language model, containing operation and input details.

    Returns:
        A tuple containing:
        - The action (Execution Result, GET, POST, DELETE, PUT).
        - The input or execution result string.

    """
    logger.proto(f"{get_action_and_input.__name__}")
    logger.proto(llm_output)

    regex = r"Operation:[\s]*(.*?)[\n]*Input:[\s]*(.*)"
    match = re.search(regex, llm_output, re.DOTALL)
    if not match:
        raise ValueError(f"Could not parse LLM output: `{llm_output}`")
    action = match.group(1).strip()
    action_input = match.group(2)
    if action not in ["GET", "POST", "DELETE", "PUT"]:
        raise NotImplementedError

    action_input = fix_json_error(action_input)
    logger.proto(action, action_input)
    return action, action_input
