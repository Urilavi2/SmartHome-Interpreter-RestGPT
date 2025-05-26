import os
import logging
import json
from datetime import datetime
from utils.tools import testConnection, create_graph
from dotenv import load_dotenv, find_dotenv
from prompts.prompts import Prompts
from models.workflow import Workflow
from utils.stt import SpeechToText
from utils.debugOptions import DebugOptions

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
    stt = None
    prompts = Prompts()
    workflow = Workflow(prompts=prompts)
    keyboard = False

    if "keyboard" in args:
        keyboard = True
    else:
        stt = SpeechToText()

    if "graph" in args:
        create_graph(workflow.app)
        print("Graph created successfully.")
        exit(0)

    for count in range(1, 4):
        if testConnection(prompts.api_url, count):
            break
      
    while True:
        default_prompt = "turn on red light"
        if not keyboard:
            try:
                
                input(f"\n{'*' * 35}\n\nPress enter to start talking...\n\n{'*' * 35}")
                inputs = {"input": stt.listen(default_msg=default_prompt)}
            except Exception as e:
                 print(e)
                 continue
        else:
            inputs = {"input": input(f"(press enter for default message: '{default_prompt}') >> ")}
        
        if inputs["input"] == "exit":
            print("Exiting...")
            break
        elif inputs["input"] == "":
            inputs["input"] = default_prompt


        config = {"recursion_limit": int(os.environ.get("RECURSION_LIMIT", "20"))}

        async for event in workflow.app.astream(inputs, config=config):
            for k, v in event.items():
                    if k != "__end__":
                        if DebugOptions() != "off":
                            print(json.dumps(v, indent=4))
                        elif  (k == "Decider" and v["final"]):
                            print(json.dumps(v["final"], indent=4))
                        