from dash import Dash, dcc, html, Input, Output, State, ctx, ALL
import plotly.express as px
import pandas as pd

# Read data from the provided CSV file
df = pd.read_csv('https://raw.githubusercontent.com/DS4Ag/agr333s/refs/heads/main/data/survey_db.csv')

# Create Dash app
app = Dash(__name__)

# Define a professional color palette
color_palette = px.colors.qualitative.Safe

# Global font sizes and layout settings
FONT_SIZES = {
    "title": 16,
    "axis_title": 16,
    "tick_labels": 16,
    "legend": 16
}

GLOBAL_LAYOUT = {
    "title": dict(font=dict(size=FONT_SIZES["title"])),
    "xaxis": dict(
        title=dict(font=dict(size=FONT_SIZES["axis_title"])),
        tickfont=dict(size=FONT_SIZES["tick_labels"])
    ),
    "yaxis": dict(
        title=dict(font=dict(size=FONT_SIZES["axis_title"])),
        tickfont=dict(size=FONT_SIZES["tick_labels"])
    ),
    "legend": dict(font=dict(size=FONT_SIZES["legend"])),
    "margin": dict(l=20, r=20, t=40, b=20)
}

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
                        'borderRadius': '10px', 'boxShadow': '0px 4px 6px rgba(0,0,0,0.1)','marginBottom': '10px'}, children=[
            html.H3('Required Filters'),
            html.Label('Select Section:'),
            dcc.Dropdown(
                id='section-dropdown',
                options=[{'label': i, 'value': i} for i in df['Section'].unique()] + [{'label': '', 'value': ''}],
                value=df['Section'].unique()[0],
                style={'marginBottom': '20px'}
            ),

            html.Div(style={"height": "50px"}),

            html.Label('Select Question:'),
            html.Div(id='question-buttons-container', style={
                "display": "flex",
                "flexDirection": "column",
                "gap": "10px"
            }),
            html.Hr(style={'borderWidth': '1px', 'borderColor': '#ccc', 'marginTop': '30px'}),
            html.H3('Optional Filters', style={'fontSize': '18px'}),
            html.Label('Select Grade Level:', style={'fontSize': '14px'}),
            dcc.Dropdown(
                id='grade-level-dropdown',
                options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in
                                                              df['College Grade Level'].unique()]+ [{'label': '', 'value': ''}],
                value='All',
                style={'marginBottom': '20px'}
            ),
            html.Label('Select Major:', style={'fontSize': '14px'}),
            dcc.Dropdown(
                id='major-dropdown',
                options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in
                                                              df['Major/Field of Study'].unique()]+ [{'label': '', 'value': ''}],
                value='All'
            ),

            # Spacer Div
            html.Div(style={"height": "100px"})  # Adds 100 pixels of space below the menu

        ]),

        # Charts Section
        html.Div(style={'width': '75%', 'paddingLeft': '20px'}, children=[
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
            dcc.Loading(
                id="loading-graphs",
                type="circle",
                children=html.Div(id='charts-container', style={
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "30px",
                    "width": "100%"
                })
            )
        ])
    ])
])


# Generate question buttons based on section
@app.callback(
    Output('question-buttons-container', 'children'),
    Input('section-dropdown', 'value')
)
def generate_question_buttons(selected_section):
    questions = df[df['Section'] == selected_section]['Question'].unique()
    return [
        html.Button(
            question,
            id={'type': 'question-button', 'index': i},
            n_clicks=0,
            style={
                "backgroundColor": "#f8f9fa",
                "border": "1px solid #ccc",
                "borderRadius": "5px",
                "padding": "10px",
                "cursor": "pointer",
                "textAlign": "center"
            }
        ) for i, question in enumerate(questions)
    ]


