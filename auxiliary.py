import plotly.express as px
import pandas as pd


def compute_jitter(df):
    if 'Time' not in df.columns or 'Source' not in df.columns:
        return df  # Can't calculate without these columns

    # Sort and calculate inter-packet arrival times per Source
    df = df.sort_values(['Source', 'Time'])
    df['InterArrival'] = df.groupby('Source')['Time'].diff()

    # Jitter is the change in interarrival time (i.e. how much timing varies)
    df['Jitter'] = df.groupby('Source')['InterArrival'].diff().abs()

    return df
