import operator
from typing import List, Any, Annotated, Tuple, Dict, Union, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from enum import Enum


class PlanModel(BaseModel):
    """Plan to follow in future"""
    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )

class ParserModel(BaseModel):
    """Used to parse the natural langauge output from the agent to python dict"""
    res: Union[Dict[str, Any], Dict[str, str]] = Field(
        description="holds the organized response from the agent, with the wanted information according to plan. The keys are refined information like person_id, movie_id, person_name, movie_name and more."
    )

class EndpointModel(BaseModel):
    """Endpoint to get information from"""
    endpoint: Union[Dict[str, Any], Dict[str, str]] = Field(
        description="An endpoint to send http request to. Should have keys like: http_method, URL, path_variables, queries, headers, body, etc."
    )
    old_result: str = Field(
        description="The old result calculated before. return None if not used."
    )

class PlanExecute(TypedDict):
    input: str
    original_plan: List[str]
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    api: Annotated[List[dict], operator.add]
    task: int
    response: str
    current_agent_answer: str


class ResponseModel(BaseModel):
    """Final answer that fulfills user request"""
    response: str


class ActModel(BaseModel):
    """Action to perform."""
    more: bool = Field(
        description="Action to perform. If you want to respond to user, return False. "
        "If you need to further use tools to get the answer, Return True."
    )
    response: Optional[str] = Field(
        default=None,
        description="Optional response to provide if available."
    )
    replan: Optional[PlanModel] = Field(
        default=None,
        description="Optional new plan schema if available."
    )



class Entity(Enum):
    planner = 1
    api = 2
    executor = 3
    full = 4