# Update summary cards
@app.callback(
    Output('summary-cards-container', 'children'),
    Input({'type': 'question-button', 'index': ALL}, 'n_clicks'),
    [State('section-dropdown', 'value'),
     State('grade-level-dropdown', 'value'),
     State('major-dropdown', 'value')]
)
def update_summary_cards(_, selected_section, selected_grade, selected_major):
    if not ctx.triggered:
        return []

    # Get selected question
    triggered_id = ctx.triggered_id
    question_index = triggered_id['index']
    questions = df[df['Section'] == selected_section]['Question'].unique()
    selected_question = questions[question_index]

    # Filter data
    filtered_df = df[
        (df['Section'] == selected_section) &
        (df['Question'] == selected_question)
        ]
    if selected_grade != 'All':
        filtered_df = filtered_df[filtered_df['College Grade Level'] == selected_grade]
    if selected_major != 'All':
        filtered_df = filtered_df[filtered_df['Major/Field of Study'] == selected_major]

    # Calculate metrics
    total_responses = len(filtered_df)
    answer_counts = filtered_df['Answer'].value_counts()
    most_common = answer_counts.idxmax() if not answer_counts.empty else "N/A"
    unique_answers = len(answer_counts)

    # Create cards
    return [
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
            html.P(f"{most_common}", style={"textAlign": "center", "fontSize": "24px", "margin": 0})
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


@app.callback(
    Output('charts-container', 'children'),
    Input({'type': 'question-button', 'index': ALL}, 'n_clicks'),
    [State('section-dropdown', 'value'),
     State('grade-level-dropdown', 'value'),
     State('major-dropdown', 'value')]
)
def update_charts(_, selected_section, selected_grade, selected_major):
    if not ctx.triggered:
        return [html.Div("Please select a question to display charts.")]

    # Get selected question
    triggered_id = ctx.triggered_id
    question_index = triggered_id['index']
    questions = df[df['Section'] == selected_section]['Question'].unique()
    selected_question = questions[question_index]

    # Filter data
    filtered_df = df[
        (df['Section'] == selected_section) &
        (df['Question'] == selected_question)
        ]
    if selected_grade != 'All':
        filtered_df = filtered_df[filtered_df['College Grade Level'] == selected_grade]
    if selected_major != 'All':
        filtered_df = filtered_df[filtered_df['Major/Field of Study'] == selected_major]

    # Get sorted answer order
    #answer_order = sorted(filtered_df['Answer'].unique())
    answer_order = sorted([str(ans) for ans in filtered_df['Answer'].dropna().unique()])

    # Pie Chart
    pie_data = filtered_df['Answer'].value_counts().reset_index()
    pie_data.columns = ['Answer', 'Count']

    pie_chart = dcc.Graph(
        figure=px.pie(
            pie_data,
            values='Count',
            names='Answer',
            title=f'Distribution of Answers: {selected_question}',
            #category_orders={'Answer': sorted(filtered_df['Answer'].unique())},
            category_orders={'Answer': sorted(filtered_df['Answer'].dropna().astype(str).unique())},
            color_discrete_sequence=color_palette
        ).update_traces(
            textinfo='percent',  # Show only percentages
            textfont=dict(size=FONT_SIZES["tick_labels"])  # Adjust font size for readability
        ).update_layout(**GLOBAL_LAYOUT),
        config={'responsive': True},
        style={'height': '50vh'}
    )
    # Grade Level Bar Chart
    grade_data = filtered_df.groupby(
        ['College Grade Level', 'Answer']
    ).size().reset_index(name='Count')
    grade_bar_chart = dcc.Graph(
        figure=px.bar(
            grade_data,
            x='Answer',
            y='Count',
            color='College Grade Level',
            title=f'Answers by Grade Level: {selected_question}',
            category_orders={'Answer': answer_order},
            barmode='stack',
            color_discrete_sequence=color_palette
        ).update_layout(**GLOBAL_LAYOUT),
        config={'responsive': True},
        style={'height': '50vh'}
    )

    # Major Bar Chart
    major_data = filtered_df.groupby(
        ['Major/Field of Study', 'Answer']
    ).size().reset_index(name='Count')
    major_bar_chart = dcc.Graph(
        figure=px.bar(
            major_data,
            x='Answer',
            y='Count',
            color='Major/Field of Study',
            title=f'Answers by Major: {selected_question}',
            category_orders={'Answer': answer_order},
            barmode='stack',
            color_discrete_sequence=color_palette
        ).update_layout(**GLOBAL_LAYOUT),
        config={'responsive': True},
        style={'height': '50vh'}
    )

    return [pie_chart, grade_bar_chart, major_bar_chart]

# # Run app
server = app.server

# Run app
# if __name__ == '__main__':
#     app.run(debug=True)