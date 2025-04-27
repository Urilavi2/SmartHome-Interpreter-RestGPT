from pydantic import BaseModel, Field

class ledModel(BaseModel):
    """Model for LED control."""
    color: str = Field(
        description="LED to control, e.g., 'led1', 'led2'."
    )
    state: str = Field(
        description="State of the LED, e.g., 'on', 'off'."
    )


class temperatureModel(BaseModel):
    """Model for temperature."""
    celsius: float = Field(
        description="Temperature in Celsius."
    )
    fahrenheit: float = Field(
        description="Temperature in Fahrenheit."
    )


class lcdModel(BaseModel):
    """Model for LCD message."""
    message: str = Field(
        description="Message to display on the LCD."
    )

class potentiometerModel(BaseModel):
    """Model for potentiometer."""
    resistance: int = Field(
        description="Resistance value of the potentiometer."
    )
