from argparse import ArgumentParser

from scripts.UI import mainUI
from scripts.telegramBot import mainBot

def get_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--method",
        default="ui"
    )
    return parser


if __name__ == '__main__':
    
    args = get_parser().parse_args()
    method = args.method.lower()
    
    if method == "ui":
        mainUI()
    elif method == "bot":
        import asyncio
        asyncio.run(mainBot())
    else:
        import sys
        print("Please provide running method: 'ui' or 'bot'")
        sys.exit()