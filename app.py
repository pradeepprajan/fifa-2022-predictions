from dash import html
from dash import dcc
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import Output, Input

# importing data
df_2022 = pd.read_csv('fifa_2022.csv')
df_2022_avg = pd.read_csv('fifa_2022_avg.csv')

# finding total number of goals and matches
df_2022_avg['Total_goals'] = df_2022_avg['goals_as_team1']+df_2022_avg['goals_as_team2']
df_2022_avg['Total_matches'] = df_2022_avg['matches_as_team1']+df_2022_avg['matches_as_team2']

# preparing data for plotting
date_today = '2022-12-03'
date_tomorrow = '2022-12-04'
today_match = df_2022[:][(df_2022['match_date'] == date_today) | (df_2022['match_date'] == date_tomorrow)]
today_teams = []
for index,row in today_match.iterrows():
    today_teams.append([row['team1'],row['team2']])

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
server = app.server
option_list = []
for match in today_teams:
    stage = today_match.loc[(today_match['team1']==match[0]) & (today_match['team2']==match[1]),'stage'].to_string().split("  ")[2]
    params = {'label': match[0]+' vs '+match[1]+' - '+stage, 'value': match[0]+' vs '+match[1]+' - '+stage}
    option_list.append(params)
default_stage = today_match.loc[(today_match['team1']==today_teams[0][0]) & (today_match['team2']==today_teams[0][1]),'stage'].to_string().split("  ")[2]
dropdown = html.Div([
    html.Label('Select the match', style={'display': 'block', 'fontSize': 15, 'marginLeft': 10}),
    dcc.Dropdown(
        id='match-dropdown',
        options=option_list,
        value=today_teams[0][0]+' vs '+today_teams[0][1]+' - '+default_stage,
        clearable=False,
        style={'marginLeft': 10, 'marginRight': 20}
    )
])

app.layout = html.Div(
    [
        dbc.Row([
            dbc.Col((html.H1('FIFA 2022 World Cup Qatar Predictor',
                             style={'textAlign': 'center', 'color': 'white', 'marginTop': 90})), width=12)
        ], style={'background-color': 'indigo', 'marginBottom': 20, 'height': 200}),
html.Div([
            dbc.Row([
                dbc.Col(
                    html.H2(html.B('Predictions on '+date_today+' and '+date_tomorrow+' - Probability of win'),
                            style={'textAlign': 'left', 'marginBottom': 30, 'marginLeft': 10, 'marginTop': 15}),
                    width=12)
            ]),
            dbc.Row([
                dbc.Col(dropdown, width=12)
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='match-piechart', figure={}, config={'displayModeBar': False}))
            ], style={'marginBottom': 30}),
            dbc.Row([
                dbc.Col(html.Hr(style={'width': '99%', 'color': 'black', 'border-width': 2, 'marginBottom': 30,
                                       'marginLeft': 0}))
            ])
        ]),
html.Div([
            dbc.Row([
                dbc.Col(
                    html.H2(html.B('Performance history of playing teams in past world cups since 1930'),
                            style={'textAlign': 'left', 'marginBottom': 30, 'marginLeft': 10, 'marginTop': 15}),
                    width=12)
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='performance-matches-barchart', figure={}, config={'displayModeBar': False}))
            ], style={'marginBottom': 30}),
            dbc.Row([
                dbc.Col(dcc.Graph(id='performance-goals-barchart', figure={}, config={'displayModeBar': False}))
            ], style={'marginBottom': 30})
        ]),

])

@app.callback(
    [Output(component_id='match-piechart', component_property='figure'),
    Output(component_id='performance-matches-barchart',component_property='figure'),
    Output(component_id='performance-goals-barchart',component_property='figure')],
    [Input(component_id='match-dropdown', component_property='value')]
)
def match(match_today_string):
    match_today_comp = match_today_string.split(" vs ")
    match_today = [match_today_comp[0],match_today_comp[1].split(" - ")[0]]
    value1 = float(today_match['prob_team1_win'][(today_match['team1'] == match_today[0]) & (today_match['team2'] == match_today[1])])
    value2 = float(today_match['prob_team2_win'][(today_match['team1'] == match_today[0]) & (today_match['team2'] == match_today[1])])
    value3 = float(today_match['prob_draw'][(today_match['team1'] == match_today[0]) & (today_match['team2'] == match_today[1])])
    plot_data_history = df_2022_avg[:][(df_2022_avg['team_name'] == match_today[0]) | (df_2022_avg['team_name'] == match_today[1])]
    fig_pie_chart = px.pie(names=[match_today[0],match_today[1],'Draw'],
                           values=[value1,value2,value3],
                           color=[1,2,3],
                           color_discrete_map={1:'blue',2:'green',3:'orange'})
    fig_pie_chart.update_traces(hovertemplate='Team : %{label}: Probability of win: %{value} %')
    fig_bar_chart_matches = px.bar(plot_data_history,x='team_name',y='Total_matches',
                                   color='team_name')
    fig_bar_chart_matches.update_layout(width=1000)
    fig_bar_chart_matches.update_xaxes(title_text="Team")
    fig_bar_chart_matches.update_yaxes(title_text="Number of matches played")
    fig_bar_chart_goals = px.bar(plot_data_history,x='team_name', y='Total_goals',
                                 color='team_name')
    fig_bar_chart_goals.update_layout(width=1000)
    fig_bar_chart_goals.update_xaxes(title_text="Team")
    fig_bar_chart_goals.update_yaxes(title_text="Number of goals played")
    return fig_pie_chart,fig_bar_chart_matches,fig_bar_chart_goals

if __name__ == '__main__':
    app.run_server(debug=False)


