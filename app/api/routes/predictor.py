import json

from fastapi import APIRouter, HTTPException

from app.core.config import INPUT_EXAMPLE
from app.services.predict import MachineLearningModelHandlerScore as model
from app.models.prediction import (
    HealthResponse,
    MachineLearningResponse,
    MachineLearningDataInput,
)

router = APIRouter()


def get_prediction(data_point):
    """
    Perform a prediction based on the provided data input.

    Args:
        data_point (MachineLearningDataInput): The
        input data for prediction.

    Returns:
        MachineLearningResponse: The prediction result.

    Raises:
        HTTPException: If the 'data_input' argument is invalid
        or an exception occurs during prediction.
    """
    return model.predict(data_point, method="predict")


@router.post(
    "/predict",
    response_model=MachineLearningResponse,
    name="predict:get-data",
)
async def predict(data_input: MachineLearningDataInput):
    """
    Perform a prediction based on the provided data input.

    Args:
        data_input (MachineLearningDataInput):
        The input data for prediction.

    Returns:
        MachineLearningResponse: The prediction result.

    Raises:
        HTTPException: If the 'data_input'
        argument is invalid or an exception occurs during prediction.
    """
    if not data_input:
        raise HTTPException(status_code=404, detail="'data_input' argument invalid!")
    try:
        data_point = data_input.get_np_array()
        prediction = get_prediction(data_point)

    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Exception: {err}") from err

    return MachineLearningResponse(prediction=prediction)


@router.get(
    "/health",
    response_model=HealthResponse,
    name="health:get-data",
)
async def health():
    """
    Check the health status of the application.

    Returns:
        HealthResponse: The health status of the application.

    Raises:
        HTTPException: If an exception occurs while checking the health status.
            The status code will be 404 if the application is unhealthy.
    """
    is_health = False
    try:
        test_input = MachineLearningDataInput(
            **json.loads(open(  # pylint: disable=R1732
                INPUT_EXAMPLE,
                "r",
                encoding="utf-8").read())
        )
        test_point = test_input.get_np_array()
        get_prediction(test_point)
        is_health = True
        return HealthResponse(status=is_health)
    except Exception as exc:
        raise HTTPException(status_code=404, detail="Unhealthy") from exc
