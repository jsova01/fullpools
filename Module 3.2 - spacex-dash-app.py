# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div(dcc.Dropdown(id='site-dropdown',
                                            options=[{'label': 'All Sites', 'value': 'ALL'}
                                            ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                                            value='ALL',
                                            placeholder='Select a Launch Site here',
                                            searchable=True
                                            )),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                html.Div(dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0', 100: '100'},
                                                value=[min_payload, max_payload]),
                                ),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class', 
            names= 'Launch Site', 
            title='Total Success Launches by Site')
        return fig
    else:
       # return the outcomes piechart for a selected site
       # Group by 'class' and count the occurrences of 1 (success) and 0 (failure)
        class_counts = filtered_df['class'].value_counts().reset_index()
        class_counts.columns = ['class', 'count']
        
        fig = px. pie(class_counts, values='count', 
            names='class', 
            title=f'Total Success Launches for Site {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def get_scatter_plot(entered_site, payload_range):
     # Filter by site (if 'ALL' is selected, use the entire dataset)
    if entered_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

    # Further filter by payload range (payload_range is expected to be a tuple of min and max values)
    min_payload, max_payload = payload_range
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= min_payload) & 
                               (filtered_df['Payload Mass (kg)'] <= max_payload)]

    # Create the scatter plot: x-axis = Payload Mass (kg), y-axis = Success (1 or 0), color by Success
    fig = px.scatter(filtered_df,
        x='Payload Mass (kg)',   # Payload mass as x-axis
        y='class',               # 'class' is the success (1) or failure (0)
        color="Booster Version Category",           # Color by success (1) or failure (0)
        title=f'Payload vs Success for Site: {entered_site}' if entered_site != 'ALL' else 'Payload vs Success for All Sites',
        labels={'class': 'Launch Success (0=Failed, 1=Success)', 'Payload Mass (kg)': 'Payload Mass (kg)'}
    )

    return fig
    
# Run the app
if __name__ == '__main__':
    app.run()