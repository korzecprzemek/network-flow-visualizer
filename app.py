from flask import Flask, request, render_template, redirect, url_for, session
import pandas as pd
import os
import plotly.express as px
from charts import *

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'tajny_klucz'  # wymagane do użycia sesji

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    charts = {}
    sort_by = request.args.get('sort_by')
    ascending = request.args.get('ascending', '1') == '1'
    df = None

    if request.method == 'POST':
        file = request.files['file']
        if file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            session['csv_file'] = filepath  # zapisz ścieżkę w sesji

    csv_file = session.get('csv_file')
    if csv_file and os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        charts['protocol_pie'] = protocol_pie_chart(df)
        charts['top_sources_bar'] = top_sources_chart(df)
        charts['jitter_by_connection'] = jitter_by_connection_chart(df)
        charts['mac_addresses'] = mac_connection_graph(df)
        charts['list'] = dataframe_table_html(df, max_rows=10, sort_by=sort_by, ascending=ascending)
        charts['heatmap'] = heatmap_packet_activity(df, time_bin='1Min')
        charts['length_distribution'] = packet_length_distribution(df)
        charts['ip_entropy'] = source_ip_entropy(df)

    return render_template('index.html', charts=charts)

@app.route('/csv', methods=['GET', 'POST'])
def show_csv():
    sort_by = request.args.get('sort_by')
    ascending = request.args.get('ascending', '1') == '1'
    start = int(request.args.get('start', 0))
    max_rows = 100
    filter_value = request.args.get('filter_value', '')
    filter_column = request.args.get('filter_column', '')
    df = None
    table_html = ""
    if request.method == 'POST':
        file = request.files['file']
        if file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            session['csv_file'] = filepath

    csv_file = session.get('csv_file')
    if csv_file and os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        # Filtrowanie
        if filter_value and filter_column and filter_column in df.columns:
            df = df[df[filter_column].astype(str).str.contains(filter_value, case=False, na=False)]
        table_html = dataframe_table_html(
            df, max_rows=max_rows, sort_by=sort_by, ascending=ascending, start=start
        )

    next_start = start + max_rows
    prev_start = max(0, start - max_rows)
    total_rows = len(df) if df is not None else 0

    # Przekaż listę kolumn do szablonu
    columns = df.columns.tolist() if df is not None else []

    return render_template(
        'csv.html',
        table_html=table_html,
        start=start,
        max_rows=max_rows,
        next_start=next_start,
        prev_start=prev_start,
        total_rows=total_rows,
        filter_value=filter_value,
        filter_column=filter_column,
        columns=columns
    )




if __name__ == '__main__':
    app.run(debug=True, port=3000)