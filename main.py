from utils.tools import split_args
from prototype import prototype
import asyncio

def main():
    try:
        args, kwargs = split_args()
        asyncio.run(prototype(*args, **kwargs))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()