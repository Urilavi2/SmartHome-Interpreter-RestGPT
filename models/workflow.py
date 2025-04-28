import os
import logging
from PIL import Image
from langgraph.graph import END, StateGraph, START
from utils.tools import http_toolkit
from langchain_openai import ChatOpenAI
from prompts.prompts import Prompts
from langgraph.prebuilt import create_react_agent
from models.blocks import PlanModel, ParserModel, EndpointModel, ActModel, PlanExecute, DecisionModel


logger = logging.getLogger(__name__)

class Workflow:
    def __init__(self, prompts: Prompts):
        self.prompts = prompts
        self.llm_model = os.environ.get("LLM_MODEL", None)
        self.llm = ChatOpenAI(model=self.llm_model, temperature=0.0)
        self.planner = prompts.planner | self.llm.with_structured_output(PlanModel)
        self.api_selector = prompts.api_selector | self.llm.with_structured_output(EndpointModel)
        caller_tools = http_toolkit()
        self.agent_caller = create_react_agent(self.llm, caller_tools, state_modifier=prompts.caller)
        self.parser = prompts.parser | self.llm.with_structured_output(ParserModel)

        self.decider = prompts.decider | self.llm.with_structured_output(DecisionModel)

        self.replanner = prompts.replanner | self.llm.with_structured_output(PlanModel)
        
        self.state = StateGraph(PlanExecute)
        self.configure_workflow()    
        self.app = self.state.compile()


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
        self.state.add_edge("Parser", "Decider")
        self.state.add_node("Decider", self.decider_step)
        self.state.add_conditional_edges("Decider", self.should_end, ["Replan", END])
        self.state.add_edge("Replan", "API Selector")

    async def plan_step(self, state: PlanExecute):
        try:
            logger.runlog(f"input: {state["input"]}")
            plan = await self.planner.ainvoke({"messages": [("user", state["input"])]})
            logger.runlog(f"the plan:\
                          {plan}\n")
            return {"plan": plan.steps, "task": 0, "past_steps": [], "original_plan": plan.steps}
        except Exception as e:
            logger.runlog(f"Error in planning step: {e}")
            print(f"Error in planning step: {e}")
            print(f"Could not plan the task. Please check the input and try again.")
            print("Exiting the program.")
            exit(1)

    async def api_selector_step(self, state: PlanExecute):
        tryCount = 0
        while True:
            try:
                task = state["plan"][0]
                logger.runlog(f"The current step: {task}")
                endpoint = await self.api_selector.ainvoke({"messages": [("user",task)]})
                logger.runlog(f"API Selector stage\n-----------------\
                            API Request: {endpoint.endpoint}")
                return {"api": [endpoint.endpoint], "task": state["task"] + 1}
            except Exception as e:
                tryCount += 1
                logger.runlog(f"Error in API Selector step: {e}")
                print(f"Error in API Selector step: {e}")
                print(f"Could not select the API. Trying again...")
                if tryCount == 3:
                    print(f"API Selector failed after {tryCount} tries. Exiting...")
                    print("Please check your API URL and internet connection and try again.")
                    exit(2)
            if tryCount < 3:
                continue
        
    async def caller_step(self, state: PlanExecute):
        tryCount = 0
        while True:
            try:
                task = state["plan"][0]
                http_request = state["api"][-1]
                if http_request is None:
                    logger.runlog(f"API Caller stage\n-----------------\n       NO API FOUND!\n")
                
                formatted_task = {"http_request": http_request, "task": task, "past_steps": state["past_steps"]}
                logger.runlog(f"Caller Agent input: {formatted_task}")
                call = await self.agent_caller.ainvoke({"messages": [("user",str(formatted_task))]})
                logger.runlog(f"Caller Response:\n---------------\n\
                {call["messages"][-1].content}\n\n------------------------\n")
                return {"current_agent_answer": call["messages"][-1].content}
            except Exception as e:
                tryCount += 1
                logger.runlog(f"Error in API Caller step: {e}")
                print(f"Error in API Caller step: {e}")
                print(f"Could not call the API. Trying again...")
                if tryCount == 3:
                    print(f"API Caller failed after {tryCount} tries. Exiting...")
                    print("Please check your API URL and internet connection and try again.")
                    exit(3)
            if tryCount < 3:
                continue

    async def parser_step(self, state: PlanExecute):
        tryCount = 0
        while True:
            try:
                task = state["plan"][0]
                input_for_parser = {"task": task, "api output": state["current_agent_answer"]}
                parse = await self.parser.ainvoke({"messages": [("user", str(input_for_parser))]})
                logger.runlog(f"Parser Response:\n---------------\n\
                            {parse.res}")
                logger.runlog(f"Past_steps: {task, state['past_steps']}")
                return {"current_agent_answer": dict(parse.res), "past_steps": [(task, str(parse.res))]}
            except Exception as e:
                logger.runlog(f"Error in Parser step: {e}")
                tryCount += 1
                print(f"Error in Parser step: {e}")
                print(f"Could not parse the API response. Trying again...")
                if tryCount == 3:
                    print(f"Parser failed after {tryCount} tries. Exiting...")
                    print("Please check your API URL and internet connection and try again.")
                    exit(4)
            if tryCount < 3:
                continue

    async def decider_step(self, state: PlanExecute):
        try:
            tryCount = 0
            task = state["plan"][0]
            original_plan = state["original_plan"]
            currect_answer = state["current_agent_answer"]
            input_for_decider = {"task": task, "original_plan": original_plan, "current_answer": currect_answer, "user_input": state["input"]}
            logger.runlog(f"Decider input: {input_for_decider}")
            while True:
                decision = await self.decider.ainvoke({"messages": [("user", str(input_for_decider))]})
                logger.runlog(f"Decider Response:\n---------------\n\
                            decision: {decision.decision}, wrong_answer: {decision.wrong_answer}, final: {decision.final}")
                if decision.decision and not decision.wrong_answer:
                    if decision.final:
                        logger.runlog(f"Final Response: {decision.final}")
                        return {"final": decision.final}
                    else: raise KeyError("final key is not provided.")
                elif decision.wrong_answer:
                    return {"wrong_answer": True}
                else:
                    return {"wrong_answer": False}
        except Exception as e:
            tryCount += 1
            logger.runlog(f"Error in Decider step: {e}")
            print(f"Error in Decider step: {e}")
            if tryCount == 3:
                print(f"Could not decide what to do. Please check the input and try again.")
                print("Exiting the program.")
                exit(6)

    async def replan_step(self, state: PlanExecute):
        tryCount = 0
        try:
            while True:
                new_plan = await self.replanner.ainvoke(state)
                logger.runlog(f"Replan Response:\n---------------\n\
                            {new_plan.steps}")
                return {"plan": new_plan.steps}
        except Exception as e:
            tryCount += 1
            logger.runlog(f"Error in Replan step: {e}")
            print(f"Error in Replan step: {e}")
            print(f"Could not replan the task. Trying again...")
            if tryCount == 3:
                print(f"Replan failed after {tryCount} tries. Exiting...")
                print("Please check your API URL and internet connection and try again.")
                exit(5)
           
    def should_end(self, state: PlanExecute):
        if "final" in state and state["final"]:
            logger.runlog(f"Final Response: {state["final"]}")
            return END 
        else:   
            return "Replan"
        
        
    def create_graph(self, g: StateGraph.compile):
        a = g.get_graph(xray=True).draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(a)
        return a
    
    def show_graph(self):
        Image.open("graph.png").show()