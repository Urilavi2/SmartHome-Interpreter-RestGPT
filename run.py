import os
import logging
import json
from datetime import datetime
from utils.tools import testConnection, create_graph
from dotenv import load_dotenv, find_dotenv
from prompts.prompts import Prompts
from models.workflow import Workflow

RUNTIME_level = 99
logging.addLevelName(RUNTIME_level, "RUNTIME")
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f"logs/{datetime.now().strftime('%H%M%S%d%m%Y')}.log"),
                    ])

  
def runlog(self, message, *args, **kwargs):
    RUNTIME_level = 99
    if self.isEnabledFor(RUNTIME_level):
            self._log(RUNTIME_level, message, args, **kwargs)

logging.Logger.runlog = runlog
logger = logging.getLogger(__name__)

async def run(*args, **kwargs):
    _ = load_dotenv(find_dotenv())
    prompts = Prompts()
    workflow = Workflow(prompts=prompts)
    graph = args[0] if len(args) > 0 and args[0]=="graph" else False
    if graph:
        create_graph(workflow.app)
        print("Graph created successfully.")
        exit(0)
    for count in range(1, 4):
        if testConnection(prompts.api_url, count):
            break
    while True:
        default_prompt = "turn on red light"
        inputs = {"input": input(f"(press enter for default message: '{default_prompt}') >> ")}
        if inputs["input"] == "exit":
            print("Exiting...")
            break
        elif inputs["input"] == "":
            inputs["input"] = default_prompt

        config = {"recursion_limit": 20}

        async for event in workflow.app.astream(inputs, config=config):
            for k, v in event.items():
                    if k != "__end__":
                        print(json.dumps(v, indent=4))