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
def filter_top_nodes(df, top_n=20, group_rest=True, column='Source'):
    top_nodes = df[column].value_counts().nlargest(top_n).index

    if group_rest:
        df[column] = df[column].apply(lambda x: x if x in top_nodes else 'Other')

    return df[df[column] != 'Other'] if not group_rest else df

def filter_top_nodes_bidirectional(df, top_n=20):
    all_nodes = pd.concat([df['Source'], df['Destination']])
    top_nodes = all_nodes.value_counts().nlargest(top_n).index

    return df[df['Source'].isin(top_nodes) | df['Destination'].isin(top_nodes)]
def filter_by_top_nodes(df, top_nodes, keep_others=False):
    df = df.copy()
    if keep_others:
        df['Source'] = df['Source'].apply(lambda x: x if x in top_nodes else 'Other')
        df['Destination'] = df['Destination'].apply(lambda x: x if x in top_nodes else 'Other')
        return df
    else:
        return df[df['Source'].isin(top_nodes) | df['Destination'].isin(top_nodes)]
def get_top_connections(df, top_n=10):
    df = df.copy()
    df['Connection'] = df['Source'] + ' → ' + df['Destination']
    return df['Connection'].value_counts().nlargest(top_n).index.tolist()
def get_top_nodes(df, top_n=20):
    all_nodes = pd.concat([df['Source'], df['Destination']])
    return all_nodes.value_counts().nlargest(top_n).index.tolist()


