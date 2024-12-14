from dotenv import load_dotenv, find_dotenv
from logging import getLogger, Logger
from typing import List, Optional, Any

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatResult
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field
from langgraph.prebuilt import create_react_agent

# from utils.api_tool import planner_prompt

logger = Logger(name=__name__, level='INFO')

_ = load_dotenv(find_dotenv())


# try:
#     with open("../prompts/planner_prompt.txt", "r") as f:
#         PLANNER_PROMPT = f.read()
# except Exception as e:
#     logger.error(f"Encountered an error while reading api_selector_prompt.txt.\nError message:\n--------------\n{e}")
#     exit(1)


class PlanModel(BaseModel):
    """Plan to follow in future"""
    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )

class Planner(BaseChatModel):
    prompt: str
    llm: BaseChatModel
    llm_model: str
    def __init__(self, prompt: str, llm_model: str):
        self.prompt = ChatPromptTemplate.from_messages([("system", prompt), ("placeholder", "{messages}")])
        self.llm_model = llm_model
        self.planner_client = self.prompt | ChatOpenAI(self.llm_model, temperature=0.9).with_structured_output(PlanModel)
        super().__init__(model=self.planner_client, planner_prompt=self.prompt)


    def _llm_type(self) -> str:
        return self.llm_model

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        return self.planner_client._generate(messages, stop, run_manager, **kwargs)

propmt = """For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps."""
p = Planner(prompt=propmt, llm_model="gpt-4o-mini")
res = p.invoke({
        "messages": [
            ("user", "what is the hometown of the current Best main male actor winner?")
        ]
    })
print(res)

