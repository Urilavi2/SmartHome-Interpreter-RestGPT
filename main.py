from utils.tools import split_args
from prototype import prototype
from run import run
from testing import tests
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
        elif entity.lower() == "testing":
            subject = kwargs.get("subject",None)
            if not subject:
                print("No subject for testing specified")
                exit(2)
            asyncio.run(tests(subject))
        else:
            asyncio.run(prototype(*args, **kwargs))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()