from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
import plotly.express as px
import os

# Konfiguracja ścieżek
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
DB_PATH = os.path.join(project_root, 'scripts', 'chicago_crimes.db')


# Funkcja do pobierania danych z bazy danych z opcjonalnym filtrem lat
def query_database(year_filter=None):
    """Pobieranie danych z bazy z opcjonalnym filtrem lat"""
    try:
        conn = sqlite3.connect(DB_PATH)
        base_query = """
        SELECT 
            Year, Month, PrimaryType, LocationDescription, Description,
            Arrest, Domestic, Beat, District, Ward, CommunityArea,
            Hour, Latitude, Longitude, COUNT(*) as count, 
            SUM(Arrest) as arrests
        FROM ChicagoCrimes
        """

        if isinstance(year_filter, tuple):  # zakres lat
            base_query += f" WHERE Year BETWEEN {year_filter[0]} AND {year_filter[1]}"
        elif year_filter:  # pojedynczy rok
            base_query += f" WHERE Year = {year_filter}"

        base_query += """
        GROUP BY Year, Month, PrimaryType, LocationDescription, Description,
                 Arrest, Domestic, Beat, District, Ward, CommunityArea, Hour,
                 Latitude, Longitude
        """

        df = pd.read_sql_query(base_query, conn)
        conn.close()
        return df
    except sqlite3.OperationalError as e:
        print(f"Błąd bazy danych: {e} | Ścieżka: {DB_PATH}")
        return pd.DataFrame()


# Funkcja tworząca komunikat o ładowaniu danych
def create_loading_message():
    """Tworzenie komponentu z komunikatem ładowania"""
    return html.Div([
        html.H4("Ładowanie danych...", className="text-center mt-4")
    ])


# Funkcja tworząca komponent do wyboru lat analizy
def create_year_selector():
    """Tworzenie komponentu do wyboru lat"""
    return dbc.Card(
        dbc.CardBody([
            html.H4("Wybór okresu analizy", className="mb-3"),
            dcc.RadioItems(
                id='date-range-type',
                options=[
                    {'label': ' Jeden rok', 'value': 'single'},
                    {'label': ' Zakres lat', 'value': 'range'}
                ],
                value='single',
                className="mb-3"
            ),
            html.Div(id='year-selector-container', children=[
                html.Div(
                    id='single-year-container',
                    children=[
                        dcc.Dropdown(
                            id='single-year-dropdown',
                            options=[{'label': str(year), 'value': year}
                                     for year in range(2008, 2018)],
                            value=2008,
                            placeholder="Wybierz rok"
                        )
                    ]
                ),
                html.Div(
                    id='year-range-container',
                    style={'display': 'none'},
                    children=[
                        html.P("Wybierz zakres lat:", className="mt-3"),
                        dcc.RangeSlider(
                            id='year-range-slider',
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
                "Generuj analizę",
                id="generate-button",
                color="primary",
                className="mt-3 w-100"
            )
        ]),
        className="mb-4"
    )


# Funkcja tworząca wykresy na podstawie danych
def create_charts(df, include_map):
    """Tworzenie wykresów na podstawie danych"""
    # Sumaryczna liczba przestępstw na rok
    yearly_stats = px.bar(
        df.groupby('Year')['count'].sum().reset_index(),
        x='Year', y='count',
        title='Sumaryczna liczba przestępstw na rok'
    )
    yearly_stats.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=df['Year'].min(),
            dtick=1,
            title='Rok'
        ),
        yaxis=dict(
            title='Liczba przestępstw'
        )
    )

    # Trend miesięczny
    time_trend = px.line(
        df.groupby(['Year', 'Month'])['count'].sum().reset_index(),
        x='Month', y='count', color='Year',
        title='Trend przestępczości'
    )
    time_trend.update_xaxes(
        tickmode='array',
        ticktext=['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
                  'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'],
        tickvals=list(range(1, 13)),
        title='Miesiąc'
    )
    time_trend.update_yaxes(title='Liczba przestępstw')

    # Rozkład godzinowy
    hourly_trend = px.bar(
        df.groupby('Hour')['count'].sum().reset_index(),
        x='Hour', y='count',
        title='Rozkład przestępstw w ciągu doby'
    )
    hourly_trend.update_xaxes(title='Godzina')
    hourly_trend.update_yaxes(title='Liczba przestępstw')

    # Rozkład lokalizacji
    location_dist = px.treemap(
        df.groupby('LocationDescription')['count'].sum().reset_index(),
        path=['LocationDescription'],
        values='count',
        title='Rozkład lokalizacji przestępstw'
    )

    # Przestępstwa i aresztowania
    arrest_stats = px.bar(
        df.groupby('PrimaryType').agg({
            'count': 'sum',
            'arrests': 'sum'
        }).reset_index().nlargest(10, 'count'),
        x='PrimaryType',
        y=['count', 'arrests'],
        title='Przestępstwa vs Aresztowania',
        barmode='group'
    )
    arrest_stats.update_xaxes(title='Typ przestępstwa')
    arrest_stats.update_yaxes(title='Liczba')

    components = [
        dbc.Row(dbc.Col(dcc.Graph(figure=yearly_stats), width=12), className="mb-4"),
        dbc.Row(dbc.Col(dcc.Graph(figure=time_trend), width=12), className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=hourly_trend), width=12),
            dbc.Col(dcc.Graph(figure=location_dist), width=12)
        ], className="mb-4"),
        dbc.Row(dbc.Col(dcc.Graph(figure=arrest_stats), width=12))
    ]

    if include_map:
        crime_map = px.scatter_mapbox(
            df,
            lat="Latitude",
            lon="Longitude",
            hover_name="PrimaryType",
            hover_data={"Arrest": True, "count": True},
            color="PrimaryType",
            title="Mapa przestępstw w Chicago",
            mapbox_style="carto-positron",
            zoom=10
        )
        components.append(dbc.Row(dbc.Col(dcc.Graph(figure=crime_map), width=12), className="mb-4"))
    else:
        components.append(
            dbc.Alert("Mapa przestępstw nie może być wygenerowana dla zakresu lat.", color="warning", className="mt-4"))

    return dbc.Container(components)


