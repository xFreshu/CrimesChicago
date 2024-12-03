import os
import sqlite3
import pandas as pd
from dash import html, dcc, callback, Output, Input
import plotly.express as px


# Funkcja do ładowania danych z bazy SQLite
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "../../scripts/chicago_crimes.db")

    # Diagnostyka: wyświetl ścieżkę do bazy danych
    print(f"Ścieżka do bazy danych: {db_path}")

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Plik bazy danych nie został znaleziony: {db_path}")

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM ChicagoCrimes", conn)
    conn.close()

    # Diagnostyka: liczba rekordów
    print(f"Liczba rekordów w bazie: {len(df)}")
    return df


# Przygotowanie wizualizacji
def prepare_visualizations():
    df = load_data()
    df['Date'] = pd.to_datetime(df['Date'])  # Konwersja kolumny Date na typ datetime
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Hour'] = df['Date'].dt.hour

    crime_count_by_month = df.groupby('Month')['CaseNumber'].count().reset_index()
    crime_count_by_hour = df.groupby('Hour')['CaseNumber'].count().reset_index()

    fig_month = px.bar(
        crime_count_by_month, x='Month', y='CaseNumber',
        title="Liczba przestępstw w miesiącach",
        labels={'Month': 'Miesiąc', 'CaseNumber': 'Liczba Przestępstw'}
    )

    fig_hour = px.bar(
        crime_count_by_hour, x='Hour', y='CaseNumber',
        title="Liczba przestępstw w godzinach",
        labels={'Hour': 'Godzina', 'CaseNumber': 'Liczba Przestępstw'}
    )

    return fig_month, fig_hour


# Layout strony
def layout():
    return html.Div([
        html.H1("Analiza Wizualna Danych"),
        html.P("Tutaj znajdziesz wizualizacje danych przestępstw."),
        dcc.Loading(
            id="loading-visual-analysis",
            type="circle",  # Wskaźnik ładowania (circle lub dot)
            children=[
                html.Div(id="graphs-container")  # Miejsce, gdzie pojawią się wykresy
            ]
        )
    ])


# Callback do dynamicznego ładowania danych
@callback(
    Output("graphs-container", "children"),
    Input("graphs-container", "id")  # Wykonywane na inicjalizację
)
def update_graphs(_):
    try:
        fig_month, fig_hour = prepare_visualizations()
        return [
            dcc.Graph(figure=fig_month),
            dcc.Graph(figure=fig_hour)
        ]
    except FileNotFoundError as e:
        return html.Div([
            html.H1("Błąd: Nie znaleziono bazy danych"),
            html.P(str(e))
        ])
    except Exception as e:
        return html.Div([
            html.H1("Błąd"),
            html.P(f"Nieoczekiwany błąd: {e}")
        ])
