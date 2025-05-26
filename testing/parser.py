import json
from utils.tools import progress_bar, grading_system
from utils.debugOptions import DebugOptions

async def parser(workflow, input_file, config, output_file):
    inputs_json = {}
    with open(input_file, 'r') as in_file:
        inputs_json = in_file.read()
        inputs_json = json.loads(inputs_json)
    if inputs_json == {}:
        print("No input file found")
        return  
    print("Number of queries: ", len(inputs_json))
    grading_dict = grading_system(input_json=inputs_json)
    grade = 100
    for query_idx, query in enumerate(inputs_json):
        progress_bar(query_idx + 1, len(inputs_json), prefix="Caller", length=50)
        true_results = list(query["result"])
        parser_results = list(query["previous_result"])
        for step_idx, (caller_result, wanted_parser_result, step) in enumerate(zip(true_results, parser_results, query["plan"])):
            inputs = {"input": {"task": step, "api output": caller_result}}
            async for event in workflow.app.astream(inputs, config=config):
                for k, v in event.items():
                    if k != "__end__":
                        parser_result = v["current_agent_answer"]
            
            if parser_result != wanted_parser_result:
                grade -= grading_dict[query["index"]]
                faliure_dict = {"input": query["input"], "step": step, "step index": step_idx, "caller result": caller_result, "wanted_parser_result":wanted_parser_result, "parsed result": parser_result}
                with open(output_file ,'a') as f:
                    f.write(json.dumps(faliure_dict, indent=4))
                    f.write(",\n")
                break
    
    with open(output_file ,'a') as f: 
         f.write(f"\n{'*'*20}\n\nFinal Grade: {grade}\n\n{'*'*20}")
    print(f"\n{'*'*20}\n\nFinal Grade: {grade}\n\n{'*'*20}")