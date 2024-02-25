import logging
import pandas as pd
import numpy as np
from tqdm import tqdm

class SequenceGenerator:
    def __init__(self, telescope=15):
        self.telescope = telescope

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df["Time"] = pd.to_datetime(df["Time"])
        df = df.drop(columns=["region_name"])
        return df

    def build_recent_sequence(self, df, region_id):
        # Filter the DataFrame for the specified region
        region_data = df[df['region_id'] == region_id].copy()
        region_data = self.build_sequences(region_data)
        
        # Check if the size of the region_data is smaller than telescope
        if len(region_data) < self.telescope:
            raise ValueError(f"Insufficient data for region {region_id} to create a sequence of length {self.telescope}.")
        
        # Sort the data by 'Time' in descending order to get the most recent data first
        region_data.sort_values(by='Time', ascending=False, inplace=True)
        
        # Take the first 'telescope' rows to get the most recent sequence
        recent_sequence = region_data.head(self.telescope).copy()
        
        return recent_sequence

    def build_sequences(self, df):
        edit_df = df.copy(deep=True)
        # Sort the DataFrame by 'region_id' and 'Time'
        edit_df.sort_values(by=['region_id', 'Time'], inplace=True)
        
        # Create a list to store the resulting sequences
        sequences = []
        
        # Iterate through the DataFrame to create sequences
        for region_id, region_group in tqdm(edit_df.groupby('region_id')):
            for i in range(len(region_group) - (self.telescope-1)):
                sequence_data = region_group.iloc[i:i+self.telescope].copy()
                end_date = sequence_data['Time'].max()
                
                # Check for consecutive days within the sequence
                date_diff = sequence_data['Time'].diff().fillna(pd.Timedelta(days=1))
                if (date_diff == pd.Timedelta(days=1)).all():
                    sequence_data['DayForDanger'] = end_date
                    danger_level = sequence_data[sequence_data['Time'] == end_date]["DangerLevel"].values[0]
                    sequence_data['SequenceDangerLevel'] = danger_level
                    sequence_data['SequenceID'] = f"{region_id}-{end_date}"
                    sequences.append(sequence_data)
        
        # Concatenate the sequences into a new DataFrame
        sequences_df = pd.concat(sequences)
        
        # Reset the index of the resulting DataFrame if needed
        sequences_df.reset_index(drop=True, inplace=True)

        logging.debug(f"Created {sequences_df["SequenceID"].nunique()} sequences.")

        return sequences_df
