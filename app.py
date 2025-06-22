from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import os
import plotly.express as px
from charts import *

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/', methods=['GET', 'POST'])
def index():
    charts = {}
    chart_html = None
    if request.method == 'POST':
        file = request.files['file']
        if file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            df = pd.read_csv(filepath)
            charts['protocol_pie'] = protocol_pie_chart(df)
            charts['top_sources_bar'] = top_sources_chart(df)
            charts['jitter_by_connection'] = jitter_by_connection_chart(df)
            charts['mac_addresses'] = mac_connection_graph(df)
            # Basic chart: first 2 numeric columns
            #Line chart
    return render_template('index.html', charts=charts)
if __name__ == '__main__':
    app.run(debug=True, port=3000)

