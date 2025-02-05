from utils.tools import split_args
from prototype import prototype
import asyncio

def main():
    try:
        args, kwargs = split_args()
        asyncio.run(prototype(*args, **kwargs))
    except Exception as e:
        print(e)


# missing:
# pass the API spec to the agent  --> need to change the data structure of api_ref (in Prompts class) to include as key the name and method of the endpoint, and as value everything else.
# Replan if caught an error - count errors
# Change the propmts to be more informative and more general. Right now they are very specific to the TMDB API (like moive_id, etc.)

if __name__ == "__main__":
    main()