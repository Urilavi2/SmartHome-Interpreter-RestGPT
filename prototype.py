import asyncio
import json
from copy import deepcopy
from datetime import datetime
import os
from time import sleep
from plistlib import dumps
from utils.tools import http_toolkit
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv, find_dotenv
from logging import getLogger, Logger
from langchain_core.prompts import ChatPromptTemplate
from prompts.prompt_reader import Prompts
from models.blocks import *
from utils.sawgger_interpreter import *
from langgraph.graph import END, StateGraph, START
from utils.caller_tools import get_response, get_action_and_input, get_matched_endpoint
from PIL import Image
import logging

PROTOTYPE_level = 99
logging.addLevelName(PROTOTYPE_level, "PROTOTYPE")
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f"logs/{datetime.now().strftime('%H%M%S%d%m%Y')}.log"),
                    ])

def testConnection(url: str, count: int) -> bool:
    import requests
    print(f"Connection attempt {count}...\n{'-' * 30}")
    print(f"Tring to connect to the API on {url}...")
    try:
        res = requests.get(url, timeout=5)
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

def proto(self, message, *args, **kwargs):
    if self.isEnabledFor(PROTOTYPE_level):
        self._log(PROTOTYPE_level, message, args, **kwargs)

logging.Logger.proto = proto
logger = getLogger(__name__)

def create_graph(g: StateGraph.compile):
    a = g.get_graph(xray=True).draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(a)
    Image.open("graph.png").show()

async def prototype(*args, **kwargs):
    entity = kwargs.get("entity",None)
    if entity is None:
        print("No entity specified")
        exit(1)

    if entity.lower() not in ["planner", "api", "executor", "full"]:
        print("Entity not valid")
        exit(2)
    entity = Entity[entity]

    _ = load_dotenv(find_dotenv())
    llm_model = os.environ.get("LLM_MODEL", None)
    prompts = Prompts()

    for count in range(1, 4):
        if testConnection(prompts.api_url, count):
            break

    inputs = {"input": input(">> ")}

    caller_tools = http_toolkit()

    llm = ChatOpenAI(model=llm_model, temperature=0.0)
    planner = prompts.planner | llm.with_structured_output(PlanModel)
    api_selector = prompts.api_selector | llm.with_structured_output(EndpointModel)
    agent_caller = create_react_agent(llm, caller_tools, state_modifier=prompts.caller)
    parser = prompts.parser | llm.with_structured_output(ParserModel)
    replanner = prompts.replanner | llm.with_structured_output(ActModel)


    async def plan_step(state: PlanExecute):
        logger.proto(f"input: {state["input"]}")
        plan = await planner.ainvoke({"messages": [("user", state["input"])]})
        logger.proto(f"the plan:\n{plan}\n")
        return {"plan": plan.steps, "task": 0, "past_steps": [], "original_plan": plan.steps}

    async def api_selector_step(state: PlanExecute):
        task = state["plan"][0]
        if entity.value == 2:
            state["plan"] = state["plan"][1:]
        logger.proto(f"The current step: {task}")
        endpoint = await api_selector.ainvoke({"messages": [("user",task)]})
        logger.proto(f"API Selector stage\n-----------------\
                    API Request: {endpoint.endpoint}")
        if entity.value == 2:
            return {"api": [endpoint.endpoint], "task": state["task"] + 1, "plan": state["plan"]}
        return {"api": [endpoint.endpoint], "task": state["task"] + 1}

    async def caller_step(state: PlanExecute):
        task = state["plan"][0]
        formatted_task = {"http_request": state["api"][-1], "task": task, "past_steps": state["past_steps"]}
        logger.proto(f"Caller Agent input: {formatted_task}")
        call = await agent_caller.ainvoke({"messages": [("user",str(formatted_task))]})
        logger.proto(f"Caller Response:\n---------------\n\
        {call["messages"][-1].content}\n\n------------------------\n")
        return {"current_agent_answer": call["messages"][-1].content}

    async def parser_step(state: PlanExecute):
        task = state["plan"][0]
        input_for_parser = {"task": task, "api output": state["current_agent_answer"]}
        parse = await parser.ainvoke({"messages": [("user", str(input_for_parser))]})
        logger.proto(f"Parser Response:\n---------------\n\
                     {parse}")
        logger.proto(f"Past_steps: {task, state['past_steps']}")
        if entity.value == 3:
            return {"current_agent_answer": "", "past_steps": [(task, str(parse.res))], "plan": state["plan"][1:]}
        return {"current_agent_answer": "", "past_steps": [(task, str(parse.res))]}

    async def replan_step(state: PlanExecute):
        output = await replanner.ainvoke(state)
        output.more = bool(output.more)
        if not output.more:
            return {"response": output.response}
        else:
            logger.proto(f"Re-Plan stage:\nnew plan: {output.replan.steps}")
            return {"plan": output.replan.steps}

    def should_end(state: PlanExecute):
        if "response" in state and state["response"] or len(state["plan"]) == 0:
            try:
                logger.proto(f"Final Response: {state["response"]}")
            except:
                pass
            return END
        else:
            # return "agent"
            return "API Selector"

    workflow = StateGraph(PlanExecute)
    workflow.add_node("Planner", plan_step)
    workflow.add_edge(START, "Planner")
    if entity.value > 1:
        workflow.add_node("API Selector", api_selector_step)
        workflow.add_edge("Planner", "API Selector")
        if entity.value > 2:
            workflow.add_node("Executor", caller_step)
            workflow.add_edge("API Selector", "Executor")
            workflow.add_node("Parser", parser_step)
            workflow.add_edge("Executor", "Parser")
            if entity.value > 3:
                workflow.add_node("Replan", replan_step)
                workflow.add_edge("Parser", "Replan")
                workflow.add_conditional_edges("Replan", should_end,["API Selector", END],)# Next, we pass in the function that will determine which node is called next.
            else:  # PLANNER --> API --> CALLER
                workflow.add_conditional_edges("Parser", should_end, ["API Selector",
                                                                      END], )  # Next, we pass in the function that will determine which node is called next.
        else:  # PLANNER --> API
            workflow.add_conditional_edges("API Selector", should_end, ["API Selector",
                                                                  END], )  # Next, we pass in the function that will determine which node is called next.

    app = workflow.compile()
    # create_graph(app)
    config = {"recursion_limit": 20}

    async for event in app.astream(inputs, config=config):
        for k, v in event.items():
                if k != "__end__":
                    print(json.dumps(v, indent=4))


