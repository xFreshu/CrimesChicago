from dash import html, dcc, Output, Input, State, callback_context, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.figure_factory as ff
from scipy import stats
import numpy as np
import os

# Konfiguracja ścieżek
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
DB_PATH = os.path.join(project_root, 'scripts', 'chicago_crimes.db')


def query_correlations(year_filter=None):
    try:
        conn = sqlite3.connect(DB_PATH)

        # 1. Czas i przestępczość
        time_query = """
        SELECT 
            Hour,
            COUNT(*) as hourly_count,
            SUM(CASE WHEN Arrest = 1 THEN 1 ELSE 0 END) as arrests,
            strftime('%w', Date) as day_of_week,
            Month,
            Year
        FROM ChicagoCrimes
        WHERE 1=1
        """

        # 2. Typ przestępstwa a lokalizacja
        location_query = """
        SELECT 
            PrimaryType,
            LocationDescription,
            District,
            Ward,
            CommunityArea,
            COUNT(*) as count
        FROM ChicagoCrimes
        WHERE 1=1
        """

        # 3. Analiza egzekwowania prawa
        law_enforcement_query = """
        SELECT 
            District,
            Beat,
            PrimaryType,
            COUNT(*) as total_crimes,
            SUM(CASE WHEN Arrest = 1 THEN 1 ELSE 0 END) as arrests,
            CAST(SUM(CASE WHEN Arrest = 1 THEN 1 ELSE 0 END) AS FLOAT) / 
            COUNT(*) as arrest_rate
        FROM ChicagoCrimes
        WHERE 1=1
        """

        if isinstance(year_filter, tuple):
            time_query += f" AND Year BETWEEN {year_filter[0]} AND {year_filter[1]}"
            location_query += f" AND Year BETWEEN {year_filter[0]} AND {year_filter[1]}"
            law_enforcement_query += f" AND Year BETWEEN {year_filter[0]} AND {year_filter[1]}"
        elif year_filter:
            time_query += f" AND Year = {year_filter}"
            location_query += f" AND Year = {year_filter}"
            law_enforcement_query += f" AND Year = {year_filter}"

        time_query += " GROUP BY Hour, day_of_week, Month, Year"
        location_query += " GROUP BY PrimaryType, LocationDescription, District, Ward, CommunityArea"
        law_enforcement_query += " GROUP BY District, Beat, PrimaryType"

        df_time = pd.read_sql_query(time_query, conn)
        df_location = pd.read_sql_query(location_query, conn)
        df_law = pd.read_sql_query(law_enforcement_query, conn)

        conn.close()
        return df_time, df_location, df_law

    except sqlite3.OperationalError as e:
        print(f"Błąd bazy danych: {e}")
        return None, None, None


def create_skeleton_loading():
    return dbc.Container([
        dbc.Row([
            dbc.Col(dbc.Card(className="mb-4", children=[
                html.Div(style={
                    "height": "400px",
                    "background": "linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)",
                    "backgroundSize": "1000px 100%",
                    "animation": "shimmer 2s infinite linear"
                })
            ]), width=12)
        ]) for _ in range(3)
    ])


def create_year_selector():
    return dbc.Card(
        dbc.CardBody([
            html.H4("Wybór okresu analizy", className="mb-3"),
            dcc.RadioItems(
                id='stats-date-range-type',
                options=[
                    {'label': ' Jeden rok', 'value': 'single'},
                    {'label': ' Zakres lat', 'value': 'range'}
                ],
                value='single',
                className="mb-3"
            ),
            html.Div([
                html.Div(
                    id='stats-single-year-container',
                    children=[
                        dcc.Dropdown(
                            id='stats-single-year-dropdown',
                            options=[{'label': str(year), 'value': year}
                                     for year in range(2008, 2018)],
                            value=2008,
                            placeholder="Wybierz rok"
                        )
                    ]
                ),
                html.Div(
                    id='stats-year-range-container',
                    style={'display': 'none'},
                    children=[
                        dcc.RangeSlider(
                            id='stats-year-range-slider',
                            min=2008,
                            max=2017,
                            step=1,
                            value=[2008, 2017],
                            marks={str(year): str(year)
                                   for year in range(2008, 2018)}
                        )
                    ]
                )
            ]),
            dbc.Button(
                "Generuj diagramy",
                id="stats-generate-button",
                color="primary",
                className="mt-3 w-100"
            )
        ]),
        className="mb-4"
    )


