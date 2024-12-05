from dash import html, dcc, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
import plotly.express as px
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
DB_PATH = os.path.join(project_root, 'scripts', 'chicago_crimes.db')


def query_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT 
            Year, Month, PrimaryType, LocationDescription, Description,
            Arrest, Domestic, Beat, District, Ward, CommunityArea,
            Hour, COUNT(*) as count, 
            SUM(Arrest) as arrests
        FROM ChicagoCrimes
        GROUP BY Year, Month, PrimaryType, LocationDescription, Description,
                 Arrest, Domestic, Beat, District, Ward, CommunityArea, Hour
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except sqlite3.OperationalError as e:
        print(f"Error: {e} | Path: {DB_PATH}")
        return pd.DataFrame()


def create_skeleton_loading():
    return dbc.Container([
        dbc.Row([
            dbc.Col(
                dbc.Card(className="mb-4", children=[
                    html.Div(style={
                        "height": "400px",
                        "background": "linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)",
                        "backgroundSize": "1000px 100%",
                        "animation": "shimmer 2s infinite linear"
                    }),
                    html.Div(className="p-3", children=[
                        html.Div(style={
                            "height": "20px",
                            "width": "60%",
                            "background": "linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)",
                            "backgroundSize": "1000px 100%",
                            "animation": "shimmer 2s infinite linear",
                            "marginBottom": "10px"
                        }),
                        html.Div(style={
                            "height": "40px",
                            "background": "linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)",
                            "backgroundSize": "1000px 100%",
                            "animation": "shimmer 2s infinite linear"
                        })
                    ])
                ]),
                width=12
            )
        ]),
        dbc.Row([
            dbc.Col(
                [create_skeleton_chart("300px") for _ in range(2)],
                width=6
            ) for _ in range(2)
        ])
    ])


def create_skeleton_chart(height):
    return dbc.Card(
        className="mb-4",
        children=[
            html.Div(style={
                "height": height,
                "background": "linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)",
                "backgroundSize": "1000px 100%",
                "animation": "shimmer 2s infinite linear"
            }),
            html.Div(className="p-3", children=[
                html.Div(style={
                    "height": "15px",
                    "width": "70%",
                    "background": "linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)",
                    "backgroundSize": "1000px 100%",
                    "animation": "shimmer 2s infinite linear",
                    "marginBottom": "8px"
                })
            ])
        ]
    )


def create_insight_card(title, text):
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, className="mb-2"),
            html.P(text)
        ]),
        className="mb-4"
    )


def layout():
    return html.Div([
        html.H1("Analiza Przestępczości Chicago", className="mb-4 text-center"),
        html.Div(id="loading-graphs", children=create_skeleton_loading())
    ])


def create_charts(df):
    charts = {
        'time_trend': px.line(
            df.groupby(['Year', 'Month'])['count'].sum().reset_index(),
            x='Month', y='count', color='Year',
            title='Trend przestępczości'
        ).update_xaxes(
            tickmode='array',
            ticktext=['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
                      'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'],
            tickvals=list(range(1, 13))
        ),
        'hourly_trend': px.bar(
            df.groupby('Hour')['count'].sum().reset_index(),
            x='Hour', y='count',
            title='Rozkład przestępstw w ciągu doby'
        ),
        'location_dist': px.treemap(
            df.groupby('LocationDescription')['count'].sum().reset_index(),
            path=['LocationDescription'],
            values='count',
            title='Rozkład lokalizacji przestępstw'
        ),
        'arrest_stats': px.bar(
            df.groupby('PrimaryType').agg({'count': 'sum', 'arrests': 'sum'})
            .reset_index().nlargest(10, 'count'),
            x='PrimaryType', y=['count', 'arrests'],
            title='Przestępstwa vs Aresztowania',
            barmode='group'
        )
    }

    insights = {
        'time': "Analiza ujawnia wyraźne wzorce sezonowe w przestępczości, ze wzrostem w miesiącach letnich.",
        'hourly': "Największa liczba przestępstw występuje w godzinach popołudniowych i wieczornych.",
        'location': "Przestępstwa najczęściej mają miejsce na ulicach i w miejscach publicznych.",
        'arrests': "Skuteczność aresztowań różni się znacząco w zależności od typu przestępstwa."
    }

    return dbc.Container([
        dbc.Row(dbc.Col(dcc.Graph(figure=charts['time_trend']), width=12), className="mb-4"),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=charts['hourly_trend']),
                create_insight_card("Analiza godzinowa", insights['hourly'])
            ], width=6),
            dbc.Col([
                dcc.Graph(figure=charts['location_dist']),
                create_insight_card("Analiza lokalizacji", insights['location'])
            ], width=6)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=charts['arrest_stats']),
                create_insight_card("Skuteczność aresztowań", insights['arrests'])
            ], width=12)
        ])
    ])


def register_callbacks(app):
    @app.callback(
        Output("loading-graphs", "children"),
        Input("loading-graphs", "id")
    )
    def update_graphs(_):
        df = query_database()
        if df.empty:
            return dbc.Alert("Błąd dostępu do bazy danych.", color="danger")
        return create_charts(df)
