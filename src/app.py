from config import config
import pandas as pd
from connect import connect
import psycopg2
import plotly.graph_objects as go # or plotly.express as px
from dash import Dash, dcc, html, Input, Output  
import random
from datetime import date, datetime, timedelta
import numpy as np
import pytz


app = Dash(__name__)
server = app.server

def get_db_connection():
    conn = connect()
    return conn

conn = get_db_connection()
cur = conn.cursor()
cur.execute('SELECT * FROM weather;')
weather = cur.fetchall()
cur.execute('SELECT * FROM riseset;')
riseset = cur.fetchall()
cur.close()
conn.close()




df = pd.DataFrame(weather, columns=['Id',
          'Current Weather',
          'Description of the Weather',
          'Temperature ((\u00B0f))',
          'Feels Like ((\u00B0f))',
          'Minimum Temperature ((\u00B0f))',
          'Maximum Temperature ((\u00B0f))',
          'Humidity (%)',
          'Wind Speed (mph)',
          'Wind Direction ((\u00B0f) clockwise from N)',
          'Time Stamp (GMT)'])
sun = pd.DataFrame(riseset, columns=['Id', 'sunrise (GMT)', 'sunset (GMT)'])

# Change timezones
df['Time Stamp'] =  df['Time Stamp (GMT)'].dt.tz_convert('US/Eastern')
sun['sunrise'] = sun['sunrise (GMT)'].dt.tz_convert('US/Eastern')
sun['sunset'] = sun['sunset (GMT)'].dt.tz_convert('US/Eastern')




# tz = pytz.timezone('America/New_York')
# for s in [df, sun]:
#     for r in range(len(s)):
#         for c in s.columns:
#             if isinstance(s.loc[r,c], datetime):
#                 # print(s[r][c], type(s[r][c]))
#                 s.loc[r,c] = s.loc[r,c].dt.astimezone(tz)
# num_rows = len(riseset)
# # Get the number of columns (elements in each tuple)
# num_cols = len(riseset[0]) if num_rows > 0 else 0
# print("Shape:", (num_rows, num_cols))

# print(sun.shape)

# num_rows = len(weather)
# # Get the number of columns (elements in each tuple)
# num_cols = len(weather[0]) if num_rows > 0 else 0
# print("Shape:", (num_rows, num_cols))

# print(df.shape)

# print(riseset[25][2])
# print(type(riseset[25][2]))
# print(sun['sunrise'])
# print(type(sun.loc[25,'sunset']))

# print("weather")
# print(weather[3381][10])
# print(type(weather[3381][10]))
# print(df.loc[3381,'Time Stamp'])
# print(type(df.loc[3381,'Time Stamp']))
# print(df['Time Stamp'].dt.time)
# print(df.loc[3381,'Time Stamp'].tzinfo)
# print(sun.loc[25,'sunrise'].tzinfo)
# print(sun.loc[25,'sunset'].tzinfo)



df.drop('Id', axis=1, inplace=True)
df.drop_duplicates(inplace=True, ignore_index=True)
df = df.sort_values(by = 'Time Stamp')
sun.drop('Id', axis=1, inplace=True)
sun = sun.sort_values(by = 'sunrise')


# df['Date'] = 0
# df.loc[i, "Date"] = str(df.loc[i, 'Time Stamp'].date()).replace('-','')

df['Time'] = 0
df['Hour'] = df['Time Stamp'].dt.hour
df['Minute'] = df['Time Stamp'].dt.minute

sun['RiseTime'] = 0
sun['SetTime'] = 0
sun['RiseHour'] = sun['sunrise'].dt.hour
sun['SetHour'] = sun['sunset'].dt.hour
sun['RiseMinute'] = sun['sunrise'].dt.minute
sun['SetMinute'] = sun['sunset'].dt.minute


# stringitize the time of day
for s in [df,sun]:
    for r in range(len(s)):
        for c in ['', 'Rise','Set']:
            # ignore when column name doesn't exist in df
            try:
                hr = str(s.loc[r,c+"Hour"])
                min = str(s.loc[r,c+'Minute'])
                #2 digits of minutes
                if len(min)>1:
                    # 2 digits of minutes and hours
                    if len(hr) >1:
                        s.loc[r, c+"Time"] =int( hr + min )
                    # 2 digits of minutes and 1 digit of hours
                    else:
                        s.loc[r, c+"Time"] =int( '0' + hr + min )
                # 1 digit of minutes and two digits of hours
                elif len(hr) >1:
                    s.loc[r, c + "Time"] =int( hr + '0' + min )
                # 1 digit of minutes and hours
                else:
                    s.loc[r, c+"Time"] = int( '0' + hr + '0' + min )

            except:
                continue





