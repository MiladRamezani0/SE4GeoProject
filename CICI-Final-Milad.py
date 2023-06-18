#!/usr/bin/env python
# coding: utf-8

# 
# ## <span style="color:gold">CICI Group Project</span>
# 
# 
# 
# ## <span style="color:gold">Air Quality Report with Jupyter Notebook dashboard</span>

# .
# 
# 
# ## <span style="color:green">CICI_BackEnd</span>

# In[42]:


###...<<< Import libraries >>>...###
from flask import Flask,jsonify,request
import json 
from sqlalchemy import create_engine, text
import os
import requests
import geopandas as gpd
import psycopg2
import geoalchemy2
from jupyter_dash import JupyterDash
import dash
from dash import dcc
from dash import html
JupyterDash.infer_jupyter_proxy_config()
import pandas as pd
import matplotlib.pyplot as plt
from ipywidgets import interact, Dropdown
import folium
import numpy as np
import ipywidgets as widgets
from IPython.display import display
from matplotlib.colors import Normalize
import shapely 
import plotly.graph_objects as go
from folium.plugins import HeatMap
from folium import IFrame
import plotly.express as px
import folium.plugins as plugins
import base64

# print('\n Import libraries Done!!!')
# ###...<<< download Data from the https://discomap.eea.europa.eu/map/fme/AirQualityUTDExport.htm >>>...###
# # Set the directory path to save the files
# save_directory = "E:/Plimi/01 - First Term/03 - Software Engineering For Geoinformatics/05 - Project/03 - python code/CICI-Group-Project/CICI_Data"
# # Rest of your code
# #print('-----------------------------------------------------------------------')
# # Set download url
# ServiceUrl = "http://discomap.eea.europa.eu/map/fme/latest"
# # Countries to download
# # Note: List is not complete['IT','DE']#
# countries = ['AD','AT','BA','BG','CZ','DE','DK','EE','GI','HR','IE','IS','LT','LU','LV','NL','PL','PT','SE','BE','CY','ES','FR','GR','HU','IT','MT','NO','XK','FI','GB','RS','SI','SK','CH']
# # Pollutant to be downloaded
# pollutants = ['NO2','O3','CO','SO2','PM2.5','PM10','NO']
# for country in countries:
#     for pollutant in pollutants:
#         fileName = "%s_%s.csv" % (country, pollutant)
#         downloadFile = '%s/%s_%s.csv' % (ServiceUrl, country, pollutant)
#         # Download and save to local path
#         #print('Downloading: %s' % downloadFile )
#         file = requests.get(downloadFile).content
#         output_path = os.path.join(save_directory, fileName)
#         with open(output_path, 'wb') as output:
#             output.write(file)
#         #print('Saved locally as: %s' % output_path)
#         #print('-----')
# print('Download finished')
################################################################DATA BASE #####################################################
# # Setup db connection (generic connection path to be update with your credentials: 'postgresql://user:password@localhost:5432/mydatabase')
# engine = create_engine('postgresql://postgres:mrzk1234@localhost:5432/se4g') 
# con = engine.connect()
# con
# data=gpd.read_file(r"E:/Plimi/01 - First Term/03 - Software Engineering For Geoinformatics/05 - Project/03 - python code/CICI-Group-Project/CICI_Data/01_Data/CICI_Data.csv")
# print("Done!!!")
# #save data to sql
# data.to_sql('CICI_Data', engine, if_exists = 'replace', index=False)
# print("Done!!!")
################################################################DATA BASE #####################################################
# Directory containing the CSV files
directory = r"E:/Plimi/01 - First Term/03 - Software Engineering For Geoinformatics/05 - Project/03 - python code/CICI-Group-Project/CICI_Data"
# Initialize an empty list to store the DataFrames
dataframes = []
# Iterate over each file in the directory
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        file_path = os.path.join(directory, filename)
        
        # Check the file size in bytes
        file_size = os.path.getsize(file_path)
        if file_size < 15360:  # File size less than 15 KB
            continue  # Skip this file
        
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        # Append the DataFrame to the list
        dataframes.append(df)
