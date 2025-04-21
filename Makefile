CLEAN_FILES := logs/* graph.png

planner:
	@echo "Starting Smart Home Prototype with Planner only..."
	@py ./main.py entity=planner

api:
	@echo "Starting Smart Home Prototype with Planner + API Selector..."
	@py ./main.py entity=api

executor:
	@echo "Starting Smart Home Prototype with Planner + API Selector + Executor..."
	@py ./main.py entity=executor

full:
	@echo "Starting Smart Home Full Prototype Application..."
	@py ./main.py entity=full

run:
	@echo "Starting Smart Home Framework..."
	@py ./main.py entity=framework

test:
	@echo "Starting Smart Home With Local Server..."
	@py ./main.py entity=framework --local

clean:
	@echo "Cleaning up..."
	@rm -rf $(CLEAN_FILES) | true