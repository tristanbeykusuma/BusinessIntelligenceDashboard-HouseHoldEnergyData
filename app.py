import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

data = (
    pd.read_csv("D202.csv")
    .drop(columns=['NOTES'])
)
data["NEW_DATE"] = pd.to_datetime(data['DATE'] + " " + data['START TIME'])
data_daily = (
    pd.read_csv("project_data.csv")
    .groupby(['DAY']).agg({'USAGE':'sum'})
)
data_daily['DAY'] = data_daily.index
data_daily.rename(columns={'USAGE':'USAGE'}, inplace=True)

external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Energy Corporation Business Intelligence Dashboard"

app.layout = html.Div(
    children=[
        html.H1('Energy Corporation Business Intelligence Dashboard - House Hold Energy Data'),
         html.P(
            children=(
                "Analyze the usage of household energy in a time series"
            ),
        ),
        dcc.Dropdown(['Data Plot', 'Data Correlation', 'Rolling Calculation', 'Model Predictions'],
            'Data Plot',
            id='dropdown'
        ),
        html.Div(id='display-value'),
    ]
)

@callback(Output('display-value', 'children'), Input('dropdown', 'value'))
def display_value(value):
    if value=='Data Plot':
        return [dcc.Graph(
            figure={
                "data": [
                    {
                        "x": data_daily["DAY"],
                        "y": data_daily["USAGE"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Daily Usage Energy Aggregate Sum"},
            },
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": data["NEW_DATE"],
                        "y": data["USAGE"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Household Energy Usage"},
            },
        ),]
    elif value=='Data Correlation':
       return [html.Img(id='autocorrelation', src='assets/autocorrelation.png', className='myImg', n_clicks_timestamp=0),
               html.Img(id='energycorrelation', src='assets/energy_correlation.png', className='myImg', n_clicks_timestamp=0),
               html.Img(id='energycorrelation80', src='assets/energy_correlation80.png', className='myImg', n_clicks_timestamp=0), ]
    elif value=='Rolling Calculation':
       return [html.Img(id='rollingcalc', src='assets/rolling_calculation.png', className='myImg', n_clicks_timestamp=0),
               html.Img(id='decompose', src='assets/seasonal_decompose.png', className='myImg', n_clicks_timestamp=0),]
    elif value=='Model Predictions':
       return [html.H4('Autoregressive Integrated Moving Average Model'),
               html.Img(id='rollingcalc', src='assets/arima_pred.png', className='myImg', n_clicks_timestamp=0),
               html.H4('LSTM Sequential Model'),
               html.Img(id='decompose', src='assets/lstm_pred.png', className='myImg', n_clicks_timestamp=0),]


if __name__ == "__main__":
    app.run_server(debug=True)