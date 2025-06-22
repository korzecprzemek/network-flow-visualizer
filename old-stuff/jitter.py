import pandas as pd
import plotly.graph_objects as go
import os

def generuj_interaktywny_jitter(nazwa_pliku_csv, nazwa_wyjscia_html="jitter_interaktywny.html"):
    # Wczytanie danych
    df = pd.read_csv(nazwa_pliku_csv)
    df['Connection'] = df['Source'] + ' → ' + df['Destination']

    # Top N połączeń do analizy
    top_n = 10
    top_connections = df['Connection'].value_counts().head(top_n).index.tolist()

    # Przygotowanie danych jittera dla każdego połączenia
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
                'Czas: %{x:.6f} s<br>' +
                'Jitter: %{y:.6f} s<br>' +
                'Połączenie: ' + conn
        )
        jitter_traces.append(trace)

        # Przycisk do filtrowania
        button = dict(
            label=conn,
            method="update",
            args=[
                {"visible": [i == idx for i in range(len(top_connections))]},
                {"title": f"Jitter w czasie dla połączenia: {conn}"}
            ]
        )
        buttons.append(button)

    # Tworzenie figury z przyciskami
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
        title=f"Jitter w czasie dla połączeń (TOP {top_n})",
        xaxis_title="Czas [s]",
        yaxis_title="Jitter [s]",
        hovermode="closest",
        height=600,
        width=1400
    )
    #fig.update_xaxes(range=[0, 1])


    # Zapis do HTML
    fig.write_html(nazwa_wyjscia_html)
    print(f"Wykres zapisany jako: {os.path.abspath(nazwa_wyjscia_html)}")

# Przykładne wywołanie
if __name__ == "__main__":
    generuj_interaktywny_jitter("Test.csv")