from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
import os

# Konfiguracja ścieżek
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
DB_PATH = os.path.join(project_root, 'scripts', 'chicago_crimes.db')


# tworzy komponent z komunikatem ładowania
def create_loading_message():
    return html.Div([
        html.H4("Ładowanie danych...", className="text-center mt-4")
    ])


# funkcja do pobierania danych z bazy danych
def query_arrests_data(year_filter=None):
    try:
        conn = sqlite3.connect(DB_PATH)

        query = """
        SELECT 
            PrimaryType as Typ,
            Arrest as Aresztowanie,
            Month as Miesiac,
            Year as Rok
        FROM ChicagoCrimes
        WHERE 1=1
        """

        if isinstance(year_filter, tuple):
            query += f" AND Year BETWEEN {year_filter[0]} AND {year_filter[1]}"
        elif year_filter:
            query += f" AND Year = {year_filter}"

        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    except sqlite3.OperationalError as e:
        print(f"Błąd bazy danych: {e}")
        return None


# funkcja do tworzenia statystyk aresztowań
def create_arrest_statistics(df):
    # Podstawowe statystyki aresztowań według typu przestępstwa
    crime_stats = df.groupby('Typ').agg({
        'Aresztowanie': ['count', 'sum', 'mean']
    }).round(3)

    crime_stats = crime_stats.reset_index()
    crime_stats.columns = ['Typ przestępstwa', 'Liczba przestępstw', 'Liczba aresztowań', 'Wskaźnik aresztowań']
    crime_stats = crime_stats.sort_values('Liczba przestępstw', ascending=False)
    crime_stats['Wskaźnik aresztowań'] = crime_stats['Wskaźnik aresztowań'].map(lambda x: f"{x:.1%}")

    return crime_stats


# funkcja do tworzenia szczegółowych statystyk
def create_detailed_statistics(df):
    # Najpierw utworzmy miesięczne agregacje
    monthly_counts = df.groupby(['Typ', 'Rok', 'Miesiac']).size().reset_index(name='count')

    # Teraz możemy obliczyć statystyki dla każdego typu
    detailed_stats = pd.DataFrame()

    # Podstawowe obliczenia dla każdego typu
    type_stats = df.groupby('Typ').agg({
        'Aresztowanie': [
            ('Całkowita liczba', 'count'),
            ('% wszystkich przestępstw', lambda x: len(x) / len(df) * 100)
        ]
    })
    type_stats.columns = type_stats.columns.get_level_values(1)

    # Obliczenia na podstawie miesięcznych danych
    monthly_stats = monthly_counts.groupby('Typ').agg({
        'count': [
            ('Średnia miesięczna', 'mean'),
            ('Minimum miesięczne', 'min'),
            ('Maximum miesięczne', 'max'),
            ('Odchylenie standardowe', 'std'),
            ('Mediana miesięczna', 'median')
        ]
    })
    monthly_stats.columns = monthly_stats.columns.get_level_values(1)

    # Łączymy wszystkie statystyki
    detailed_stats = pd.concat([type_stats, monthly_stats], axis=1)
    detailed_stats = detailed_stats.reset_index()
    detailed_stats.columns = ['Typ przestępstwa', 'Całkowita liczba', '% wszystkich przestępstw',
                              'Średnia miesięczna', 'Minimum miesięczne', 'Maximum miesięczne',
                              'Odchylenie standardowe', 'Mediana miesięczna']

    # Formatowanie liczb
    detailed_stats['Całkowita liczba'] = detailed_stats['Całkowita liczba'].astype(int)
    detailed_stats['% wszystkich przestępstw'] = detailed_stats['% wszystkich przestępstw'].map(lambda x: f"{x:.2f}%")
    detailed_stats['Średnia miesięczna'] = detailed_stats['Średnia miesięczna'].round(1)
    detailed_stats['Minimum miesięczne'] = detailed_stats['Minimum miesięczne'].astype(int)
    detailed_stats['Maximum miesięczne'] = detailed_stats['Maximum miesięczne'].astype(int)
    detailed_stats['Odchylenie standardowe'] = detailed_stats['Odchylenie standardowe'].round(2)
    detailed_stats['Mediana miesięczna'] = detailed_stats['Mediana miesięczna'].round(1)

    # Sortowanie według całkowitej liczby przestępstw
    detailed_stats = detailed_stats.sort_values('Całkowita liczba', ascending=False)

    return detailed_stats


# funkcja do tworzenia dashboardu statystycznego
def create_statistics_dashboard(df):
    crime_stats = create_arrest_statistics(df)
    detailed_stats = create_detailed_statistics(df)

    # Obliczanie sumarycznych statystyk
    total_crimes = df['Aresztowanie'].count()
    total_arrests = df['Aresztowanie'].sum()
    overall_rate = total_arrests / total_crimes
    unique_types = df['Typ'].nunique()
    avg_crimes_per_type = total_crimes / unique_types

    return dbc.Container([
        html.H3("Podsumowanie", className="mt-4 mb-3"),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Statystyki ogólne"),
                        html.P([
                            f"Całkowita liczba przestępstw: {total_crimes:,}",
                            html.Br(),
                            f"Liczba aresztowań: {total_arrests:,}",
                            html.Br(),
                            f"Ogólny wskaźnik aresztowań: {overall_rate:.1%}",
                            html.Br(),
                            f"Liczba typów przestępstw: {unique_types}",
                            html.Br(),
                            f"Średnia liczba przestępstw na typ: {avg_crimes_per_type:,.0f}"
                        ])
                    ])
                ]),
                width=12
            )
        ]),

        html.H3("Podstawowa Analiza według Typu Przestępstwa", className="mt-4 mb-3"),
        dbc.Row([
            dbc.Col(
                dbc.Table.from_dataframe(
                    crime_stats,
                    striped=True,
                    bordered=True,
                    hover=True,
                    className="text-start"
                ),
                width=12
            )
        ]),

        html.H3("Szczegółowa Analiza Statystyczna", className="mt-4 mb-3"),
        dbc.Row([
            dbc.Col(
                dbc.Table.from_dataframe(
                    detailed_stats,
                    striped=True,
                    bordered=True,
                    hover=True,
                    className="text-start"
                ),
                width=12
            )
        ])
    ])


# funkcja do tworzenia komponentu wyboru roku
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
                "Generuj analizę",
                id="stats-generate-button",
                color="primary",
                className="mt-3 w-100"
            )
        ]),
        className="mb-4"
    )


# funkcja do tworzenia układu strony
def layout():
    return html.Div([
        html.H1("Analiza Statystyczna", className="mb-4 text-center"),
        dbc.Row([
            dbc.Col(create_year_selector(), width=12)
        ]),
        html.Div(id="stats-content")
    ])


# funkcja do rejestrowania callbacków
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
    def update_statistics(n_clicks, single_year, year_range, range_type):
        if n_clicks is None:
            return html.Div()

        return create_loading_message()

    @app.callback(
        Output("stats-content", "children", allow_duplicate=True),
        [Input("stats-content", "children")],
        [State("stats-single-year-dropdown", "value"),
         State("stats-year-range-slider", "value"),
         State("stats-date-range-type", "value")],
        prevent_initial_call=True
    )
    # funkcja do ładowania danych statystycznych
    def load_statistics_data(_, single_year, year_range, range_type):
        year_filter = None
        if range_type == 'single':
            year_filter = single_year
        else:
            year_filter = tuple(year_range)

        df = query_arrests_data(year_filter)

        if df is None:
            return dbc.Alert(
                "Błąd podczas pobierania danych.",
                color="danger",
                className="mt-3"
            )

        return create_statistics_dashboard(df)