# Funkcja definiująca główny układ aplikacji
def layout():
    """Główny układ strony"""
    return html.Div([
        html.H1("Analiza Wizualna Danych", className="mb-4 text-center"),
        dbc.Row([
            dbc.Col(create_year_selector(), width=12)
        ]),
        html.Div(id="loading-graphs")
    ])


# Funkcja rejestrująca callbacki aplikacji
def register_callbacks(app):
    """Rejestracja callbacków"""

    @app.callback(
        Output('year-range-container', 'style'),
        Output('single-year-container', 'style'),
        Input('date-range-type', 'value')
    )
    def toggle_year_selector(selector_type):
        if selector_type == 'range':
            return {'display': 'block'}, {'display': 'none'}
        return {'display': 'none'}, {'display': 'block'}

    @app.callback(
        Output("loading-graphs", "children"),
        [Input("generate-button", "n_clicks")],
        [State("single-year-dropdown", "value"),
         State("year-range-slider", "value"),
         State("date-range-type", "value")]
    )
    def update_graphs(n_clicks, single_year, year_range, range_type):
        if n_clicks is None:
            return []

        return create_loading_message()

    @app.callback(
        Output("loading-graphs", "children", allow_duplicate=True),
        [Input("loading-graphs", "children")],
        [State("single-year-dropdown", "value"),
         State("year-range-slider", "value"),
         State("date-range-type", "value")],
        prevent_initial_call=True
    )
    def load_data(loading_children, single_year, year_range, range_type):
        if not loading_children:
            return []

        year_filter = None
        include_map = False

        if range_type == 'single':
            year_filter = single_year
            include_map = True
        else:
            year_filter = tuple(year_range)

        df = query_database(year_filter)

        if df.empty:
            return dbc.Alert("Brak danych dla wybranego okresu.", color="warning")

        return create_charts(df, include_map)
