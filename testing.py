from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from prompts.prompts import Prompts
from models.workflow import Workflow
import os
import json


async def tests(subject):
    _ = load_dotenv(find_dotenv())
    prompts = Prompts()
    workflow = Workflow(prompts=prompts, subject=subject)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_file = f"datasets/inputs/{subject}.json"
    output_file = f"datasets/outputs/{subject}_output_{timestamp}.txt"
    config = {"recursion_limit": int(os.environ.get("RECURSION_LIMIT", "20"))}

    match subject.lower():
        case "planner":
            await planner(workflow=workflow,
                          input_file=input_file,
                          config=config,
                          output_file=output_file)


async def planner(workflow, input_file, config, output_file):
     with open(input_file, 'r') as in_file:
           inputs_json = in_file.read()
           inputs_json = json.loads(inputs_json)
           for query in inputs_json:
                inputs = {"input": query["input"]}
                async for event in workflow.app.astream(inputs, config=config):
                            for k, v in event.items():
                                    if k != "__end__":
                                        dumps = {}
                                        dumps["input"] = inputs["input"]
                                        dumps["plan"] = v["plan"]
                                        with open(output_file, 'a') as f:
                                            f.write(json.dumps(dumps, indent=4))
                                            f.write(",\n")