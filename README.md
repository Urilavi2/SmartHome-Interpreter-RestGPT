# Smart Home AI Agent

An advanced voice-controlled smart home system that leverages large language models (LLMs) to interpret and execute complex, natural language commands. This project revolutionizes smart home control by enabling intuitive voice interaction with connected devices through AI-powered command processing.

## Project Overview

Traditional smart home systems often rely on limited voice commands or complex app interfaces, reducing usability. This project develops an intelligent smart home system using AI agents capable of understanding and executing complex, multi-step voice commands through natural language processing.

### Key Features

- **Natural Language Processing**: Processes complex, conversational voice commands using GPT-4.1
- **Multi-Step Command Execution**: Handles conditional logic and sequential operations
- **Real-Time Device Control**: Controls LEDs, LCD displays, sensors, and other smart home devices
- **RESTful API Integration**: Built on OpenAPI standard for extensible device communication
- **Modular Architecture**: Graph-based workflow using LangGraph for scalable processing
- **High Reliability**: Achieved 92% success rate across comprehensive testing scenarios

## How to Run

1. **Full run** - with Microphone, remote smart home hit: `make run`
2. **Run with keyboard and local server** - `make keyboard`
3. **Run with local server and microphone** - `make local`

**NOTE:** Microphone supports only for Windows and was not been used, tested and verified on other devices.

## System Architecture

The system consists of three main components:

### Hardware Layer
- **ESP32 Microcontroller**: Acts as local web server with Wi-Fi connectivity
- **Connected Devices**: RGB LED, LCD display, temperature sensor, potentiometer
- **Power**: Standard USB power supply through ESP32

### API Layer
- **RESTful API**: OpenAPI-compliant endpoints for device control
- **Local Web Server**: Hosted on ESP32 for real-time device communication
- **Standardized Interface**: Consistent request/response formats

### Software Framework
- **RestGPT-Based Architecture**: Intelligent command processing and execution
- **LangGraph Workflow**: Directed graph structure with specialized processing nodes
- **Plan-and-Solve Prompting**: Advanced LLM reasoning through planning and execution phases
- **Speech-to-Text**: Voice input conversion for natural interaction

## Technical Specifications

| Component | Specification |
|-----------|--------------|
| Microcontroller | ESP32 (Wi-Fi, Bluetooth) |
| Devices | RGB LED, LCD, Temperature Sensor, Potentiometer |
| Software Stack | RestGPT-based, LangGraph, OpenAPI, STT |
| LLM Integration | Plan-and-Solve Prompting, GPT-4.1 |
| API Endpoints | LED, LCD, Sensors, System Status |
| User Interface | Voice-controlled, keyboard |
| Network | Local web server (RESTful API) |

## API Endpoints

| Endpoint | Method | Purpose | Response Format |
|----------|--------|---------|-----------------|
| `/led/{led_color}` | GET/POST | Control LED state and color | `{"status": "on", "color": "red"}` |
| `/lcd` | POST | Display message on LCD | `{"message": "text"}` |
| `/temperature` | GET | Get temperature reading | `{"celsius": 24.5, "fahrenheit": 76.1}` |
| `/potentiometer` | GET | Read resistance value | `{"resistance": 512}` |
| `/get-all` | GET | Fetch all device statuses | Combined device status JSON |

## Testing Results

The system was evaluated with 50 test queries across four complexity levels:

- **Level 1 (Simple Commands)**: 90% success rate (9/10)
- **Level 2 (Two Actions/Conditions)**: 100% success rate (14/14)
- **Level 3 (Conditional & Multi-Step)**: 86% success rate (12/14)
- **Level 4 (Complex Multi-Variable)**: 92% success rate (11/12)

**Overall Success Rate: 92%**

### Example Commands

- **Level 1**: "Turn on the green LED!"
- **Level 2**: "Display 'CHECK' on LCD and turn off red LED"
- **Level 3**: "If temperature < 18, turn on red LED and display 'COLD'"
- **Level 4**: "If LCD has 'ready' and temp between 21-23, turn on blue + red LEDs, show 'Ready OK' else, if the resistance is greater than 200 turn the green LED"

## Architecture Components

### RestGPT Framework Nodes

1. **Planner Node**: Generates high-level plans from natural language commands
2. **API Selector Node**: Selects appropriate API endpoints based on OpenAPI specification
3. **Executor Node**: Executes API calls and processes responses
4. **Parser Node**: Extracts and structures information from API responses
5. **Decider Node**: Determines workflow continuation or termination
6. **Replanner Node**: Generates revised plans when goals aren't achieved

## Project Results

- **92% Overall Success Rate**: Across comprehensive testing scenarios
- **Natural Language Processing**: Successfully interprets complex, multi-step commands
- **Real-Time Control**: Responsive device control with minimal latency
- **Modular Design**: Extensible architecture for future device integration
- **Reliable Hardware Integration**: Consistent ESP32 and sensor performance

## Contributors

- **Student**: Uri Lavi (urila@post.bgu.ac.il)
- **Advisor**: Prof. Chen Avin
- **Institution**: Ben-Gurion University of the Negev, Faculty of Engineering Science

## References

This project builds upon advanced research in:
- Chain-of-Thought Prompting for LLM reasoning
- Plan-and-Solve Prompting techniques
- RestGPT framework for API integration
- LangGraph for workflow orchestration


