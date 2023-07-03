from typing import Callable
from fastapi import FastAPI


def create_start_app_handler(app: FastAPI) -> Callable:
    """
    Create handler to preload the model
    """
    def start_app() -> None:
        """
        Method to start app with handler
        """
        print(app)

    return start_app
