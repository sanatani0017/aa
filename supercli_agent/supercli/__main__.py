import asyncio
from supercli.ui.cli import run_cli

def main() -> None:
    asyncio.run(run_cli())

if __name__ == "__main__":
    main()
