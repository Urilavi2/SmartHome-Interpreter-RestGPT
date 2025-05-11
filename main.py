from utils.tools import split_args
from prototype import prototype
from run import run
import asyncio

def main():
    try:
        args, kwargs = split_args()
        entity = kwargs.get("entity",None)
        if entity is None:
            print("No entity specified")
            exit(1)
        if entity.lower() == "framework":
            asyncio.run(run(*args, **kwargs))
        else:
            asyncio.run(prototype(*args, **kwargs))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()