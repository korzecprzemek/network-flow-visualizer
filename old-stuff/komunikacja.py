import pandas as pd
import plotly.express as px
import os

def generuj_wykres_html(nazwa_pliku_csv, nazwa_wyjscia_html="wykres_komunikacji.html"):
    # Wczytanie danych z pliku CSV
    df = pd.read_csv(nazwa_pliku_csv)

    # Tworzenie kolumny z opisem połączenia
    df['Connection'] = df['Source'] + ' → ' + df['Destination']

    # Mapowanie połączeń na ID
    connection_mapping = {conn: idx for idx, conn in enumerate(df['Connection'].unique())}
    df['Connection_ID'] = df['Connection'].map(connection_mapping)

    # Tworzenie dodatkowej kolumny do wyświetlania po najechaniu
    df['hover_text'] = (
        'ID połączenia: ' + df['Connection_ID'].astype(str) + '<br>' +
        'Połączenie: ' + df['Connection'] + '<br>' +
        'Czas: ' + df['Time'].astype(str) + ' s'
    )

    # Tworzenie wykresu
    fig = px.scatter(
        df,
        x="Time",
        y="Connection_ID",
        hover_data={"hover_text": True},
        labels={"Time": "Czas [s]", "Connection_ID": "ID Połączenia"},
        title="Interaktywny wykres komunikacji między węzłami (z ID połączeń)"
    )

    # Dostosowanie wyglądu
    fig.update_traces(marker=dict(size=6, opacity=0.6), selector=dict(mode='markers'))
    fig.update_layout(
        hovermode="closest",
        height=600
    )

    # Zapis wykresu do pliku HTML
    fig.write_html(nazwa_wyjscia_html)
    print(f"Wykres zapisany jako: {os.path.abspath(nazwa_wyjscia_html)}")

# Przykładne wywołanie:
if __name__ == "__main__":
    generuj_wykres_html("Test.csv")
