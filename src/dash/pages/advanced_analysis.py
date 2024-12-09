from dash import html, dcc, Input, Output, State, callback_context, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
import plotly.express as px
from statsmodels.tsa.arima.model import ARIMA
from pyspark.sql import SparkSession
import os

# Konfiguracja ścieżek
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
DB_PATH = os.path.join(project_root, 'scripts', 'chicago_crimes.db')


def query_database(year_filter=None, month=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        base_query = """
        SELECT 
            Year, Month, PrimaryType, COUNT(*) as count
        FROM ChicagoCrimes
        WHERE 1=1
        """

        if isinstance(year_filter, tuple):
            base_query += f" AND Year >= {year_filter[0]} AND Year <= {year_filter[1]}"
        elif year_filter:
            base_query += f" AND Year = {year_filter}"

        if month and month != 'all':
            base_query += f" AND Month = {month}"

        base_query += """ 
        GROUP BY Year, Month, PrimaryType
        ORDER BY Year, Month
        """

        df = pd.read_sql_query(base_query, conn)
        conn.close()
        return df
    except sqlite3.OperationalError as e:
        print(f"Błąd bazy danych: {e}")
        print(f"Zapytanie: {base_query}")
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
                    })
                ]),
                width=12
            )
        ]),
        dbc.Row([
            dbc.Col(
                dbc.Card(className="mb-4", children=[
                    html.Div(style={
                        "height": "300px",
                        "background": "linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)",
                        "backgroundSize": "1000px 100%",
                        "animation": "shimmer 2s infinite linear"
                    })
                ]),
                width=12
            ) for _ in range(2)
        ])
    ])


def create_year_selector():
    return dbc.Card(
        dbc.CardBody([
            html.H4("Wybór okresu analizy", className="mb-3"),
            dcc.RadioItems(
                id='advanced-date-range-type',
                options=[
                    {'label': ' Jeden rok', 'value': 'single'},
                    {'label': ' Zakres lat', 'value': 'range'}
                ],
                value='single',
                className="mb-3"
            ),
            html.Div([
                html.Div(
                    id='advanced-single-year-container',
                    children=[
                        dcc.Dropdown(
                            id='advanced-single-year-dropdown',
                            options=[{'label': str(year), 'value': year}
                                     for year in range(2008, 2016)],
                            value=2008,
                            placeholder="Wybierz rok"
                        ),
                        html.Div([
                            html.P("Wybierz miesiąc (opcjonalnie):", className="mt-3"),
                            dcc.Dropdown(
                                id='advanced-month-dropdown',
                                options=[
                                    {'label': 'Wszystkie miesiące', 'value': 'all'},
                                    {'label': 'Styczeń', 'value': 1},
                                    {'label': 'Luty', 'value': 2},
                                    {'label': 'Marzec', 'value': 3},
                                    {'label': 'Kwiecień', 'value': 4},
                                    {'label': 'Maj', 'value': 5},
                                    {'label': 'Czerwiec', 'value': 6},
                                    {'label': 'Lipiec', 'value': 7},
                                    {'label': 'Sierpień', 'value': 8},
                                    {'label': 'Wrzesień', 'value': 9},
                                    {'label': 'Październik', 'value': 10},
                                    {'label': 'Listopad', 'value': 11},
                                    {'label': 'Grudzień', 'value': 12}
                                ],
                                value='all',
                                placeholder="Wybierz miesiąc"
                            )
                        ], className="mt-2")
                    ]
                ),
                html.Div(
                    id='advanced-year-range-container',
                    style={'display': 'none'},
                    children=[
                        html.P("Wybierz zakres lat:", className="mt-3"),
                        dcc.RangeSlider(
                            id='advanced-year-range-slider',
                            min=2008,
                            max=2016,
                            step=1,
                            value=[2008, 2016],
                            marks={str(year): str(year)
                                   for year in range(2008, 2016)}
                        )
                    ]
                )
            ]),
            dbc.Button(
                "Generuj analizę zaawansowaną",
                id="advanced-generate-button",
                color="primary",
                className="mt-3 w-100"
            )
        ]),
        className="mb-4"
    )