# Concatenate all the DataFrames into a single DataFrame
merged_data = pd.concat(dataframes, ignore_index=True)
# Delete rows with negative values in value_numeric column
merged_data = merged_data[merged_data['value_numeric'] >= 0]
# Specify the column containing the date and time values
column_name = 'value_datetime_begin'
# Convert the column to datetime format
merged_data[column_name] = pd.to_datetime(merged_data[column_name])
# Create new columns for time and date
merged_data['Time'] = merged_data[column_name].dt.time
merged_data['Date'] = merged_data[column_name].dt.date
# Remove the original datetime column
merged_data.drop(columns=[column_name], inplace=True)
# Drop rows with missing values in 'value_numeric' column
merged_data.dropna(subset=['value_numeric'], inplace=True)
###...<<< delete some columns >>>...###
###...<<< and insert country full name >>>...###
# List of columns to be deleted
columns_to_delete = ['network_localid', 'network_name', 'network_namespace','network_timezone', 'samplingpoint_localid', 'samplingpoint_namespace','station_localid', 'station_namespace', 'value_datetime_end','value_datetime_inserted', 'value_datetime_updated', 'value_validity', 'value_verification']  
# Delete the columns from the DataFrame
merged_data = merged_data.drop(columns=columns_to_delete)
# Define a dictionary mapping symbols to names
country_mapping = {
    'AD': 'Andorra','AT': 'Austria','BA': 'Bosnia and Herzegovina','BG': 'Bulgaria','CZ': 'Czech Republic','DE': 'Germany','DK': 'Denmark','EE': 'Estonia','GI': 'Gibraltar','HR': 'Croatia','IE': 'Ireland','IS': 'Iceland','LT': 'Lithuania','LU': 'Luxembourg','LV': 'Latvia','NL': 'Netherlands','PL': 'Poland','PT': 'Portugal','SE': 'Sweden','BE': 'Belgium','CY': 'Cyprus','ES': 'Spain','FR': 'France','GR': 'Greece','HU': 'Hungary','IT': 'Italy','MT': 'Malta','NO': 'Norway','XK': 'Kosovo','FI': 'Finland','GB': 'United Kingdom','RS': 'Serbia','SI': 'Slovenia','SK': 'Slovakia','CH': 'Switzerland'
}
# Replace symbols with names in the specified column
merged_data['network_countrycode'] = merged_data['network_countrycode'].replace(country_mapping)
# Create a dictionary of country coordinates
country_coordinates = {
    'Albania': (41.1533, 20.1683),'Andorra': (42.5462, 1.6016),'Austria': (47.5162, 14.5501),'Belarus': (53.7098, 27.9534),'Belgium': (50.5039, 4.4699),'Bosnia and Herzegovina': (43.9159, 17.6791),'Bulgaria': (42.7339, 25.4858),'Croatia': (45.1000, 15.2000),'Cyprus': (35.1264, 33.4299),'Czech Republic': (49.8175, 15.4730),'Denmark': (56.2639, 9.5018),'Estonia': (58.5953, 25.0136),'Finland': (61.9241, 25.7482),'France': (46.6034, 1.8883),'Germany': (51.1657, 10.4515),'Gibraltar': (36.14, 5.35),'Greece': (39.0742, 21.8243),'Hungary': (47.1625, 19.5033),'Iceland': (64.9631, -19.0208),'Ireland': (53.4129, -8.2439),'Italy': (41.8719, 12.5674),'Kosovo': (42.6026, 20.9030),'Latvia': (56.8796, 24.6032),'Liechtenstein': (47.1660, 9.5554),'Lithuania': (55.1694, 23.8813),'Luxembourg': (49.8153, 6.1296),'Malta': (35.9375, 14.3754),'Moldova': (47.4116, 28.3699),'Monaco': (43.7384, 7.4246),'Montenegro': (42.7087, 19.3744),'Netherlands': (52.1326, 5.2913),'North Macedonia': (41.6086, 21.7453),'Norway': (60.4720, 8.4689),'Poland': (51.9194, 19.1451),'Portugal': (39.3999, -8.2245),'Romania': (45.9432, 24.9668),'Russia': (61.5240, 105.3188),'San Marino': (43.9424, 12.4578),'Serbia': (44.0165, 21.0059),'Slovakia': (48.6690, 19.6990),'Slovenia': (46.1512, 14.9955),'Spain': (40.4637, -3.7492),'Sweden': (60.1282, 18.6435),'Switzerland': (46.8182, 8.2275),'Ukraine': (48.3794, 31.1656),'United Kingdom': (55.3781, -3.4360),'Vatican City': (41.9029, 12.4534)
}
# Convert non-numeric values in value_numeric to NaN
merged_data['value_numeric'] = pd.to_numeric(merged_data['value_numeric'], errors='coerce')
# Group the data by network_countrycode, pollutant, and value_unit
mean_samplingpoint = merged_data.groupby(['network_countrycode', 'pollutant'])['value_numeric'].mean(numeric_only=True).reset_index()
# Add the unit and station name columns
mean_samplingpoint['unit'] = mean_samplingpoint.apply(lambda row: merged_data.loc[(merged_data['network_countrycode'] == row['network_countrycode']) & (merged_data['pollutant'] == row['pollutant']), 'value_unit'].iloc[0], axis=1)
mean_samplingpoint['station_name'] = mean_samplingpoint.apply(lambda row: merged_data.loc[(merged_data['network_countrycode'] == row['network_countrycode']) & (merged_data['pollutant'] == row['pollutant']), 'station_name'].iloc[0], axis=1)
# Add the coordinates for each country
mean_samplingpoint['coordinates'] = mean_samplingpoint['network_countrycode'].map(country_coordinates)
# Add the samplingpoint_x and samplingpoint_y columns
mean_samplingpoint['samplingpoint_x'] = mean_samplingpoint['coordinates'].apply(lambda coord: coord[0])
mean_samplingpoint['samplingpoint_y'] = mean_samplingpoint['coordinates'].apply(lambda coord: coord[1])
##########################################################################################################################################################################################################################
# Filter the data based on user-selected country and pollution
def filter_data(country, pollutant):
    filtered_data = merged_data[(merged_data['network_countrycode'] == country) & (merged_data['pollutant'] == pollutant)]
    return filtered_data.tail(48)  # Limit the data to the last 48 rows
