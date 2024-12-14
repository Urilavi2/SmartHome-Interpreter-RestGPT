from dotenv import load_dotenv, find_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain


_ = load_dotenv(find_dotenv())
llm_model = "gpt-4o-mini"

def main():
    # prompt = ChatPromptTemplate.from_template(
    #     "What is the best name to describe \
    #     a company that makes {product}? what will be the price based on the customer's name {name}"
    # )
    # llm = ChatOpenAI(temperature=0.9, model=llm_model)
    # chain = LLMChain(llm=llm, prompt=prompt)
    # product = "Queen Size Sheet Set"
    # name = "uri"
    # a = chain.run({"product": product,
    #                "name": name})  # the key is "product", as defined in the prompt. for multi-vars, pass dict with the keys with expected names and the values
    # print(a)
    testing()




def testing():
    from typing import List

    from langchain_community.tools import tool
    from langchain_community.tools.tavily_search import TavilySearchResults
    from langchain_openai import ChatOpenAI
    @tool
    def print_hi():
        """prints hi"""
        print('Hello, World!')

    from pydantic import BaseModel, Field

    class Plan(BaseModel):
        """Plan to follow in future"""

        steps: List[str] = Field(
            description="different steps to follow, should be in sorted order"
        )

    from langchain_core.prompts import ChatPromptTemplate

    planner_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """For the given objective, come up with a simple step by step plan. \
    This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
    The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.""",
            ),
            ("placeholder", "{messages}"),
        ]
    )
    planner = planner_prompt | ChatOpenAI(
        model="gpt-4o", temperature=0
    ).with_structured_output(Plan)


if __name__ == "__main__":
    main()