include .env
CLEAN_FILES := logs/* graph.png datasets/outputs/*
DEBUG := off
SUBJECT:= 

run: disable-local
	@echo "Starting Smart Home Framework..."
	@py ./main.py entity=framework

local: check-connection
	@echo "Starting Smart Home With Local Server..."
	@py ./main.py entity=framework 

clean:
	@echo "Cleaning up..."
	@rm -rf $(CLEAN_FILES) | true

enable-local:
	@echo "Turnning ON 'api-esp32-smarthome.local' in hosts file..."
	@toggle_hosts.bat on 
	@echo "Done!"

disable-local:
	@set -e
	@echo "Turnning OFF 'api-esp32-smarthome.local' in hosts file..."
	@toggle_hosts.bat off
	@echo "Done!"

run-server: enable-local
	@echo "Starting Local Server..."
	@powershell.exe -Command "Start-Process cmd -ArgumentList '/k', 'python \"$(CURDIR)/server_mock/server.py\"'"
	@echo "Server started!"


check-connection:
	@curl -s -o /dev/null -w "%{http_code}" http://api-esp32-smarthome.local:80 | grep -q 200 && echo "Server is already running!" || $(MAKE) run-server


keyboard: check-connection
	@echo "Starting Smart Home With Local Server..."
	@py ./main.py entity=framework keyboard debug=$(DEBUG)