######################popUp#########################
# Group the data by network_countrycode, pollutant, and value_unit
mean_samplingpoint = merged_data.groupby(['network_countrycode', 'pollutant'])[['samplingpoint_x', 'samplingpoint_y', 'value_numeric', 'value_unit']].mean(numeric_only=True).reset_index()
# Add a column to show the unit of data
mean_samplingpoint['unit'] = mean_samplingpoint.apply(lambda row: merged_data.loc[(merged_data['network_countrycode'] == row['network_countrycode']) & (merged_data['pollutant'] == row['pollutant']), 'value_unit'].iloc[0], axis=1)
# Add the station name column
mean_samplingpoint['station_name'] = mean_samplingpoint.apply(lambda row: merged_data.loc[(merged_data['network_countrycode'] == row['network_countrycode']) & (merged_data['pollutant'] == row['pollutant']), 'station_name'].iloc[0], axis=1)
# Create a dropdown menu to select the pollution type
pollution_types = mean_samplingpoint['pollutant'].unique()
# Create a map centered on Europe
latitude_center = 38.77  
longitude_center = 9.18  
zoom_level = 4  # Specify the initial zoom level for the map
mape = folium.Map(location=[latitude_center, longitude_center], zoom_start=zoom_level)
# Create a dictionary to store the popup messages for each country
country_popups = {}
# Iterate over the data to create the popup messages
for index, row in mean_samplingpoint.iterrows():
    country = row['network_countrycode']
    pollutant = row['pollutant']
    value = round(row['value_numeric'], 3)  # Round the value to 3 decimal places
    unit = row['unit']
    station_name = row['station_name']  # Retrieve the station name    
    # Create a message for the current pollutant
    pollutant_message = f"<b>Pollutant:</b> {pollutant}<br><b>Value:</b> {value} {unit}<br><b>Station:</b> {station_name}<br>"
    # Add the pollutant message to the country's popup message
    if country in country_popups:
        country_popups[country] += "<br>" + pollutant_message
    else:
        country_popups[country] = f"<b>Country:</b> {country}<hr>{pollutant_message}"
# Create a single popup for each country with multiple sections
for country, popup_message in country_popups.items():
    # Create the popup message for the country
    country_popup = folium.Popup(popup_message, max_width=900, max_height=600)
    # Add a marker for the country with the custom popup
    folium.Marker(location=country_coordinates[country], popup=country_popup).add_to(mape)  
