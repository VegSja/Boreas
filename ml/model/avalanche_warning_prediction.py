"""Module for avalanche warning prediction."""
import logging

import numpy as np
import pandas as pd
import tensorflow as tf


class AvalancheWarningPrediction:
    """
    Class for avalanche warning prediction.

    We use a LSTM model to predict the avalanche warning.
    """

    def __init__(self, model_path):
        """
        Class for avalanche warning prediction.

        Parameters
        ----------
        model_path : str
            Path to the model to load. If None, a new model is built.
        """
        if model_path is None:
            self._model = self.build_model()
        else:
            self._model = self.load_model(model_path)

    def build_model(self, num_outputs: int = 4, input_shape: tuple = (7, 11)):
        """
        Build a LSTM model for avalanche warning prediction.

        Parameters
        ----------
        num_outputs : int, optional
            Number of outputs of the model, by default 4
        input_shape : tuple, optional
            Shape of the input data, by default (7, 11)

        Returns
        -------
        tf.keras.Sequential
            A sequential model with the following layers:
            - LSTM layer with 64 units and return_sequences=True
            - LSTM layer with 32 units and return_sequences=False
            - Dense layer with num_outputs units and softmax activation
            - Reshape layer to reshape the output to (None, 1, num_outputs)
        """
        logging.debug(
            "Bulding avalanche prediction model"
            / "with the following parameters:"
            / f"Number of outputs: {num_outputs}, Input shape: {input_shape}",
        )
        model = tf.keras.Sequential(
            [
                tf.keras.layers.LSTM(
                    64, return_sequences=True, input_shape=input_shape
                ),
                tf.keras.layers.LSTM(32, return_sequences=False),
                tf.keras.layers.Dense(units=num_outputs, activation="softmax"),
                tf.keras.layers.Reshape(
                    (1, num_outputs)
                ),  # Reshape the output to (None, 1, output_shape)
            ]
        )

        return model

    def train_model(
        self,
        train_data: pd.DataFrame,
        validation_data: pd.DataFrame,
        max_epochs: int = 20,
        patience: int = 2,
    ):
        """
        Train the avalanche prediction model.

        Parameters
        ----------
        train_data : pd.DataFrame
            Training data
        validation_data : pd.DataFrame
            Validation data
        max_epochs : int, optional
            Maximum number of epochs, by default 20
        patience : int, optional
            Patience for early stopping, by default 2

        Returns
        -------
        tf.keras.callbacks.History
            History of the training
        """
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=patience, mode="min"
        )
        self.model.compile(
            loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
            optimizer=tf.keras.optimizers.Adam(),
            metrics=["accuracy"],
        )
        history = self._model.fit(
            train_data,
            epochs=max_epochs,
            validation_data=validation_data,
            callbacks=[early_stopping],
        )
        return history

    def load_model(self, model_path: str) -> tf.keras.Sequential:
        """
        Load a model from a path.

        Parameters
        ----------
        model_path : str
            Path to the model to load

        Returns
        -------
        tf.keras.Sequential
            Loaded model
        """
        logging.debug(f"Loading avalanche prediction model from {model_path}")
        model = tf.keras.models.load_model(model_path)
        return model

    def predict(self, data: pd.DataFrame):
        """
        Predict the avalanche warning for a given data.

        Parameters
        ----------
        data : pd.DataFrame
            Data to predict the avalanche warning for

        Returns
        -------
        np.array
            Predicted labels
        np.array
            Prediction probabilities
        """
        logging.debug(f"Predicting avalanche warning for {data}")
        prediction = self.model.predict(data)
        predicted_labels = np.argmax(prediction[:, 0], axis=-1)
        prediction_probabilities = np.max(prediction[:, 0], axis=-1)
        return predicted_labels, prediction_probabilities
