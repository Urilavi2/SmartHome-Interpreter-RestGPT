import json
from utils.tools import grading_system
import re


async def caller(workflow, input_file, config, output_file):
    inputs_json = {}
    with open(input_file, 'r') as in_file:
        inputs_json = in_file.read()
        inputs_json = json.loads(inputs_json)
    if inputs_json == {}:
        print("No input file found")
        return  
    grading_dict = grading_system(input_json=inputs_json)
    grade = 100
    for query in inputs_json:
        success = True
        plan = list(query["plan"])
        api = list(query["api"])
        wanted_result = list(query["result"])
        got_result = None
        past_steps = []
        print(f"{'-'*40}\nInput: {query['input']}")
        for step_idx, step in enumerate(plan):
            wanted_result_step = wanted_result[step_idx]
            print(f"Step: {step}")
            inputs = {"input": {"http_request": api[step_idx], "task": step, "past_steps": past_steps}}
            async for event in workflow.app.astream(inputs, config=config):
                for k, v in event.items():
                    if k != "__end__":
                        got_result = v["current_agent_answer"][0]
                        success = caller_conditions(wanted_result=wanted_result_step, result=got_result, workflow_part=workflow.caller_test, step=step)
            if not success:
                grade -= grading_dict[query["index"]]
                faliure_dict = {"input": query["input"], "step": step, "step index": step_idx, "wanted result step": wanted_result_step, "got_result": got_result, "past steps": past_steps}
                with open(output_file ,'a') as f:
                    f.write(json.dumps(faliure_dict, indent=4))
                    f.write(",\n")
                break
            try:
                past_steps.append((step, query.get("previous_result",[None])[step_idx]))
            except Exception as e:
                print(e)
                print("task: ", step)
                print("wanted_result: ", wanted_result_step)
                print("got_result: ", got_result)
                print("past_steps: ", past_steps)
                print("query: ", query['input'])

    with open(output_file ,'a') as f: 
         f.write(f"\n{'*'*20}\n\nFinal Grade: {grade}\n\n{'*'*20}")
    print(f"\n{'*'*20}\n\nFinal Grade: {grade}\n\n{'*'*20}")
    print("grading_dict: ", grading_dict)

def caller_conditions(wanted_result, result, workflow_part, step) -> bool:
    input_to_test = {"input": {"wanted_result": wanted_result, "actual_result": result, "task": step}}
    res = workflow_part.invoke({"messages": [("user", str(input_to_test["input"]))]})
    return bool(res.decision)