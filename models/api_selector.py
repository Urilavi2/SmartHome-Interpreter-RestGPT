from typing import List, Dict, Any, Optional

from langchain import BasePromptTemplate, PromptTemplate
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chat_models import ChatOpenAI
from langchain.chains.base import Chain
from langchain.llms.base import BaseLLM
from logging import getLogger
from langchain_core.tools import tool

from utils.sawgger_interpreter import ReducedOpenAPISpec

# API_SELECTOR_PROMPT = ""
icl_examples = """Example 1:

Background: The id of Wong Kar-Wai is 12453
User query: give me the latest movie directed by Wong Kar-Wai.
API calling 1: GET /person/12453/movie_credits to get the latest movie directed by Wong Kar-Wai (id 12453)
API response: The latest movie directed by Wong Kar-Wai is The Grandmaster (id 44865), ...

Example 2:

Background: No background
User query: search for movies produced by DreamWorks Animation
API calling 1: GET /search/company to get the id of DreamWorks Animation
API response: DreamWorks Animation's company_id is 521
Instruction: Continue. Search for the movies produced by DreamWorks Animation
API calling 2: GET /discover/movie to get the movies produced by DreamWorks Animation
API response: Puss in Boots: The Last Wish (id 315162), Shrek (id 808), The Bad Guys (id 629542), ...

Example 3:

Background: The id of the movie Happy Together is 18329
User query: search for the director of Happy Together
API calling 1: GET /movie/18329/credits to get the director for the movie Happy Together
API response: The director of Happy Together is Wong Kar-Wai (12453)

Example 4:

Background: No background
User query: search for the highest rated movie directed by Wong Kar-Wai
API calling 1: GET /search/person to search for Wong Kar-Wai
API response: The id of Wong Kar-Wai is 12453
Instruction: Continue. Search for the highest rated movie directed by Wong Kar-Wai (id 12453)
API calling 2: GET /person/12453/movie_credits to get the highest rated movie directed by Wong Kar-Wai (id 12453)
API response: The highest rated movie directed by Wong Kar-Wai is In the Mood for Love (id 843), ...
"""

logger = getLogger(__name__)

try:
    with open("../prompts/api_selector_prompt.txt") as f:
        API_SELECTOR_PROMPT = f.read()
except Exception as e:
    logger.error(f"Encountered an error while reading api_selector_prompt.txt.\nError message:\n--------------\n{e}")


class API_selector(Chain):
    def __init__(self, llm: BaseLLM, background: str, api_spec: ReducedOpenAPISpec):
        api_name_desc = [f"{endpoint[0]} {endpoint[1].split('.')[0] if endpoint[1] is not None else ''}" for endpoint in
                         api_spec.endpoints]
        api_name_desc = '\n'.join(api_name_desc)
        api_selector_prompt = PromptTemplate(
            template=API_SELECTOR_PROMPT,
            partial_variables={"endpoints": api_name_desc, "icl_examples": icl_examples},
            input_variables=["plan", "background", "agent_scratchpad"],
        )
        self.output_key: str = "result"
        super().__init__(llm=llm, api_spec=api_spec, api_selector_prompt=api_selector_prompt)

    @property
    def _chain_type(self) -> str:
        return "RestGPT API Selector"

    @property
    def input_keys(self) -> List[str]:
        return ["plan", "background"]

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        pass
