from .core.logging import logger

def main():
    logger.info("Ultra CLI Agent core loaded.")
    logger.warn("Run via: ultra chat <task>")

if __name__ == "__main__":
    main()
