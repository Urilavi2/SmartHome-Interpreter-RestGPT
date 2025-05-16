import json


async def api_selector(workflow, input_file, config, output_file):
    with open(input_file, 'r') as in_file:
        inputs_json = in_file.read()
        inputs_json = json.loads(inputs_json)
        grade = 100
        for query in inputs_json:

            success = True
            plan = list(query["plan"])
            wanted_api = list(query["api"])
            got_api = {}
            past_steps = []
            print(f"{'-'*40}\nInput: {query["input"]}\n{'-'*40}\n")
            for step_idx, step in enumerate(plan):
                wanted_api_step: dict = wanted_api[step_idx]
                print(f"Step: {step}")
                inputs = {"input": step}
                if step_idx >= 1:
                     inputs = {"input": step + "You already did the following endpoints: " + str(past_steps)}
                async for event in workflow.app.astream(inputs, config=config):
                    for k, v in event.items():
                        if k != "__end__":
                            got_api = v["api"][0]
                            success = api_selector_conditions(wanted_api=wanted_api_step, api=got_api, only_url=query["only_url"])
                if not success:
                    grade -= query["grade"]
                    faliure_dict = {"input": query["input"], "step": step, "step index": step_idx, "wanted api step": wanted_api_step, "got api step": got_api, "past steps": past_steps}
                    with open(output_file ,'a') as f:
                        f.write(json.dumps(faliure_dict, indent=4))
                        f.write(",\n")
                    break                    
                past_steps.append(wanted_api_step)

    with open(output_file ,'a') as f: 
         f.write(f"\n{'*'*20}\n\nFinal Grade: {grade}\n\n{'*'*20}")
    print(f"\n{'*'*20}\n\nFinal Grade: {grade}\n\n{'*'*20}")

def api_selector_conditions(wanted_api: dict, api: dict, only_url: bool) -> bool:
        success = ((api["http_method"].upper() == wanted_api["method"].upper()) and (api["URL"].lower() == wanted_api["URL"].lower()))
        if success and not only_url:
            if api["http_method"].upper() == "POST":
                wanted_body = wanted_api.get("body", {})
                got_body = api.get("body", {})
                success = wanted_body.get("message", "").lower() == got_body.get("message", "None").lower()
            elif "led" in api["URL"]:
                wanted_queries:dict = wanted_api.get("queries", {})
                got_queries:dict =  api.get("queries", {})
                success = (wanted_queries.get("color", "").lower() == got_queries.get("color", "None").lower()) and (wanted_queries.get("state", "").lower() == got_queries.get("state", "None").lower())
        return success