# ------------------------------------------------------------------------------
# App layout


app.layout = html.Div([

    html.H1("Weather Application Dashboards with Dash", style={'text-align': 'center'}),

    dcc.DatePickerRange(
        id='date-picker-range',
        start_date_placeholder_text='12/17/2024',
        min_date_allowed=date(2024, 12, 17),
        end_date = date.today(),
        start_date= date.today() - timedelta(days=30),
        # if year, month, day matches
        end_date_placeholder_text='Select a date'
    ),

    html.Div(id='output_container', children=[],
        # style={
        #     'border-style':'solid',
        #     'border-width':'5px'
        #     }
        ),
    html.Br(),

    dcc.Graph(id='weather_range', figure={})

])

# # ------------------------------------------------------------------------------
# # Connect the Plotly graphs with Dash Components
@app.callback(
        #the input goes into the empty component property

    # input text response    
    [Output(component_id='output_container', component_property='children'),
     
     #graph
     Output(component_id='weather_range', component_property='figure')],

    #start date
    [Input(component_id='date-picker-range', component_property='start_date')], # 'value' is one of the parameters of a dropdown component

    #end date
    [Input(component_id='date-picker-range', component_property='end_date')] # 'value' is one of the parameters of a dropdown component
)
# the callback input is fed into the following function
def update_graph(start, end):

    start_date_object = datetime.strptime(start, '%Y-%m-%d').date()
    end_date_object = datetime.strptime(end, '%Y-%m-%d').date()

    container = "The range chosen by user was from {} to {}".format(start, end)

    dff = df.copy()
    dff = dff[ dff["Time Stamp"].dt.date >= start_date_object]
    dff = dff[ dff["Time Stamp"].dt.date <= end_date_object]
    sunc = sun.copy()
    sunc = sunc[ sunc["sunrise"].dt.date >= start_date_object]
    sunc = sunc[ sunc["sunrise"].dt.date <= end_date_object]


    # Plotly Graph Objects (GO)
    fig = go.Figure()

# we're trying to get this graph problem where we only get a small consecutive segement of time each day.

# Maybe if we add a trace for each individual day, we'll get all the data

# if that doesn't work, let's first work on the basic explorer: type in details and a table comes up
    
    # for each date
    fig.add_trace(go.Scatter(
        x = sunc['sunrise'].dt.date,
        y = sunc['RiseTime'],
        mode='lines+markers',
        name ='sunrise',
        fill='tozeroy',
        line=dict(
            color = 'gray'
        ),
        marker=dict(
            symbol = "circle",
            size = 15
        ),
        showlegend=True,
        
        

    ))

    fig.add_trace(go.Scatter(
        x = sunc['sunrise'].dt.date,
        y = [2500]*len(sunc),
        mode='lines',
        showlegend=False,
        line= dict(
            color = 'lightgray'
        )

    ))

    fig.add_trace(go.Scatter(
        x = sunc['sunset'].dt.date,
        y = sunc['SetTime'],
        mode='lines+markers',
        name ='sunset',
        fill='tonexty',
        line=dict(
            color = 'gray'
        ),
        marker=dict(
            symbol = "circle",
            size = 15
        ),
        showlegend=True,
    ))

    for i in range(len(dff['Time Stamp'].dt.date.unique())):
        day = dff['Time Stamp'].dt.date.unique()[i]
        dfday = dff.copy()
        dfday=dfday[dfday['Time Stamp'].dt.date == day]

        fig.add_trace(go.Scatter(
                x = dfday['Time Stamp'].dt.date,
                y = dfday['Time'],
                mode = 'markers',
                name=str(day),
                marker=dict(
                    color=dfday['Temperature ((\u00B0f))'],
                    coloraxis='coloraxis'
                            ),
                marker_symbol='square'
                )
        )


    # or any Plotly Express function e.g. px.bar(...)
    # fig.add_trace( ... )
    fig.update_layout(
            title=dict(
                text='Temperature thoughout the day'
            ),
            xaxis=dict(
                title=dict(
                    text= "Date"
                ),
                # showgrid=True,
                # ticklabelmode="period",
                # dtick="D1", 
                # # tickformat="%a\n%m/%d"
            ),
            yaxis=dict(
                title=dict(
                    text='Time of Day HHMM'
                ),
                tickvals=[k*100 for k in range(0,24)],
                ticktext=['00:00','01:00','02:00','03:00','04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00']
            ),
            height=700,
            showlegend=False,
            coloraxis =dict(
                colorbar=dict(
                    title_text= "Temperature (\u00B0F)",
                    # tickmode='linear',
                    # dtick=5,
                    # tick0=0

                )
                ),
                


    )

    # what is returned here goes into the OUTPUT
    return container, fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)