from time import sleep
import sys
from langchain_community.agent_toolkits.openapi.toolkit import RequestsToolkit
from langchain_community.utilities.requests import TextRequestsWrapper
from PIL import Image
from langgraph.graph import StateGraph
import json
import traceback

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
            args.append(arg.strip("-"))
    return args, kwargs

def testConnection(url: str, count: int) -> bool:
    import requests
    print(f"Connection attempt {count}...\n{'-' * 30}")
    url_endpoint = url + "/"
    print(f"Tring to connect to the API on {url_endpoint}...")
    try:
        res = requests.get(url_endpoint, timeout=5)
        if res.status_code == 200:
            print("Connection successful")
            return True
    except:
        pass
    if count == 3:
        print(f"Connection failed after {count} tries. Exiting...")
        print("Please check your API URL and try again.")
        exit(4)
    print("Connection to the API failed. Trying again in 5 seconds...")
    sleep(5)

def create_graph(g: StateGraph.compile):
    a = g.get_graph(xray=True).draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(a)
    Image.open("graph.png").show()

def grading_system(input_json:dict) -> dict:
    try:
        indexs = list()
        index_counter = {}
        for query in input_json:
            index = int(query["index"])
            indexs.append(index)
        set_indexs = list(set(indexs))
        set_indexs.sort()
        for index in set_indexs:
            index_counter[index] = indexs.count(index)

        weight_sum = sum(index * index_counter[index] for index in set_indexs)
        weights = {index: round(100 * index / weight_sum) for index in set_indexs}
        return weights
    except Exception as e:
        print(f"Error reading input file: {e}")
        return {}