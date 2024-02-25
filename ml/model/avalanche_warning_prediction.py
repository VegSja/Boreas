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
        self._model = self.load_model(model_path)

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

    def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        features = ['temp_2m_max', 'temp_2m_min', 'temp_2m_mean', 'rain_sum',
               'snowfall_sum', 'windspeed_10m_max', 'windgusts_10m_max',
               'winddirection_10m_dominant']
        target = "SequenceDangerLevel"
        data = data[features]
        return data

    def predict(self, sequence: pd.DataFrame):
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
        logging.debug(f"Predicting avalanche warning for sequence")
        prediction = self._model.predict(sequence.values.reshape(1, 15, 8))
        predicted_labels = np.argmax(prediction[0], axis=-1) + 1
        prediction_probabilities = prediction[0]
        return predicted_labels, prediction_probabilities
