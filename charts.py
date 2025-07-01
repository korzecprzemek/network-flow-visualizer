import plotly.express as px
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import numpy as np
from auxiliary import *



def protocol_pie_chart(df):
    protocol_counts = df['Protocol'].value_counts().reset_index()
    protocol_counts.columns = ['Protocol', 'Count']
    protocol_counts = protocol_counts.astype({'Count': int})


    fig = px.pie(protocol_counts,names='Protocol', values='Count', title='Protocol Breakdown')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig.to_html(full_html=False) 

def top_sources_chart(df, top_n=10):
    df_filtered = filter_top_nodes(df,top_n=top_n,column='Source',group_rest = False)
    top_sources = df['Source'].value_counts().head(top_n).reset_index()
    top_sources.columns = ['Source', 'Count']
    top_sources = top_sources.astype({'Count': int})
    
    fig = px.bar(top_sources, x='Source', y='Count', title=f'Top {top_n} Source Devices by Packet Count')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    return fig.to_html(full_html=False)

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
def mac_connection_graph(df,top_n=10):
    top_nodes = get_top_nodes(df, top_n)
    df_filtered = filter_by_top_nodes(df, top_nodes, keep_others=False)

    df = df[(df['Source'] != 'Other') | (df['Destination'] != 'Other')]
    G = nx.from_pandas_edgelist(df_filtered, source="Source", target="Destination", create_using=nx.DiGraph())

    pos = nx.spring_layout(G, seed=42)

    edge_x = []
    edge_y = []
    for src, dst in G.edges():
        x0, y0 = pos[src]
        x1, y1 = pos[dst]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    node_x = []
    node_y = []
    node_text = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition='top center',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color='lightblue',
            size=10,
            line_width=2
        )
    )
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=dict(text='MAC Address Connection Graph', font=dict(size=16)),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    ))

    return fig.to_html(full_html=False)

def dataframe_table_html(df, max_rows=100, sort_by=None, ascending=True, start=0):
    """Zwraca HTML z tabelą z danych DataFrame (paginacja, sortowanie)."""
    if df.empty:
        return "<p>Brak danych do wyświetlenia.</p>"
    if sort_by and sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=ascending)
    table_html = "<h2>Dane z CSV</h2><table border='1'><thead><tr>"
    for col in df.columns:
        table_html += (
            f"<th>{col} "
            f"<a href='?sort_by={col}&ascending=1'>&uarr;</a> "
            f"<a href='?sort_by={col}&ascending=0'>&darr;</a>"
            f"</th>"
        )
    table_html += "</tr></thead><tbody>"
    for _, row in df.iloc[start:start+max_rows].iterrows():
        table_html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
    table_html += "</tbody></table>"
    table_html += f"<p>Wyświetlono wiersze {start+1} - {min(start+max_rows, len(df))} z {len(df)}.</p>"
    return table_html


def heatmap_packet_activity(df, time_bin='1Min'):
    if 'Time' not in df.columns:
        return "<p style='color:red;'>⚠️ CSV must include 'Time' column.</p>"

    try:
        # Zamień Time na timedelta (czas od początku przechwytywania)
        df['TimeDelta'] = pd.to_timedelta(df['Time'], unit='s')
        df['Timestamp'] = pd.to_datetime('1970-01-01') + df['TimeDelta']
    except Exception as e:
        return f"<p style='color:red;'>⚠️ Error parsing time: {e}</p>"

    # Zaokrąglij czas do siatki (np. 1 minuta)
    df['TimeRounded'] = df['Timestamp'].dt.floor(time_bin)

    # Tworzymy kolumnę pomocniczą: sekundy w minucie
    df['Second'] = df['Timestamp'].dt.second
    df['Minute'] = df['Timestamp'].dt.strftime('%H:%M')

    # Tworzenie tabeli przestawnej: liczba pakietów [Minute x Second]
    pivot = df.pivot_table(index='Minute', columns='Second', values='No.', aggfunc='count', fill_value=0)

    # Upewnij się, że wszystkie kolumny (0–59 sek) istnieją
    for sec in range(60):
        if sec not in pivot.columns:
            pivot[sec] = 0
    pivot = pivot[sorted(pivot.columns)]

    # Dane do heatmapy
    z = pivot.values
    x = [f"{sec:02d}" for sec in pivot.columns]  # sekundy
    y = pivot.index.tolist()  # minuty (godzina:minuta)

    # Tworzenie wykresu
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=x,
        y=y,
        colorscale='YlOrRd',
        colorbar=dict(title='Liczba pakietów'),
        hovertemplate='Czas: %{y}:%{x}<br>Liczba pakietów: %{z}<extra></extra>'
    ))

    fig.update_layout(
        title='Heatmapa aktywności sieciowej (minuta vs sekunda)',
        xaxis_title='Sekunda',
        yaxis_title='Godzina:Minuta',
        autosize=True,
        margin=dict(l=40, r=40, t=80, b=40),
        height=500
    )

    return fig.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})

def packet_length_distribution(df, bin_size=50):
    if 'Length' not in df.columns:
        return "<p style='color:red;'>⚠️ CSV must include 'Length' column.</p>"

    try:
        df['Length'] = pd.to_numeric(df['Length'], errors='coerce')
        df = df.dropna(subset=['Length'])
    except Exception as e:
        return f"<p style='color:red;'>⚠️ Error parsing Length: {e}</p>"

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df['Length'],
        xbins=dict(start=0, end=df['Length'].max(), size=bin_size),
        marker_color='indianred',
        opacity=0.75
    ))

    fig.update_layout(
        title='Rozkład długości pakietów',
        xaxis_title='Długość pakietu (bajty)',
        yaxis_title='Liczba pakietów',
        bargap=0.05,
        bargroupgap=0.1,
        autosize=True,
        margin=dict(l=40, r=40, t=80, b=40),
        height=500
    )

    return fig.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})


def source_ip_entropy(df, time_bin='1Min'):
    if 'Time' not in df.columns or 'Source' not in df.columns:
        return "<p style='color:red;'>⚠️ CSV must include 'Time' and 'Source' columns.</p>"

    try:
        # Czas jako datetime
        df['TimeDelta'] = pd.to_timedelta(df['Time'], unit='s')
        df['Timestamp'] = pd.to_datetime('1970-01-01') + df['TimeDelta']
        df['TimeRounded'] = df['Timestamp'].dt.floor(time_bin)
    except Exception as e:
        return f"<p style='color:red;'>⚠️ Error parsing time: {e}</p>"

    # Grupa po przedziałach czasowych
    entropy_data = []

    for time_bin_value, group in df.groupby('TimeRounded'):
        counts = group['Source'].value_counts()
        probs = counts / counts.sum()
        entropy = -(probs * np.log2(probs)).sum()
        entropy_data.append((time_bin_value, entropy))

    if not entropy_data:
        return "<p style='color:red;'>⚠️ No entropy data available after processing.</p>"

    times, entropies = zip(*entropy_data)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times,
        y=entropies,
        mode='lines+markers',
        line=dict(color='teal'),
        name='Entropia IP źródłowych',
        hovertemplate='Czas: %{x}<br>Entropia: %{y:.3f}<extra></extra>'
    ))

    fig.update_layout(
        title='Entropia adresów źródłowych IP w czasie',
        xaxis_title='Czas',
        yaxis_title='Entropia (bitów)',
        autosize=True,
        margin=dict(l=40, r=40, t=80, b=40),
        height=500
    )

    return fig.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})