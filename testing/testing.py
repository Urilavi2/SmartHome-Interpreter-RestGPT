from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from prompts.prompts import Prompts
from models.workflow import Workflow
import os
from testing.api_selector import api_selector
from testing.planner import planner
from testing.caller import caller
from testing.parser import parser


async def tests(subject):
    _ = load_dotenv(find_dotenv())
    prompts = Prompts()
    workflow = Workflow(prompts=prompts, subject=subject)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_file = f"datasets/inputs/{subject}.json"
    output_file = f"datasets/outputs/{subject}_output_{timestamp}.json"
    config = {"recursion_limit": int(os.environ.get("RECURSION_LIMIT", "20"))}

    match subject.lower():
        case "planner":
            await planner(workflow=workflow,
                          input_file=input_file,
                          config=config,
                          output_file=output_file)
        case "api_selector":
                await api_selector(workflow=workflow,
                                   input_file=input_file,
                                   config=config,
                                   output_file=output_file)
        case "caller":
              await caller(workflow=workflow,
                            input_file=input_file,
                            config=config,
                            output_file=output_file)
        case "parser":
              await parser(workflow=workflow,
                            input_file=input_file,
                            config=config,
                            output_file=output_file)

        case "all":
              await all(workflow=workflow,
                            input_file=input_file,
                            config=config,
                            output_file=output_file,
                            timestamp=timestamp)
        case _:
            print(f"Unknown subject: {subject}")
            return



async def all(workflow, input_file, config, output_file, timestamp):
    for subject in ["planner", "api_selector", "caller", "parser"]:
        input_file = f"datasets/inputs/{subject}.json"
        output_file = f"datasets/outputs/{subject}_output_{timestamp}.json"
        match subject.lower():
            case "planner":
                await planner(workflow=workflow,
                            input_file=input_file,
                            config=config,
                            output_file=output_file)
            case "api_selector":
                    await api_selector(workflow=workflow,
                                    input_file=input_file,
                                    config=config,
                                    output_file=output_file)
            case "caller":
                await caller(workflow=workflow,
                                input_file=input_file,
                                config=config,
                                output_file=output_file)
            case "parser":
                await parser(workflow=workflow,
                                input_file=input_file,
                                config=config,
                                output_file=output_file)