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
    if "local" not in args:
        for count in range(1, 4):
            if testConnection(prompts.api_url, count):
                break
    while True:
        inputs = {"input": input(">> ")}
        if inputs["input"] == "exit":
            print("Exiting...")
            break
        elif inputs["input"] == "graph":
            prompts.show_graph()
            continue

        workflow = Workflow(prompts=prompts, graph=True)
        # workflow.show_graph()

        config = {"recursion_limit": 20}

        async for event in workflow.app.astream(inputs, config=config):
            for k, v in event.items():
                    if k != "__end__":
                        print(json.dumps(v, indent=4))