def create_time_correlation_analysis(df_time):
    df_time['day_of_week'] = pd.to_numeric(df_time['day_of_week'])
    days = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela']

    hourly_trend = px.line(
        df_time.groupby('Hour')['hourly_count'].mean().reset_index(),
        x='Hour',
        y='hourly_count',
        title='Rozkład przestępstw w ciągu doby',
        labels={'hourly_count': 'Średnia liczba przestępstw', 'Hour': 'Godzina'}
    )
    hourly_trend.update_layout(template="plotly_white")

    weekly_trend = px.bar(
        df_time.groupby('day_of_week')['hourly_count'].mean().reset_index(),
        x='day_of_week',
        y='hourly_count',
        title='Rozkład przestępstw w ciągu tygodnia',
        labels={'hourly_count': 'Średnia liczba przestępstw', 'day_of_week': 'Dzień tygodnia'}
    )
    weekly_trend.update_xaxes(ticktext=days, tickvals=list(range(7)))
    weekly_trend.update_layout(template="plotly_white")

    return hourly_trend, weekly_trend


def create_law_enforcement_analysis(df_law):
    arrest_rate = px.bar(
        df_law.groupby('District')['arrest_rate'].mean().reset_index(),
        x='District',
        y='arrest_rate',
        title='Wskaźnik aresztowań według dystryktu',
        labels={'arrest_rate': 'Wskaźnik aresztowań', 'District': 'Dystrykt'}
    )
    arrest_rate.update_layout(template="plotly_white")

    crime_arrest_rate = px.bar(
        df_law.groupby('PrimaryType').agg({
            'total_crimes': 'sum',
            'arrests': 'sum'
        }).reset_index().nlargest(10, 'total_crimes'),
        x='PrimaryType',
        y=['total_crimes', 'arrests'],
        title='Przestępstwa vs Aresztowania według typu',
        barmode='group',
        labels={
            'total_crimes': 'Całkowita liczba przestępstw',
            'arrests': 'Liczba aresztowań',
            'PrimaryType': 'Typ przestępstwa'
        }
    )
    crime_arrest_rate.update_layout(template="plotly_white")

    return arrest_rate, crime_arrest_rate


def create_correlation_dashboard(df_time, df_location, df_law):
    hourly_trend, weekly_trend = create_time_correlation_analysis(df_time)
    arrest_rate, crime_arrest_rate = create_law_enforcement_analysis(df_law)

    return dbc.Container([
        html.H3("1. Analiza czasowa przestępczości", className="mt-4 mb-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=hourly_trend), width=12),
            dbc.Col(dcc.Graph(figure=weekly_trend), width=12)
        ], className="mb-4"),

        html.H3("2. Analiza egzekwowania prawa", className="mt-4 mb-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=arrest_rate), width=12),
            dbc.Col(dcc.Graph(figure=crime_arrest_rate), width=12)
        ], className="mb-4")
    ])


def layout():
    return html.Div([
        html.H1("Analiza Statystyczna", className="mb-4 text-center"),
        dbc.Row([
            dbc.Col(create_year_selector(), width=12)
        ]),
        html.Div(id="stats-content")
    ])


def register_callbacks(app):
    @app.callback(
        [Output('stats-year-range-container', 'style'),
         Output('stats-single-year-container', 'style')],
        Input('stats-date-range-type', 'value')
    )
    def toggle_year_selector(selector_type):
        if selector_type == 'range':
            return {'display': 'block'}, {'display': 'none'}
        return {'display': 'none'}, {'display': 'block'}

    @app.callback(
        Output("stats-content", "children"),
        [Input("stats-generate-button", "n_clicks")],
        [State("stats-single-year-dropdown", "value"),
         State("stats-year-range-slider", "value"),
         State("stats-date-range-type", "value")]
    )
    def update_correlations(n_clicks, single_year, year_range, range_type):
        if n_clicks is None:
            return html.Div()
        return create_skeleton_loading()

    @app.callback(
        Output("stats-content", "children", allow_duplicate=True),
        [Input("stats-content", "children")],
        [State("stats-single-year-dropdown", "value"),
         State("stats-year-range-slider", "value"),
         State("stats-date-range-type", "value")],
        prevent_initial_call=True
    )
    def load_correlation_data(_, single_year, year_range, range_type):
        year_filter = None
        if range_type == 'single':
            year_filter = single_year
        else:
            year_filter = tuple(year_range)

        df_time, df_location, df_law = query_correlations(year_filter)

        if df_time is None:
            return dbc.Alert(
                "Błąd podczas pobierania danych.",
                color="danger",
                className="mt-3"
            )

        return create_correlation_dashboard(df_time, df_location, df_law)
