from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Read data from the provided CSV file
df = pd.read_csv('https://raw.githubusercontent.com/DS4Ag/agr333s/refs/heads/main/data/survey_db.csv')

# Create Dash app
app = Dash(__name__)

# Define a professional color palette
color_palette = px.colors.qualitative.Safe

# Layout
app.layout = html.Div(style={'font-family': 'Arial', 'padding': '20px'}, children=[

    # Header Section
    html.Div(style={'backgroundColor': '#343a40', 'padding': '20px', 'color': '#ffffff'}, children=[
        html.H1('Survey Analysis Dashboard', style={'textAlign': 'center'}),
        html.P('AGR 33300 - Data Science for Agriculture', style={'textAlign': 'center'})
    ]),

    # Filters Section
    html.Div(style={'display': 'flex', 'marginTop': '20px'}, children=[
        html.Div(style={'width': '25%', 'padding': '20px', 'backgroundColor': '#f8f9fa',
                        'borderRadius': '10px', 'boxShadow': '0px 4px 6px rgba(0,0,0,0.1)'}, children=[
            html.H3('Required Filters'),
            html.Label('Select Section:'),
            dcc.Dropdown(
                id='section-dropdown',
                options=[{'label': i, 'value': i} for i in df['Section'].unique()],
                value=df['Section'].unique()[0],
                style={'marginBottom': '20px'}
            ),
            html.Label('Select Question:'),
            dcc.Dropdown(
                id='question-dropdown',
                options=[],
                value=None,
                optionHeight=60,
                style={
                    'marginBottom': '20px',
                    'whiteSpace': 'normal',
                    'width': '100%'
                }
            ),
            # Add a horizontal line to separate required and optional filters
            html.Hr(style={'borderWidth': '1px', 'borderColor': '#ccc', 'marginTop': '30px'}),
            html.H3('Optional Filters', style={'fontSize': '18px'}),
            html.Label('Select Grade Level:', style={'fontSize': '14px'}),
            dcc.Dropdown(
                id='grade-level-dropdown',
                options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in
                                                              df['College Grade Level'].unique()],
                value='All',
                style={'marginBottom': '20px'}
            ),
            html.Label('Select Major:', style={'fontSize': '14px'}),
            dcc.Dropdown(
                id='major-dropdown',
                options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in
                                                              df['Major/Field of Study'].unique()],
                value='All'
            )
        ]),

        # Charts Section
        html.Div(style={'width': '75%', 'paddingLeft': '20px'}, children=[
            # Summary Cards Section
            dcc.Loading(
                id="loading-summary",
                type="circle",
                children=html.Div(id='summary-cards-container', style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "marginBottom": "20px",
                    "gap": "10px",
                    "flexWrap": "wrap"
                })
            ),

            # Graphs Section
            dcc.Loading(
                id="loading-graphs",
                type="circle",
                children=html.Div(id='charts-container')
            )
        ])
    ])
])


# Callback for question dropdown options
@app.callback(
    Output('question-dropdown', 'options'),
    [Input('section-dropdown', 'value')]
)
def update_question_dropdown(selected_section):
    questions = df[df['Section'] == selected_section]['Question'].unique()
    return [{'label': q, 'value': q} for q in questions]


# Callback for summary cards
@app.callback(
    Output('summary-cards-container', 'children'),
    [Input('section-dropdown', 'value'),
     Input('question-dropdown', 'value'),
     Input('grade-level-dropdown', 'value'),
     Input('major-dropdown', 'value')]
)
def update_summary_cards(selected_section, selected_question, selected_grade, selected_major):
    if not selected_question:
        return []

    # Filter data based on all selections
    filtered_df = df[(df['Section'] == selected_section) &
                     (df['Question'] == selected_question)]

    if selected_grade != 'All':
        filtered_df = filtered_df[filtered_df['College Grade Level'] == selected_grade]
    if selected_major != 'All':
        filtered_df = filtered_df[filtered_df['Major/Field of Study'] == selected_major]

    # Calculate metrics
    total_responses = len(filtered_df)
    answer_counts = filtered_df['Answer'].value_counts()
    most_common_answer = answer_counts.idxmax() if not answer_counts.empty else "N/A"
    unique_answers = len(answer_counts)

    # Create summary cards
    cards = [
        html.Div(style={
            "backgroundColor": "#f8f9fa",
            "padding": "15px",
            "borderRadius": "10px",
            "boxShadow": "0px 4px 6px rgba(0,0,0,0.1)",
            "flex": "1",
            "minWidth": "250px"
        }, children=[
            html.H3("Total Responses", style={"textAlign": "center", "marginBottom": "10px"}),
            html.P(f"{total_responses}", style={"textAlign": "center", "fontSize": "24px", "margin": 0})
        ]),
        html.Div(style={
            "backgroundColor": "#f8f9fa",
            "padding": "15px",
            "borderRadius": "10px",
            "boxShadow": "0px 4px 6px rgba(0,0,0,0.1)",
            "flex": "1",
            "minWidth": "250px"
        }, children=[
            html.H3("Most Common Answer", style={"textAlign": "center", "marginBottom": "10px"}),
            html.P(f"{most_common_answer}", style={"textAlign": "center", "fontSize": "24px", "margin": 0})
        ]),
        html.Div(style={
            "backgroundColor": "#f8f9fa",
            "padding": "15px",
            "borderRadius": "10px",
            "boxShadow": "0px 4px 6px rgba(0,0,0,0.1)",
            "flex": "1",
            "minWidth": "250px"
        }, children=[
            html.H3("Unique Answers", style={"textAlign": "center", "marginBottom": "10px"}),
            html.P(f"{unique_answers}", style={"textAlign": "center", "fontSize": "24px", "margin": 0})
        ])
    ]

    return cards


