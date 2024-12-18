import operator
from typing import List, Any, Annotated, Tuple, Dict, Union
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict


class PlanModel(BaseModel):
    """Plan to follow in future"""
    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )

class EndpointModel(BaseModel):
    """Endpoint to get information from"""
    endpoint: Union[Dict[str, Any], Dict[str, str]] = Field(
        description="An endpoint to send http request to. Should have keys like: http method, URL, path variables, queries, headers, body, etc."
    )

class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    api: Annotated[List[dict], operator.add]
    task: int
    response: str


class ResponseModel(BaseModel):
    """Response to user."""

    response: str


class ActModel(BaseModel):
    """Action to perform."""
    action: Union[ResponseModel, PlanModel] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )

class Act(BaseModel):
    """Action to perform."""

    action: Union[ResponseModel, PlanModel] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )