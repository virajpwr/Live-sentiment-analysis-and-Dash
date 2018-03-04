import sqlite3
import pandas as pd
import os
import dash
from dash.dependencies import Output, Event, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque

os.chdir('G:\\sentiment_analysis\\dataset')
app = dash.Dash(__name__)
app.layout = html.Div(
    [   html.H2('Live Twitter Sentiment'),
        dcc.Input(id='sentiment_term', value='stormemma', type='text'),
        dcc.Graph(id='live-graph', animate=False),
        dcc.Interval(
            id='graph-update',
            interval=1*1000
        ),

    ]
)


@app.callback(Output('live-graph', 'figure'),
              [Input(component_id='sentiment_term', component_property='value')],
              events=[Event('graph-update', 'interval')])

def update_graph_scatter(sentiment_term):
    try:
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 200", conn, params=('%' + sentiment_term + '%',))
        df.sort_values('unix', inplace = True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/2)).mean()
        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)
        df.dropna(inplace=True)
        df= df.resample('30s').mean
        X = df.index[-100:]
        Y = df.sentiment_smoothed[-100:]
        
        data = plotly.graph_objs.Scatter(
                x = X,
                y = Y,
                name = 'Scatter',
                mode = 'line+markers'
                )
        return{'data':[data],
               'layout' : go.Layout(
                       xaxis = dict(range=[min(X), max(X)]),
                       yaxis = dict(range=[min(Y), max(Y)]),
                       title='Term: {}'.format(sentiment_term))}
               
               
    except Exception as e:
        with open('error.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')

if __name__ == '__main__':
    app.run_server(debug=False)