def create_time_series_analysis(df):
    df_ts = df.groupby(['Year', 'Month'])['count'].sum().reset_index()
    df_ts['date'] = pd.to_datetime(df_ts['Year'].astype(str) + '-' + df_ts['Month'].astype(str) + '-01')
    df_ts = df_ts.set_index('date').sort_index()

    model = ARIMA(df_ts['count'], order=(1, 1, 1))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=12)

    # Tworzenie wykresu z jedną linią dla danych rzeczywistych
    fig = px.line(
        df_ts,
        y='count',
        title='Analiza szeregów czasowych z prognozą',
        template='plotly_white'
    )

    # Dodanie linii prognozy
    fig.add_scatter(
        x=forecast.index,
        y=forecast,
        mode='lines',
        name='Prognoza',
        line=dict(dash='dash', color='purple')
    )

    # Konfiguracja layoutu
    fig.update_layout(
        height=500,
        xaxis_title="Data",
        yaxis_title="Liczba przestępstw",
        showlegend=True,
        # Ustawienie kolorów i legendy
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    # Aktualizacja pierwszej linii (dane rzeczywiste)
    fig.data[0].update(name='Liczba przestępstw', line=dict(color='#2ecc71'))

    return dcc.Graph(figure=fig)


def create_crime_type_analysis(df):
    fig = px.bar(
        df.groupby('PrimaryType')['count'].sum().reset_index().sort_values('count', ascending=False).head(10),
        x='PrimaryType',
        y='count',
        title='Top 10 typów przestępstw',
        template='plotly_white'
    )

    fig.update_layout(
        height=400,
        xaxis_title="Typ przestępstwa",
        yaxis_title="Liczba przypadków"
    )

    return dcc.Graph(figure=fig)


def create_monthly_patterns(df):
    monthly_avg = df.groupby('Month')['count'].mean().reset_index()

    fig = px.line(
        monthly_avg,
        x='Month',
        y='count',
        title='Średnia liczba przestępstw w miesiącach',
        template='plotly_white'
    )

    fig.update_xaxes(
        ticktext=['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
                  'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'],
        tickvals=list(range(1, 13))
    )

    fig.update_layout(
        height=400,
        xaxis_title="Miesiąc",
        yaxis_title="Średnia liczba przestępstw"
    )

    return dcc.Graph(figure=fig)


def layout():
    return html.Div([
        html.H1("Zaawansowana Analiza Danych", className="mb-4 text-center"),
        dbc.Row([
            dbc.Col(create_year_selector(), width=12)
        ]),
        html.Div(id="advanced-content")
    ])


def register_callbacks(app):
    @app.callback(
        [Output('advanced-year-range-container', 'style'),
         Output('advanced-single-year-container', 'style'),
         Output('advanced-month-dropdown', 'disabled')],
        Input('advanced-date-range-type', 'value')
    )
    def toggle_year_selector(selector_type):
        if selector_type == 'range':
            return {'display': 'block'}, {'display': 'none'}, True
        return {'display': 'none'}, {'display': 'block'}, False

    @app.callback(
        Output("advanced-content", "children"),
        [Input("advanced-generate-button", "n_clicks")],
        [State("advanced-single-year-dropdown", "value"),
         State("advanced-year-range-slider", "value"),
         State("advanced-date-range-type", "value"),
         State("advanced-month-dropdown", "value")]
    )
    def update_analysis(n_clicks, single_year, year_range, range_type, month):
        if n_clicks is None:
            return html.Div()

        return create_skeleton_loading()

    @app.callback(
        Output("advanced-content", "children", allow_duplicate=True),
        [Input("advanced-content", "children")],
        [State("advanced-single-year-dropdown", "value"),
         State("advanced-year-range-slider", "value"),
         State("advanced-date-range-type", "value"),
         State("advanced-month-dropdown", "value")],
        prevent_initial_call=True
    )
    def load_data(_, single_year, year_range, range_type, month):
        year_filter = None
        if range_type == 'single':
            year_filter = single_year
        else:
            year_filter = tuple(year_range)

        df = query_database(year_filter, month)

        if df.empty:
            return dbc.Alert(
                "Brak danych dla wybranego okresu.",
                color="warning",
                className="mt-3"
            )

        return dbc.Container([
            dbc.Row([
                dbc.Col(create_time_series_analysis(df), width=12)
            ], className="mb-4"),
            dbc.Row([
                dbc.Col(create_crime_type_analysis(df), width=12)
            ], className="mb-4"),
            dbc.Row([
                dbc.Col(create_monthly_patterns(df), width=12)
            ])
        ])
