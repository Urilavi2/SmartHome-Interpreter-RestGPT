from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from prompts.prompts import Prompts
from models.workflow import Workflow
import os
from testing.api_selector import api_selector
from testing.planner import planner
from testing.caller import caller
from testing.parser import parser
from utils.tools import progress_bar
import json

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
    inputs_json = {}
    with open(input_file, 'r') as in_file:
        inputs_json = in_file.read()
        inputs_json = json.loads(inputs_json)
    if inputs_json is None:
        print(f"Input file {input_file} is empty or not found.")
        return
    for query_idx in range(0, len(inputs_json), 10):
        query = inputs_json[query_idx]
        index = int(query.get("index", 0))
        progress_bar(query_idx + 1, len(inputs_json), prefix="Running all tests", length=50)
        if index == 0:
            print("Index is 0, skipping this query.")
            continue
        inputs = {"input": query.get("input", "")}
        if not inputs["input"]:
            print("Input is empty, skipping this query.")
            continue
        answers = []
        async for event in workflow.app.astream(inputs, config=config):
            for k, v in event.items():
                if k == "Parser":
                    answers.append(v.get("current_agent_answer", {}))
                elif k == "Decider" and v.get("final", ""):
                     answers.append(v.get("final"))
        
        with open(output_file, 'a') as f:
            f.write(f"{'*' * 20}\n\nQuery: {query.get('input', '')}\nIndex: {index}\nAnswers:\n")
            for answer in answers:
                f.write(json.dumps(answer, indent=4))
                f.write("\n")
            f.write("\n" + "*" * 20 + "\n\n")
    print(f"All tests completed. Results saved to {output_file}.")