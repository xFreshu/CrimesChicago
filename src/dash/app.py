import dash
from dash import dcc, html, Input, Output

# Tworzenie instancji aplikacji
app = dash.Dash(__name__)
app.title = "Analiza Danych"

# Layout aplikacji
app.layout = html.Div([
    # Nawigacja
    html.Nav([
        html.A("Strona Główna", href="/", className="nav-link"),
        html.A("Analiza Wizualna Danych", href="/analiza-wizualna", className="nav-link"),
        html.A("Analiza Statystyczna", href="/analiza-statystyczna", className="nav-link"),
        html.A("Zaawansowana Analiza", href="/zaawansowana-analiza", className="nav-link"),
        html.A("Podsumowanie/Wnioski", href="/podsumowanie", className="nav-link"),
    ], className="nav-bar"),

    # Dynamicznie zmieniany content
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content", className="content"),
])


# Callback do obsługi stron
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/":
        return html.Div([
            html.H1("Strona Główna"),
            html.P("Witaj w aplikacji do analizy danych! Wybierz sekcję z nawigacji powyżej.")
        ])
    elif pathname == "/analiza-wizualna":
        return html.Div([
            html.H1("Analiza Wizualna Danych"),
            html.P("Tutaj znajdziesz wizualizacje danych.")
        ])
    elif pathname == "/analiza-statystyczna":
        return html.Div([
            html.H1("Analiza Statystyczna"),
            html.P("Tutaj przeprowadzimy analizę statystyczną.")
        ])
    elif pathname == "/zaawansowana-analiza":
        return html.Div([
            html.H1("Zaawansowana Analiza"),
            html.P("Zaawansowane modele i techniki analizy.")
        ])
    elif pathname == "/podsumowanie":
        return html.Div([
            html.H1("Podsumowanie/Wnioski"),
            html.P("Tutaj znajdziesz podsumowanie i wnioski z analizy.")
        ])
    else:
        return html.Div([
            html.H1("404 - Nie znaleziono strony"),
            html.P("Przepraszamy, ale strona, której szukasz, nie istnieje.")
        ])


# Uruchomienie serwera
if __name__ == "__main__":
    app.run_server(debug=True)
