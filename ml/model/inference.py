from SequenceGenerator import SequenceGenerator 
from avalanche_warning_prediction import AvalancheWarningPrediction 
import os
import pandas as pd

script_dir = os.path.dirname(os.path.realpath(__file__))
relative_filepath = os.path.join(script_dir, "../../notebooks/weather_warning_combined.csv")
df = pd.read_csv(relative_filepath)

sequence_generator = SequenceGenerator(telescope=15)
df = sequence_generator.prepare_data(df)
sequence = sequence_generator.build_recent_sequence(df, region_id=3003)

# Load the model
model = AvalancheWarningPrediction(model_path="simple_lstm.keras")
processed_sequence = model.prepare_data(sequence)
predicted_label, prediction_probs = model.predict(processed_sequence) 

print(f"Predicted labels: {predicted_label}")
print(f"Prediction probabilities: {prediction_probs}")
