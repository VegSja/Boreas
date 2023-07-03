import os

from loguru import logger

from app.core.errors import PredictException, ModelLoadException
from app.core.config import MODEL_NAME, MODEL_PATH


class MachineLearningModelHandlerScore:
    """
    A class for handling machine learning models and making predictions.

    Attributes:
        model: The machine learning model object.
    """

    model = None

    @classmethod
    def predict(cls, load_wrapper=None, method="predict"):
        """
        Make predictions using the machine learning model.

        Args:
            load_wrapper: Optional. A function
            for loading the model. If provided, it will be used to load the model.
            method: Optional. The method to use
            for making predictions. Defaults to "predict".

        Returns:
            The prediction result.

        Raises:
            PredictException: If the specified method is missing in the machine learning model.
        """

        clf = cls.get_model(load_wrapper)
        if hasattr(clf, method):
            return getattr(clf, method)(input)
        raise PredictException(f"'{method}' attribute is missing")

    @classmethod
    def get_model(cls, load_wrapper):
        """
        Get the machine learning model.

        Args:
            load_wrapper: Optional. A function for
             loading the model. If provided, it will be used to load the model.

        Returns:
            The machine learning model object.

        Note:
            The model will be loaded if it is not
            already loaded and the load_wrapper function is provided.
        """

        if cls.model is None and load_wrapper:
            cls.model = cls.load(load_wrapper)
        return cls.model

    @staticmethod
    def load(load_wrapper):
        """
        Load the machine learning model.

        Args:
            load_wrapper: A function for loading the model.

        Returns:
            The loaded machine learning model object.

        Raises:
            FileNotFoundError: If the model file path does not exist.
            ModelLoadException: If the model fails to load.
        """
        model = None
        if MODEL_PATH.endswith("/"):
            path = f"{MODEL_PATH}{MODEL_NAME}"
        else:
            path = f"{MODEL_PATH}/{MODEL_NAME}"
        if not os.path.exists(path):
            message = f"Machine learning model at {path} does not exist!"
            logger.error(message)
            raise FileNotFoundError(message)
        model = load_wrapper(path)
        if not model:
            message = f"Model {model} could not be loaded!"
            logger.error(message)
            raise ModelLoadException(message)
        return model
