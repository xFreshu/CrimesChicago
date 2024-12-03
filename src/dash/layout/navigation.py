from dash import html


def navigation():
    return html.Nav([
        html.A("Strona Główna", href="/", className="nav-link"),
        html.A("Analiza Wizualna Danych", href="/analiza-wizualna", className="nav-link"),
        html.A("Analiza Statystyczna", href="/analiza-statystyczna", className="nav-link"),
        html.A("Zaawansowana Analiza", href="/zaawansowana-analiza", className="nav-link"),
        html.A("Podsumowanie/Wnioski", href="/podsumowanie", className="nav-link"),
    ], className="nav-bar")