# Callback for charts
@app.callback(
    Output('charts-container', 'children'),
    [Input('section-dropdown', 'value'),
     Input('question-dropdown', 'value'),
     Input('grade-level-dropdown', 'value'),
     Input('major-dropdown', 'value')]
)
def update_charts(selected_section, selected_question, selected_grade, selected_major):
    if not selected_question:
        return html.Div("Please select a question to display charts.")

    # Filter data based on all selections
    filtered_df = df[(df['Section'] == selected_section) &
                     (df['Question'] == selected_question)]

    if selected_grade != 'All':
        filtered_df = filtered_df[filtered_df['College Grade Level'] == selected_grade]
    if selected_major != 'All':
        filtered_df = filtered_df[filtered_df['Major/Field of Study'] == selected_major]

    # Pie Chart
    pie_data = filtered_df['Answer'].value_counts().reset_index()
    pie_data.columns = ['Answer', 'Count']
    pie_chart = dcc.Graph(
        figure=px.pie(pie_data, values='Count', names='Answer',
                      title=f'Distribution of Answers: {selected_question}',
                      color_discrete_sequence=color_palette),
        config={'responsive': True},
        style={'height': "50%", "width": "100%", "display": "block"}
    )

    # Stacked Bar Chart by Grade Level
    grade_data = filtered_df.groupby(['College Grade Level', 'Answer']).size().reset_index(name='Count')
    grade_bar_chart = dcc.Graph(
        figure=px.bar(grade_data, x='Answer', y='Count', color='College Grade Level',
                      title=f'Answers by Grade Level: {selected_question}',
                      barmode='stack',
                      color_discrete_sequence=color_palette),
        config={'responsive': True},
        style={'height': "50%", "width": "100%", "display": "block"}
    )

    # Stacked Bar Chart by Major
    major_data = filtered_df.groupby(['Major/Field of Study', 'Answer']).size().reset_index(name='Count')
    major_bar_chart = dcc.Graph(
        figure=px.bar(major_data, x='Answer', y='Count', color='Major/Field of Study',
                      title=f'Answers by Major: {selected_question}',
                      barmode='stack',
                      color_discrete_sequence=color_palette),
        config={'responsive': True},
        style={'height': "50%", "width": "100%", "display": "block"}
    )

    return html.Div([
        pie_chart,
        grade_bar_chart,
        major_bar_chart
    ])


# Run app
if __name__ == '__main__':
    app.run(debug=False)

