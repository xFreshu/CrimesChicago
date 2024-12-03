from dash import html, dcc
from .navigation import navigation


def base_layout():
    return html.Div([
        navigation(),  # Dodanie nawigacji jako stałego komponentu
        dcc.Location(id="url", refresh=False),  # Monitorowanie URL
        html.Div(id="page-content", className="content"),  # Dynamiczna zawartość
    ])
