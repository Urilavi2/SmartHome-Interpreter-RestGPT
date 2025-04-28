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

class PlanExecute(TypedDict):
    input: str
    original_plan: List[str]
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    api: Annotated[List[dict], operator.add]
    task: int
    final: str
    current_agent_answer: str
    wrong_answer: bool

   
class DecisionModel(BaseModel):
    """Decision to make"""
    decision: bool = Field(
        description="Decision to make, True if no more steps are need or False if got the final answer."
    )
    wrong_answer: bool = Field(
        description="True if the answer is wrong, False if the answer is correct according to currect task and answer."
    )
    final: Optional[str] = Field(
        description="Final answer to be presented to the user. Apply only if decision is True.",
    )


class ActModel(BaseModel):
    """Action to perform."""
    more: bool = Field(
        description=("If the final answer is ready to present to the user, return more: false."
                    "If more steps are needed to reach the final answer, return more: true.")
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