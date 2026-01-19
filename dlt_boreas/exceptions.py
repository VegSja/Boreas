"""Custom exceptions for the dlt pipeline."""


class PipelineDataError(Exception):
    """Base exception for data-related errors in the pipeline."""
    pass


class WeatherAPIError(PipelineDataError):
    """Exception raised when weather API requests fail."""
    pass


class AvalancheAPIError(PipelineDataError):
    """Exception raised when avalanche API requests fail."""
    pass


class DataValidationError(PipelineDataError):
    """Exception raised when data validation fails."""
    pass