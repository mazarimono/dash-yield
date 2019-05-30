import dash  
import dash_core_components as dcc 
import dash_html_components as html 
import pandas as pd 
import pandas_datareader.data as web 
import plotly.graph_objs as go 
from datetime import datetime 

import os 
import json 

# Data 
start = datetime(2000, 1, 1)
today = datetime.today()

df = web.DataReader(['DFF', 'DGS3MO', 'DGS2', 'DGS5', 'DGS10', 'DGS30', 'TEDRATE', 'T10YIE', 'T10Y3M', 'T10Y2Y', 'BAA10Y'], 'fred', start, today)
df['date'] = df.index
df.columns =['ffrate', '3mT', '2yT', '5yT', '10yT', '30yT', 'tedspread', 'breakeven10Y', '3m10ySpread', '2y10ySpread', 'baa10ySpread', 'date']
df['30yT'] = df['30yT'].fillna(0)

yieldOnly = df[['date', 'ffrate', '3mT', '2yT', '5yT', '10yT', '30yT']].dropna()
spreads = df[['date', 'tedspread', '3m10ySpread', '2y10ySpread', 'baa10ySpread']].dropna()

app = dash.Dash(__name__)

server = app.server 

app.layout = html.Div([
    html.Div([
        html.H1('US Yield Data', style ={'textAlign': 'center'}),
        dcc.DatePickerRange(
            id = 'date-picker',
            minimum_nights = 5,
            clearable = True,
            start_date = datetime(2000, 1, 1),
            style = {'display': 'block'},
        ),
        html.Div([
            dcc.Graph(id = 'historical-left'),
            # html.H3('見たい範囲を上の日付ピッカー、もしくはマウスのドラッグで選択できます', style={'textAlign': 'center'}),
            ], style = {'width': '49%', 'display': 'inline-block'}),
        html.Div([
            html.H1(id='test'),
            dcc.Graph(id = 'yield-curve-right'),
            # html.H3('左の米国の主要金利のグラフでマウスホバーした地点のイールドカーブが表示できます。', style={'textAlign': 'center'}),
        ], style = {'width': '49%','display': 'inline-block'}),
    ], style = {'height': '1000', 'margin': '2%'}),
    html.Div([
        html.Div([
            html.H1('Major Yeild Spreads')
        ], style={'textAlign': 'center'}),
        html.Div([
            dcc.Dropdown(
                id = 'spread-dropdown',
                options = [{'label': i, 'value': i} for i in spreads.columns[1:]],
                value = 'tedspread'
            )
        ], style = {'width': '30%', 'margin': '2% auto 2%'}),
        html.Div([
            dcc.Graph(id='spreadGraph'),
        ], style = {'width': '60%', 'margin': '0 auto 0'}),
    ]),
])

@app.callback(dash.dependencies.Output('historical-left', 'figure'),
            [dash.dependencies.Input('date-picker', 'start_date'),
            dash.dependencies.Input('date-picker', 'end_date')])
def makeYieldHist(start_date, end_date):
    histdf = yieldOnly[start_date: end_date]
    histdf = pd.melt(histdf, id_vars='date', value_vars=['ffrate', '3mT', '2yT', '5yT', '10yT', '30yT'])
    return {
        'data': [
            go.Scatter(
                x = histdf[histdf['variable'] == i]['date'],
                y = histdf[histdf['variable'] == i]['value'],
                name = i
            ) for i in histdf['variable'].unique()
        ],
        'layout':{
            'title': 'US Yeild'
        }
    }

@app.callback(dash.dependencies.Output('yield-curve-right', 'figure'),
            [dash.dependencies.Input('historical-left', 'hoverData')])
def makeYieldCurve(hoverData):
    try:
        selectedDate = hoverData['points'][0]['x']
    except:
        selectedDate = '2000-12-18'
    
    selecteddf = yieldOnly[yieldOnly['date'] == selectedDate]
    return {
        'data':[
            go.Parcoords(
                line = dict(color='blue'),
                dimensions = list([
                    dict(range = [0, 7],
                        label = 'FF Rate', values = selecteddf['ffrate']
                    ),
                    dict(range = [0, 7],
                        label = '3M Treasury', values = selecteddf['3mT']
                    ),
                    dict(range = [0, 7],
                        label = '2Y Treasury', values = selecteddf['2yT']
                    ),
                    dict(range = [0, 7],
                        label = '5Y Treasury', values = selecteddf['5yT']
                    ),
                    dict(range = [0, 7],
                        label = '10Y Treasury', values = selecteddf['10yT']
                    ),
                    dict(range = [0, 7],
                        label = '30Y Treasury', values = selecteddf['30yT']
                    ),
                ])
            )
        ],
        'layout':{
            'title': 'Yield Curve Date: {}'.format(selectedDate)
        }
    }

@app.callback(dash.dependencies.Output('spreadGraph', 'figure'),
            [dash.dependencies.Input('spread-dropdown', 'value')])
def spreadGraph(selectedvalue):
    dff = spreads[['date', selectedvalue]]
    return {
        'data': [go.Scatter(
            x = dff['date'], 
            y = dff[selectedvalue],
            name = selectedvalue
        )
        ]
    }

if __name__ == '__main__':
    app.run_server(debug=True)