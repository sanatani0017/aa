import typer
from .core.logging import logger
from .core.planner import PlannerExecutor

app = typer.Typer(help="Ultra CLI Agent — autonomous AI coding pair programmer")

@app.command()
def chat(prompt: str = typer.Argument(..., help="Instruction or task")):
    agent = PlannerExecutor()
    logger.info(f"Task: {prompt}")
    result = agent.run(prompt)
    logger.action(result)

if __name__ == "__main__":
    app()
