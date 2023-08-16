"""Contais class for making windows used in LSTM."""

import numpy as np
import tensorflow as tf


class WindowGenerator:
    """Class for making windows used in timeseries."""

    def __init__(
        self,
        input_width,
        label_width,
        shift,
        train_df,
        val_df,
        test_df,
        label_columns=None,
    ):
        """Initialize the WindowGenerator instance with data and window \
                    parameters.

        Args:
            input_width (int): Width of the input window.
            label_width (int): Width of the label window.
            shift (int): Shift between successive windows.
            train_df (pd.DataFrame): DataFrame containing training data.
            val_df (pd.DataFrame): DataFrame containing validation data.
            test_df (pd.DataFrame): DataFrame containing test data.
            label_columns (list, optional): List of label column names.
        """
        # Store the raw data.
        self.train_df = train_df
        self.val_df = val_df
        self.test_df = test_df
        self.number_of_classes = 4

        # Work out the label column indices.
        self.label_columns = label_columns
        if label_columns is not None:
            self.label_columns_indices = {
                name: i for i, name in enumerate(label_columns)
            }
        self.column_indices = {name: i for i, name in enumerate(train_df.columns)}

        # Work out the window parameters.
        self.input_width = input_width
        self.label_width = label_width
        self.shift = shift

        self.total_window_size = input_width + shift

        self.input_slice = slice(0, input_width)
        self.input_indices = np.arange(self.total_window_size)[self.input_slice]

        self.label_start = self.total_window_size - self.label_width
        self.labels_slice = slice(self.label_start, None)
        self.label_indices = np.arange(self.total_window_size)[self.labels_slice]

        # Given a list of consecutive inputs, the split_window method will
        # convert them to a window of inputs and a window of labels.
        # but this split_window function also handles the label_columns so it
        # can be used for both the single output and multi-output examples.

    def split_window(self, features):
        """Convert a list of consecutive inputs to a window of inputs \
        and labels.

        Args:
            features (tf.Tensor): Input data tensor.

        Returns:
            tuple: A tuple containing inputs and labels.
        """
        inputs = features[:, self.input_slice, :]
        labels = features[:, self.labels_slice, :]

        if self.label_columns is not None:
            # Get the label column indices
            label_indices = [self.column_indices[name] for name in self.label_columns]

            # Remove extra dimension and convert labels to integer values
            labels = tf.cast(tf.gather(labels, label_indices, axis=-1), tf.int32)

            # One-hot encode each label column separately
            labels_list = [
                tf.one_hot(labels[:, :, idx], depth=self.number_of_classes)
                for idx in range(labels.shape[-1])
            ]

            # Concatenate the one-hot encoded labels along the last dimension
            labels = tf.concat(labels_list, axis=-1)

        # Slicing doesn't preserve static shape information, so set the shapes
        # manually. This way the `tf.data.Datasets` are easier to inspect.
        inputs.set_shape([None, self.input_width, None])
        labels.set_shape([None, self.label_width, self.number_of_classes])

        return inputs, labels

    def make_dataset(self, data):
        """Create a TensorFlow Dataset from the input data.

        Args:
            data (np.array): Input data as a NumPy array.

        Returns:
            tf.data.Dataset: A TensorFlow Dataset containing inputs and labels.
        """
        data = np.array(data, dtype=np.float32)
        ds = tf.keras.utils.timeseries_dataset_from_array(
            data=data,
            targets=None,
            sequence_length=self.total_window_size,
            sequence_stride=1,
            shuffle=True,
            batch_size=32,
        )

        ds = ds.map(self.split_window)

        return ds

    @property
    def train(self):
        """Create a TensorFlow Dataset for training data.

        Returns:
            tf.data.Dataset: A TensorFlow Dataset for training.
        """
        return self.make_dataset(self.train_df)

    @property
    def val(self):
        """Create a TensorFlow Dataset for validation data.

        Returns:
            tf.data.Dataset: A TensorFlow Dataset for validation.
        """
        return self.make_dataset(self.val_df)

    @property
    def test(self):
        """Create a TensorFlow Dataset for test data.

        Returns:
            tf.data.Dataset: A TensorFlow Dataset for test.
        """
        return self.make_dataset(self.test_df)

    @property
    def example(self):
        """Get and cache an example batch of `inputs, labels` for plotting."""
        result = getattr(self, "_example", None)
        if result is None:
            # No example batch was found, so get one from the `.train` dataset
            result = next(iter(self.train))
            # And cache it for next time
            self._example = result
        return result

    @property
    def train_labels(self):
        """Get the training labels."""
        return self.train_df[self.label_columns].to_numpy()

    @property
    def val_labels(self):
        """Get the validation labels."""
        return self.val_df[self.label_columns].to_numpy()

    @property
    def test_labels(self):
        """Get the test labels."""
        return self.test_df[self.label_columns].to_numpy()

    def __repr__(self):
        """Return a string representation of the WindowGenerator instance."""
        return "\n".join(
            [
                f"Total window size: {self.total_window_size}",
                f"Input indices: {self.input_indices}",
                f"Label indices: {self.label_indices}",
                f"Label column name(s): {self.label_columns}",
            ]
        )
