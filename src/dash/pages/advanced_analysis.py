from dash import html, dcc, Input, Output, State, callback_context, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
import os

# Konfiguracja ścieżek
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
DB_PATH = os.path.join(project_root, 'scripts', 'chicago_crimes.db')


def query_database(year_filter=None):
    """
    Pobiera dane z bazy SQLite z opcjonalnym filtrem roku
    """
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

        base_query += """ 
        GROUP BY Year, Month, PrimaryType
        ORDER BY Year, Month
        """

        df = pd.read_sql_query(base_query, conn)
        conn.close()
        return df
    except sqlite3.OperationalError as e:
        print(f"Błąd bazy danych: {e}")
        return pd.DataFrame()


def create_skeleton_loading():
    """
    Tworzy animowany wskaźnik ładowania
    """
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


def create_arima_controls():
    """
    Tworzy kontrolki do parametrów modelu ARIMA
    """
    return dbc.Card(
        dbc.CardBody([
            html.H4("Parametry modelu ARIMA", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("p (autoregresja)"),
                    dcc.Slider(
                        id='arima-p',
                        min=0,
                        max=3,
                        step=1,
                        value=1,
                        marks={i: str(i) for i in range(4)},
                        className="mb-3"
                    )
                ], width=4),
                dbc.Col([
                    html.Label("d (różnicowanie)"),
                    dcc.Slider(
                        id='arima-d',
                        min=0,
                        max=2,
                        step=1,
                        value=1,
                        marks={i: str(i) for i in range(3)},
                        className="mb-3"
                    )
                ], width=4),
                dbc.Col([
                    html.Label("q (średnia ruchoma)"),
                    dcc.Slider(
                        id='arima-q',
                        min=0,
                        max=3,
                        step=1,
                        value=1,
                        marks={i: str(i) for i in range(4)},
                        className="mb-3"
                    )
                ], width=4)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Aktualizuj model",
                        id="update-arima-button",
                        color="primary",
                        className="w-100"
                    )
                ])
            ])
        ]),
        className="mb-4"
    )


def create_year_selector():
    """
    Tworzy selektor zakresu lat
    """
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
                        )
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
            ])
        ]),
        className="mb-4"
    )


def create_time_series_analysis(df, p=1, d=1, q=1):
    """
    Tworzy analizę szeregów czasowych z prognozą ARIMA
    """
    # Przygotowanie danych
    df_ts = df.groupby(['Year', 'Month'])['count'].sum().reset_index()
    df_ts['date'] = pd.to_datetime(df_ts['Year'].astype(str) + '-' + df_ts['Month'].astype(str) + '-01')
    df_ts = df_ts.set_index('date').sort_index()

    try:
        # Model ARIMA
        model = ARIMA(df_ts['count'], order=(p, d, q))
        model_fit = model.fit()

        # Prognoza z przedziałami ufności
        forecast = model_fit.get_forecast(steps=12)
        forecast_mean = forecast.predicted_mean
        forecast_ci = forecast.conf_int()

        # Tworzenie wykresu
        fig = go.Figure()

        # Dane historyczne
        fig.add_trace(go.Scatter(
            x=df_ts.index,
            y=df_ts['count'],
            name='Dane historyczne',
            line=dict(color='#2ecc71')
        ))

        # Prognoza
        fig.add_trace(go.Scatter(
            x=forecast_mean.index,
            y=forecast_mean,
            name='Prognoza',
            line=dict(color='purple', dash='dash')
        ))

        # Przedziały ufności
        fig.add_trace(go.Scatter(
            x=forecast_ci.index,
            y=forecast_ci.iloc[:, 0],
            fill=None,
            mode='lines',
            line=dict(color='rgba(128, 0, 128, 0)'),
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=forecast_ci.index,
            y=forecast_ci.iloc[:, 1],
            fill='tonexty',
            mode='lines',
            line=dict(color='rgba(128, 0, 128, 0)'),
            name='Przedział ufności 95%',
            fillcolor='rgba(128, 0, 128, 0.2)'
        ))

        # Ustawienia wykresu
        fig.update_layout(
            title=f'Analiza szeregów czasowych z prognozą ARIMA({p},{d},{q})',
            xaxis_title="Data",
            yaxis_title="Liczba przestępstw",
            height=500,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )

        # Metryki modelu
        aic = model_fit.aic
        bic = model_fit.bic

        metrics_div = html.Div([
            html.H5("Metryki modelu:", className="mt-3"),
            html.Ul([
                html.Li(f"AIC: {aic:.2f}"),
                html.Li(f"BIC: {bic:.2f}")
            ])
        ])

        return dbc.Card([
            dbc.CardBody([
                dcc.Graph(figure=fig),
                metrics_div
            ])
        ])

    except Exception as e:
        return dbc.Alert(
            f"Błąd w tworzeniu modelu ARIMA: {str(e)}",
            color="danger",
            className="mt-3"
        )


def layout():
    """
    Główny układ aplikacji
    """
    return html.Div([
        html.H1("Zaawansowana Analiza Danych", className="mb-4 text-center"),
        dbc.Row([
            dbc.Col(create_year_selector(), width=12),
            dbc.Col(create_arima_controls(), width=12)
        ]),
        html.Div(id="advanced-content")
    ])


def register_callbacks(app):
    """
    Rejestruje callbacki aplikacji
    """

    @app.callback(
        [Output('advanced-year-range-container', 'style'),
         Output('advanced-single-year-container', 'style')],
        Input('advanced-date-range-type', 'value')
    )
    def toggle_year_selector(selector_type):
        if selector_type == 'range':
            return {'display': 'block'}, {'display': 'none'}
        return {'display': 'none'}, {'display': 'block'}

    @app.callback(
        Output("advanced-content", "children"),
        [Input("update-arima-button", "n_clicks")],
        [State("advanced-single-year-dropdown", "value"),
         State("advanced-year-range-slider", "value"),
         State("advanced-date-range-type", "value"),
         State("arima-p", "value"),
         State("arima-d", "value"),
         State("arima-q", "value")],
        prevent_initial_call=True
    )
    def show_loading_state(n_clicks, single_year, year_range, range_type, p, d, q):
        if n_clicks is None:
            return html.Div()
        return create_skeleton_loading()

    @app.callback(
        Output("advanced-content", "children", allow_duplicate=True),
        [Input("advanced-content", "children")],
        [State("advanced-single-year-dropdown", "value"),
         State("advanced-year-range-slider", "value"),
         State("advanced-date-range-type", "value"),
         State("arima-p", "value"),
         State("arima-d", "value"),
         State("arima-q", "value")],
        prevent_initial_call=True
    )
    def update_analysis(_, single_year, year_range, range_type, p, d, q):
        year_filter = None
        if range_type == 'single':
            year_filter = single_year
        else:
            year_filter = tuple(year_range)

        df = query_database(year_filter)

        if df.empty:
            return dbc.Alert(
                "Brak danych dla wybranego okresu.",
                color="warning",
                className="mt-3"
            )

        return create_time_series_analysis(df, p, d, q)
