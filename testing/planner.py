import json


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