# from dash import dcc, html
# from dash.dependencies import Input, Output
# import plotly.express as px
# import pandas as pd
# import dash
#
# # Read data from the provided CSV file
# df = pd.read_csv('1_Academic_Background.csv')
#
# # Count majors
# majors_count = df['Q1: Major/Field of Study'].value_counts().reset_index()
# majors_count.columns = ['Major', 'Count']
#
# # Count grade levels
# grade_levels_count = df['Q2: College Grade Level'].value_counts().reset_index()
# grade_levels_count.columns = ['Grade Level', 'Count']
#
# # Create Dash app
# app = dash.Dash(__name__)
#
# # Layout
# app.layout = html.Div(style={'font-family': 'Arial', 'padding': '20px'}, children=[
#     # Header Section
#     html.Div(style={'backgroundColor': '#343a40', 'padding': '20px', 'color': '#ffffff'}, children=[
#         html.H1('Survey Analysis Dashboard', style={'textAlign': 'center'}),
#         html.P('Explore survey data related to majors, grade levels, and previous courses.',
#                style={'textAlign': 'center'})
#     ]),
#
#     # Main Content Section
#     html.Div(style={'display': 'flex', 'marginTop': '20px'}, children=[
#         # Filters Section (Left Sidebar)
#         html.Div(style={'width': '25%', 'padding': '20px', 'backgroundColor': '#f8f9fa',
#                         'borderRadius': '10px', 'boxShadow': '0px 4px 6px rgba(0,0,0,0.1)'}, children=[
#             html.H3('Filters'),
#             html.Label('Select Major:'),
#             dcc.Dropdown(
#                 id='major-dropdown',
#                 options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in
#                                                               df['Q1: Major/Field of Study'].unique()],
#                 value='All',
#                 style={'marginBottom': '20px'}
#             ),
#             html.Label('Select Grade Level:'),
#             dcc.Dropdown(
#                 id='grade-level-dropdown',
#                 options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in
#                                                               df['Q2: College Grade Level'].unique()],
#                 value='All'
#             )
#         ]),
#
#         # Charts Section (Right)
#         html.Div(style={'width': '75%', 'paddingLeft': '20px'}, children=[
#             html.Div(style={'display': 'flex',
#                             'justifyContent': 'space-between',
#                             'alignItems': 'center',
#                             'flexWrap': 'wrap'}, children=[
#                 # Bar Chart for Majors
#                 html.Div(style={'flexGrow': 1,
#                                 'minWidth': '48%',
#                                 'backgroundColor': '#ffffff',
#                                 'padding': '10px',
#                                 'borderRadius': '10px',
#                                 'boxShadow': '0px 4px 6px rgba(0,0,0,0.1)'}, children=[
#                     dcc.Graph(id='majors-graph', config={
#                         "displayModeBar": True,
#                         "responsive": True,
#                         "scrollZoom": True,
#                         "showTips": True,
#                     }, figure=px.bar(majors_count, x='Major', y='Count', title='Distribution of Majors'))
#                 ]),
#
#                 # Pie Chart for Grade Levels
#                 html.Div(style={'flexGrow': 1,
#                                 'minWidth': '48%',
#                                 'backgroundColor': '#ffffff',
#                                 'padding': '10px',
#                                 'borderRadius': '10px',
#                                 'boxShadow': '0px 4px 6px rgba(0,0,0,0.1)'}, children=[
#                     dcc.Graph(id='grade-levels-graph', config={
#                         "displayModeBar": True,
#                         "responsive": True,
#                         "scrollZoom": True,
#                         "showTips": True,
#                     }, figure=px.pie(grade_levels_count, values='Count', names='Grade Level',
#                                      title='Distribution of Grade Levels'))
#                 ]),
#             ]),
#
#             # Table for previous courses
#             html.Div(style={'marginTop': '20px'}, children=[
#                 html.H3('Previous Courses Taken'),
#                 html.Div(id='previous-courses-table', style={'overflowY': 'scroll', 'height': '200px'})
#             ]),
#
#         ])
#     ])
# ])
#
#
# # Callback to display previous courses table
# @app.callback(
#     Output('previous-courses-table', 'children'),
#     [Input('major-dropdown', 'value')]
# )
# def display_previous_courses(major):
#     if major == 'All':
#         filtered_df = df
#     else:
#         filtered_df = df[df['Q1: Major/Field of Study'] == major]
#
#     return html.Div(style={'backgroundColor': '#f0f0f0', 'padding': '10px', 'borderRadius': '10px',
#                            'boxShadow': '0px 4px 6px rgba(0,0,0,0.1)'}, children=[
#         html.Table(style={'width': '100%', 'border-collapse': 'collapse'}, children=[
#             html.Thead(
#                 html.Tr(
#                     [html.Th(col, style={'border': '1px solid #ddd', 'padding': '8px'}) for col in filtered_df.columns])
#             ),
#             html.Tbody([
#                 html.Tr([
#                     html.Td(filtered_df.iloc[i][col], style={'border': '1px solid #ddd', 'padding': '8px'}) for col in
#                     filtered_df.columns
#                 ]) for i in range(len(filtered_df))
#             ])
#         ])
#     ])
#
#
#
# # Run app
# if __name__ == '__main__':
#     app.run(debug=True)