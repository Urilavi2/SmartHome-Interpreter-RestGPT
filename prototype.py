import asyncio
import json
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv, find_dotenv
from logging import getLogger, Logger
from langchain_core.prompts import ChatPromptTemplate
from models.blocks import *
from utils.sawgger_interpreter import *
from langgraph.graph import END, StateGraph, START
from utils.tools import *
from PIL import Image

def read_prompt(prompt_type: str):
    options = ["planner", "api_selector", "executer", "replanner"]
    prompt_type = prompt_type.lower()
    if prompt_type not in options:
        raise ValueError(f"Invalid prompt type: {prompt_type}")
    with open(f"prompts/{prompt_type}_prompt.txt", "r") as f:
        return f.read()

def format_endpoints(api_ref: ReducedOpenAPISpec) -> str:
    api_name_desc = [f"{endpoint[0]} {endpoint[1].split('.')[0] if endpoint[1] is not None else ''}" for endpoint in
                     api_ref.endpoints]
    api_name_desc = '\n'.join(api_name_desc)
    api_name_desc = api_name_desc.replace('{', '{{').replace('}', '}}')
    return api_name_desc

def fetch_api_ref(path: str) -> ReducedOpenAPISpec:
    with open(path) as f:
        raw_tmdb_api_spec = json.load(f)
    api_spec = reduce_openapi_spec(raw_tmdb_api_spec, only_required=False)
    return api_spec

def create_graph(g: StateGraph.compile):
    a = g.get_graph(xray=True).draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(a)
    Image.open("graph.png").show()

_ = load_dotenv(find_dotenv())

api_ref = fetch_api_ref("swagger/tmdb_oas.json")
endpoints_desc = format_endpoints(api_ref)

planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""{read_prompt(prompt_type='planner')}""",
        ),
        ("placeholder", "{messages}"),
    ]
)
api_selector_prompt = ChatPromptTemplate.from_template(read_prompt(prompt_type="api_selector"))
api_selector_prompt = ChatPromptTemplate.format_prompt(api_selector_prompt, endpoints=endpoints_desc)
api_selector_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         api_selector_prompt.messages[0].content
         ),
        ("placeholder", "{messages}"),
    ]
)

# replanner_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             f"""{read_prompt(prompt_type='replanner')}""",
#         ),
#         ("placeholder", "{messages}"),
#     ]
# )




planner = planner_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0.0).with_structured_output(PlanModel)
api_selector = api_selector_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(EndpointModel)
# replanner = replanner_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0.0).with_structured_output(ActModel)


async def plan_step(state: PlanExecute):
    plan = await planner.ainvoke({"messages": [("user", state["input"])]})
    return {"plan": plan.steps, "task": 0}

async def api_selector_step(state: PlanExecute):
    task = state["plan"][state["task"]]
    print(f"The current step: {task}")
    endpoint = await api_selector.ainvoke({"messages": [("user",task)]})
    return {"api": [endpoint.endpoint], "task": state["task"] + 1, "past_steps": [(task, "The Response")]}

# async def replan_step(state: PlanExecute):
#     output = await replanner.ainvoke(state)
#     if isinstance(output.action, ResponseModel):
#         return {"response": output.action.response}
#     else:
#         return {"plan": output.action.steps}


def should_end(state: PlanExecute):
    if ("response" in state and state["response"]) or state["task"] >= len(state["plan"]) :
        return END
    else:
        # return "agent"
        return "API Selector"

workflow = StateGraph(PlanExecute)
workflow.add_node("Planner", plan_step)
workflow.add_node("API Selector", api_selector_step)
# workflow.add_node("replan", replan_step)
workflow.add_edge(START, "Planner")
workflow.add_edge("Planner", "API Selector")
# workflow.add_edge("API Selector", "replan")
workflow.add_conditional_edges("API Selector", should_end,["API Selector", END],)# Next, we pass in the function that will determine which node is called next.

app = workflow.compile()
create_graph(app)
config = {"recursion_limit": 10}
inputs = {"input": input(">> ")}
async def main():
    async for event in app.astream(inputs, config=config):
        for k, v in event.items():
            if k != "__end__":
                print(v)

if __name__ == "__main__":
    asyncio.run(main())