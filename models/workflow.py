import os
import logging
from PIL import Image
from langgraph.graph import END, StateGraph, START
from utils.tools import http_toolkit
from langchain_openai import ChatOpenAI
from prompts.prompts import Prompts
from langgraph.prebuilt import create_react_agent
from models.blocks import PlanModel, ParserModel, EndpointModel, ActModel, PlanExecute


logger = logging.getLogger(__name__)

class Workflow:
    def __init__(self, prompts: Prompts, graph: bool):
        self.prompts = prompts
        self.llm_model = os.environ.get("LLM_MODEL", None)
        self.llm = ChatOpenAI(model=self.llm_model, temperature=0.0)
        self.planner = prompts.planner | self.llm.with_structured_output(PlanModel)
        self.api_selector = prompts.api_selector | self.llm.with_structured_output(EndpointModel)
        caller_tools = http_toolkit()
        self.agent_caller = create_react_agent(self.llm, caller_tools, state_modifier=prompts.caller)
        self.parser = prompts.parser | self.llm.with_structured_output(ParserModel)
        self.replanner = prompts.replanner | self.llm.with_structured_output(ActModel)
        
        self.state = StateGraph(PlanExecute)
        self.configure_workflow()    
        self.app = self.state.compile()
        # if graph:
        #     self.create_graph(self.app)
        # self.show_graph()

        

    def configure_workflow(self):
        self.state.add_node("Planner", self.plan_step)
        self.state.add_edge(START, "Planner")
        self.state.add_node("API Selector", self.api_selector_step)
        self.state.add_edge("Planner", "API Selector")
        self.state.add_node("Executor", self.caller_step)
        self.state.add_edge("API Selector", "Executor")
        self.state.add_node("Parser", self.parser_step)
        self.state.add_edge("Executor", "Parser")
        self.state.add_node("Replan", self.replan_step)
        self.state.add_edge("Parser", "Replan")
        self.state.add_conditional_edges("Replan", self.should_end,["API Selector", END],) # Next, we pass in the function that will determine which node is called next.

    async def plan_step(self, state: PlanExecute):
        logger.runlog(f"input: {state["input"]}")
        plan = await self.planner.ainvoke({"messages": [("user", state["input"])]})
        logger.runlog(f"the plan:\n{plan}\n")
        return {"plan": plan.steps, "task": 0, "past_steps": [], "original_plan": plan.steps}

    async def api_selector_step(self, state: PlanExecute):
        task = state["plan"][0]
        logger.runlog(f"The current step: {task}")
        endpoint = await self.api_selector.ainvoke({"messages": [("user",task)]})
        logger.runlog(f"API Selector stage\n-----------------\
                    API Request: {endpoint.endpoint}")
        return {"api": [endpoint.endpoint], "task": state["task"] + 1}

    async def caller_step(self, state: PlanExecute):
        task = state["plan"][0]
        formatted_task = {"http_request": state["api"][-1], "task": task, "past_steps": state["past_steps"]}
        logger.runlog(f"Caller Agent input: {formatted_task}")
        call = await self.agent_caller.ainvoke({"messages": [("user",str(formatted_task))]})
        logger.runlog(f"Caller Response:\n---------------\n\
        {call["messages"][-1].content}\n\n------------------------\n")
        return {"current_agent_answer": call["messages"][-1].content}

    async def parser_step(self, state: PlanExecute):
        task = state["plan"][0]
        input_for_parser = {"task": task, "api output": state["current_agent_answer"]}
        parse = await self.parser.ainvoke({"messages": [("user", str(input_for_parser))]})
        logger.runlog(f"Parser Response:\n---------------\n\
                     {parse.res}")
        logger.runlog(f"Past_steps: {task, state['past_steps']}")
        return {"current_agent_answer": dict(parse.res)[list(dict(parse.res).keys())[0]], "past_steps": [(task, str(parse.res))]}

    async def replan_step(self, state: PlanExecute):
        output = await self.replanner.ainvoke(state)
        output.more = bool(output.more)
        if not output.more:
            return {"response": output.response}
        else:
            logger.proto(f"Re-Plan stage:\nnew plan: {output.replan.steps}")
            return {"plan": output.replan.steps}
        
    def should_end(self, state: PlanExecute):
        if "response" in state and state["response"] or len(state["plan"]) == 0:
            try:
                logger.runlog(f"Final Response: {state["response"]}")
            except:
                pass
            return END
        else:
            return "API Selector"
        
    def create_graph(self, g: StateGraph.compile):
        a = g.get_graph(xray=True).draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(a)
        return a
    
    def show_graph(self):
        Image.open("graph.png").show()