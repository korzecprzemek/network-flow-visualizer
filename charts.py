import plotly.express as px
import pandas as pd
from auxiliary import *



def protocol_pie_chart(df):
    protocol_counts = df['Protocol'].value_counts().reset_index()
    protocol_counts.columns = ['Protocol', 'Count']
    protocol_counts = protocol_counts.astype({'Count': int})


    fig = px.pie(protocol_counts,names='Protocol', values='Count', title='Protocol Breakdown')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig.to_html(full_html=False) 

def top_sources_chart(df, top_n=10):
    top_sources = df['Source'].value_counts().head(top_n).reset_index()
    top_sources.columns = ['Source', 'Count']
    top_sources = top_sources.astype({'Count': int})
    
    fig = px.bar(top_sources, x='Source', y='Count', title=f'Top {top_n} Source Devices by Packet Count')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    return fig.to_html(full_html=False)

import plotly.graph_objects as go

def jitter_by_connection_chart(df, top_n=10):
    if 'Time' not in df.columns or 'Source' not in df.columns or 'Destination' not in df.columns:
        return "<p style='color:red;'>⚠️ CSV must include 'Time', 'Source', and 'Destination' columns.</p>"

    df['Connection'] = df['Source'] + ' → ' + df['Destination']
    top_connections = df['Connection'].value_counts().head(top_n).index.tolist()

    jitter_traces = []
    buttons = []

    for idx, conn in enumerate(top_connections):
        df_conn = df[df['Connection'] == conn].copy().sort_values(by='Time')
        df_conn['InterArrival'] = df_conn['Time'].diff()
        mean_interval = df_conn['InterArrival'].mean()
        df_conn['Jitter'] = (df_conn['InterArrival'] - mean_interval).abs()

        trace = go.Scatter(
            x=df_conn['Time'],
            y=df_conn['Jitter'],
            mode='lines+markers',
            name=conn,
            visible=(idx == 0),
            hovertemplate=
                'Time: %{x:.6f} s<br>' +
                'Jitter: %{y:.6f} s<br>' +
                'Connection: ' + conn
        )
        jitter_traces.append(trace)

        button = dict(
            label=conn,
            method="update",
            args=[
                {"visible": [i == idx for i in range(len(top_connections))]},
                {"title": f"Jitter over time for connection: {conn}"}
            ]
        )
        buttons.append(button)

    fig = go.Figure(data=jitter_traces)
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=buttons,
                x=1.05,
                y=1,
                xanchor='left',
                yanchor='top',
                showactive=True
            )
        ],
        title=f"Jitter over time for Top {top_n} Connections",
        xaxis_title="Time [s]",
        yaxis_title="Jitter [s]",
        hovermode="closest",
        autosize=True,
        height=500,
        margin=dict(l=40,r=40,t=80,b=40)
    )

    return fig.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})