#############################EndPopUp####################
#############################Pollution Data by Country####################
############################################
# Initialize the JupyterDash app
app = JupyterDash(__name__)
# Create dropdown widgets for country selection
country_dropdown = dcc.Dropdown(
    options=[{'label': country, 'value': country} for country in merged_data['network_countrycode'].unique()],
    value=merged_data['network_countrycode'].unique()[0],
    id='country-dropdown',
    clearable=False
)
# Create a radio bar for pollutant selection
pollutant_radio = dcc.RadioItems(
    options=[{'label': pollutant, 'value': pollutant} for pollutant in merged_data['pollutant'].unique()],
    value=merged_data['pollutant'].unique()[0],
    labelStyle={'display': 'inline-block', 'margin': '10px'},
    id='pollutant-radio'
)
# Create an output div for displaying the chart or error message
output = html.Div(id='output-div')
#############################################################
# Create a function to generate the heatmap based on the selected pollution type
def generate_heatmap(pollution_type):
    filtered_data = mean_samplingpoint[mean_samplingpoint['pollutant'] == pollution_type]

    heatmap = folium.Map(
        location=[latitude_center, longitude_center],
        zoom_start=zoom_level,
        tiles='CartoDB dark_matter'
    )
    if len(filtered_data) == 0:
        # Add a red marker to the center if no data is available
        folium.Marker(
            location=[latitude_center, longitude_center],
            icon=folium.Icon(color='red', icon='info-sign'),
        ).add_to(heatmap)
    else:
        # Create a heatmap layer
        heat_data = [[row['samplingpoint_y'], row['samplingpoint_x'], row['value_numeric']] for _, row in filtered_data.iterrows()]
        heatmap_layer = plugins.HeatMap(heat_data)
        heatmap_layer.add_to(heatmap)
    return heatmap._repr_html_()
#############################################################

# Define the app layout
app.layout = html.Div(
    # style={'backgroundColor': 'black'},  # Set the background color to black
    children=[
        html.H1("Pollution Dashboard"),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.H2("----------------------------------------- Measurement of pollution in different country in the last 48 hours -----------------------------------------"),
        html.Div([
            html.Label("Select Country:"),
            country_dropdown,
            html.Label("Select Pollutant:"),
            pollutant_radio
        ]),
        dcc.Graph(id='graph'),  # Add the graph component with the id 'graph'
        output,
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.H2("----------------------------------------------- Each country's average pollution in the 48 hours prior -----------------------------------------------"),
        html.Iframe(srcDoc=mape._repr_html_(), width='100%', height='500'),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.H2("------------------------------------------------ Pollution Data by Country in the 48 hours prior ------------------------------------------------"),
        html.Label("Select Pollution Type:"),
        dcc.Dropdown(
            id='pollution-dropdown',
            options=[{'label': pt, 'value': pt} for pt in pollution_types],
            value=pollution_types[0]
        ),
        dcc.Graph(id='pollution-graph'),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.H2("------------------------------------------------ Display the 48-hour pollution heatmap by country ------------------------------------------------"),
        html.Div(
            id='radio-bar-container',
            style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'},
            children=[
                html.Label("Pollution Type"),
                dcc.RadioItems(
                    id='pollution-type-radio',
                    options=[{'label': pollutant_name, 'value': pollutant_name} for pollutant_name in mean_samplingpoint['pollutant'].unique()],
                    value=mean_samplingpoint['pollutant'].unique()[0],
                    labelStyle={'display': 'inline-block', 'margin': '10px'}
                )
            ]
        ),
        html.Div(id='map-container', children=[html.Iframe(srcDoc='', id='map-iframe', width='100%', height='500')]),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.H2("------------------------------------------------ Download CSV Files ------------------------------------------------"),
        html.Div([
            html.A('Download merged_data CSV', id='download-merged-data', download='merged_data.csv', href='', target='_blank'),
            html.Br(),
            html.A('Download mean_samplingpoint CSV', id='download-mean-samplingpoint', download='mean_samplingpoint.csv', href='', target='_blank')
        ])
    ]
)

