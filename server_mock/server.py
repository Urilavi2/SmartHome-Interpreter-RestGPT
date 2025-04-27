from flask import Flask, request, jsonify
from server_models import lcdModel, ledModel, potentiometerModel, temperatureModel
import random

ledColors :list = ["red", "green", "blue"]
ledStatus :list = ["OFF", "ON"]
temprature = {"celsius": random.uniform(10, 40), "fahrenheit": random.uniform(50, 104)}
potentiometer = random.randint(0, 10000)

lcd = lcdModel(message="Hello World")
leds = [ledModel(color=color, state=random.choice(ledStatus)) for color in ledColors]
potentiometer = potentiometerModel(resistance=potentiometer)
temperature = temperatureModel(celsius=temprature["celsius"], fahrenheit=temprature["fahrenheit"])



# Create the Flask application
app = Flask(__name__)

# Basic GET endpoint
@app.route('/', methods=['GET'])
def hello():
    return jsonify({
        'message': 'Hello, World!',
    })


@app.route("/led", methods=["GET"])
def led():
    """Control the LED."""
    # Get the query parameters from the request
    color = request.args.get("color")
    state = request.args.get("state")
    if not color or not state:
        return jsonify({
            'message': 'Missing color or status parameter.'
        }), 404
    # Validate the input using Pydantic model
    for led_idx in range(0, len(leds)):
        if leds[led_idx].color == color:
            leds[led_idx].state = state
            return jsonify(leds[led_idx].model_dump()), 200
    return jsonify({
        'message': 'Invalid color or status parameter.'
    }), 404


@app.route("/lcd", methods=["GET", "POST"])
def lcd_screen():
    """Get or set the LCD message."""
    if request.method == "POST":
        # Update the LCD message
        new_message = request.json.get("message")
        if new_message:
            global lcd
            lcd.message = new_message
            return jsonify(lcd.model_dump()), 200
        else:
            return jsonify({"message": "Invalid message."}), 400
    elif request.method == "GET":
        # Get the current LCD message
        return jsonify(lcd.model_dump()), 200


@app.route("/temperature", methods=["GET"])
def get_temperature():
    """Get the current temperature."""
    temperature.celsius = random.uniform(10, 40)
    temperature.fahrenheit = random.uniform(50, 104)
    return jsonify(temperature.model_dump()), 200


@app.route("/potentiometer", methods=["GET"])
def get_potentiometer():
    """Get the current potentiometer value."""
    potentiometer.resistance = random.randint(0, 10000)
    return jsonify(potentiometer.model_dump()), 200

@app.route("/get-all", methods=["GET"])
def get_all():
    """Get all values."""
    return jsonify({
        "led": [led.model_dump() for led in leds],
        "temperature": temperature.model_dump(),
        "potentiometer": potentiometer.model_dump(),
        "lcd": lcd.model_dump()
    }), 200

# Error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Resource not found',
        'status': 'error'
    }), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500

if __name__ == '__main__':
    # Run the application (debug=True for development only)
    app.run(host='api-esp32-smarthome.local', port=80, debug=True)