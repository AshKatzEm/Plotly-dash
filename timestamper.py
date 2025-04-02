from config import config
import pandas as pd
from connect import connect
import psycopg2
import plotly.graph_objects as go # or plotly.express as px
from dash import Dash, dcc, html, Input, Output  
import random
from datetime import date, datetime, timedelta
import numpy as np


app = Dash(__name__)
server = app.server

def get_db_connection():
    conn = connect()
    return conn




# ------------------------------------------------------------------------------
# App layout


app.layout = html.Div([

    html.H1("S&P 500 Dashboard with Dash", style={'text-align': 'center'}),

    dcc.Input(
        id = 'symbol',
        placeholder='Enter a trading symbol...',
        type='text',
        value='AAPL'
    ),

    html.Div(id='output-container', children=[],
        # style={
        #     'border-style':'solid',
        #     'border-width':'5px'
        #     }
        ),
    html.Br(),

    dcc.Graph(id='graph', figure={})

])

# # ------------------------------------------------------------------------------
# # Connect the Plotly graphs with Dash Components
@app.callback(
        #the input goes into the empty component property

    # input text response    
    [Output(component_id='output-container', component_property='children'),
     
     #graph
     Output(component_id='graph', component_property='figure')],

    #symbol
    [Input(component_id='symbol', component_property='value')], # 'value' is one of the parameters of a dropdown component

)
# the callback input is fed into the following function
def update_graph(symbol):
    conn = get_db_connection()
    cur = conn.cursor()
    # Check if the symbol is invalid
    if type(symbol) != str:
        container = f"Symbol not recognized. Please try again."
        fig = go.Figure()  # Return an empty figure
        return container, fig
    symbol = symbol.upper()
    command = "SELECT * FROM trades WHERE symbol ='" + symbol +"' ORDER BY timestamp DESC;"
    print(command)
    cur.execute(command)
    trades = cur.fetchall()
    cur.close()
    conn.close()
    df = pd.DataFrame(trades, columns=['Id',
            'Company',
            'Symbol',
            'Last_price',
            'Volume',
            'Timestamp',
            'Conditions']
            )
    # Convert the 'Timestamp' column to datetime
    for i in range(len(df)):
        df.loc[i,'Timestamp_converted'] = datetime.fromtimestamp(df.loc[i,'Timestamp'] / 1000)

    

    # Check if the filtered DataFrame is empty
    if df.empty:
        container = f"No data found for the symbol '{symbol}'. Please try another symbol."
        fig = go.Figure()  # Return an empty figure
        return container, fig

    # If data exists, proceed
    container = f"The company chosen by user was {df.loc[0, 'Company']} with the symbol {symbol}"

    # Plotly Graph Objects (GO)
    fig = go.Figure()


    # Add a trace for Volume vs. Timestamp
    fig.add_trace(go.Scatter(
        x=df['Timestamp_converted'],
        y=df['Volume'],
        mode='lines',
        name='Volume vs. Time',
        showlegend=True
    ))

    # Return the container and figure
    return container, fig
    # what is returned here goes into the OUTPUT
    return container, fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)