@app.callback(
    Output('pollution-graph', 'figure'),
    Input('pollution-dropdown', 'value')
)
def update_graph(selected_pollution):
    # Filter the data for the selected pollution type
    selected_data = mean_samplingpoint[mean_samplingpoint['pollutant'] == selected_pollution]

    # Sort the data by country name
    selected_data = selected_data.sort_values(by='network_countrycode')

    # Create the plotly figure
    fig = px.scatter(
        selected_data,
        x='network_countrycode',
        y='value_numeric',
        size='value_numeric',
        color='value_numeric',
        hover_name='network_countrycode',
        labels={'network_countrycode': 'Country', 'value_numeric': f'{selected_pollution} Value ({selected_data["unit"].iloc[0]})'},
        title=f'{selected_pollution} Pollution by Country',
    )
    fig.update_layout(
        xaxis={'tickangle': 90},
        yaxis={'range': [-5, selected_data['value_numeric'].max() * 1.2]},
        coloraxis_colorbar={'title': f'{selected_pollution} Value ({selected_data["unit"].iloc[0]})'}
    )
    return fig
# Define the callback function
@app.callback(
    Output('graph', 'figure'),  # Specify the 'graph' id as the output
    Input('country-dropdown', 'value'),
    Input('pollutant-radio', 'value')
)
def update_chart(country, pollutant):
    filtered_data = filter_data(country, pollutant)
    if len(filtered_data) > 0:
        title = f"Measurement of {pollutant} pollution in {country} in the last 48 hours"

        # Plot the data using Plotly
        fig = go.Figure(data=go.Scatter(
            x=list(range(48)),
            y=filtered_data['value_numeric'],
            mode='markers',
            marker=dict(
                color=filtered_data['value_numeric'],
                colorscale='jet',
                size=10,
                colorbar=dict(
                    title=f'{pollutant} ({filtered_data["value_unit"].iloc[0]})',
                    yanchor='middle', y=0.5,
                    len=0.75, lenmode='fraction',
                    thickness=20, thicknessmode='pixels',
                    xanchor='left', x=1.05,
                )
            ),
            name='Data'
        ))
        fig.update_layout(
            title=title,
            xaxis_title='Time',
            yaxis_title=f'{pollutant} ({filtered_data["value_unit"].iloc[0]})',
            coloraxis_showscale=False,
            margin=dict(l=50, r=150, b=50, t=80),
            coloraxis_colorbar=dict(
                title_font=dict(size=14),
                tickfont=dict(size=12),
            ),
            legend=dict(
                title='Statistics',
                yanchor='top',
                y=0.99,
                xanchor='left',
                x=1.01,
                bgcolor='rgba(255, 255, 255, 0.7)',
                bordercolor='rgba(0, 0, 0, 0.5)',
                borderwidth=1,
                itemsizing='constant',
                itemclick='toggle',
                itemdoubleclick='toggleothers',
                font=dict(size=12),
                traceorder='normal'
            )
        )

        return fig
    else:
        error_message = f"We don't have data for {pollutant} in {country}. Please try another pollutant or country."
        return error_message
# Define callback to update the map's iframe content based on the selected pollution type
@app.callback(
    Output('map-iframe', 'srcDoc'),
    [Input('pollution-type-radio', 'value')]
)
def update_map(pollution_type):
    updated_map = generate_heatmap(pollution_type)
    return updated_map
# Callbacks to update the download links
@app.callback(
    Output('download-merged-data', 'href'),
    Output('download-mean-samplingpoint', 'href'),
    Input('download-merged-data', 'n_clicks'),
    Input('download-mean-samplingpoint', 'n_clicks')
)
def update_download_links(merged_data_clicks, mean_samplingpoint_clicks):
    ctx = dash.callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if triggered_id == 'download-merged-data':
            df = merged_data
            filename = 'merged_data.csv'
        elif triggered_id == 'download-mean-samplingpoint':
            df = mean_samplingpoint
            filename = 'mean_samplingpoint.csv'
        else:
            df = None
            filename = None
        
        if df is not None:
            # Create a CSV string from the dataframe
            csv_string = df.to_csv(index=False, encoding='utf-8')
            csv_string = "data:text/csv;charset=utf-8," + base64.b64encode(csv_string.encode()).decode()
            return csv_string, csv_string
    
    # Return empty href for initial state
    return '', ''
# Run the app
if __name__ == '__main__':
    app.run_server(mode='inline',port=9012)
    # app.run_server(mode='external',port=9012)
    # app.run_server(mode='jupyterlab',port=9012)


# In[ ]:




