import asyncio

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv, find_dotenv
from logging import getLogger, Logger
from langchain_core.prompts import ChatPromptTemplate
from models.blocks import *
from langgraph.graph import END, StateGraph, START
from utils.tools import *
from PIL import Image

def read_prompt(prompt_type: str):
    options = ["planner", "api_selector", "executer"]
    prompt_type = prompt_type.lower()
    if prompt_type not in options:
        raise ValueError(f"Invalid prompt type: {prompt_type}")
    with open(f"prompts/{prompt_type}_prompt.txt", "r") as f:
        return f.read()



_ = load_dotenv(find_dotenv())

planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""{read_prompt(prompt_type='planner')}""",
        ),
        ("placeholder", "{messages}"),
    ]
)


planner = planner_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0.5).with_structured_output(PlanModel)


async def plan_step(state: PlanExecute):
    plan = await planner.ainvoke({"messages": [("user", state["input"])]})
    return {"plan": plan.steps}


def should_end(state: PlanExecute):
    if "response" in state and state["response"]:
        return END
    else:
        # return "agent"
        return END
workflow = StateGraph(PlanExecute)
workflow.add_node("planner", plan_step)
workflow.add_edge(START, "planner")
workflow.add_conditional_edges(
    "planner",
    # Next, we pass in the function that will determine which node is called next.
    should_end,
    # ["planner", END],
)
app = workflow.compile()

a = app.get_graph(xray=True).draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(a)
Image.open("graph.png").show()

config = {"recursion_limit": 5}
inputs = {"input": input(">> ")}
async def main():
    async for event in app.astream(inputs, config=config):
        for k, v in event.items():
            if k != "__end__":
                print(v)

if __name__ == "__main__":
    asyncio.run(main())