import sys
import os

# Dodanie katalogu głównego do sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from dash import Dash, Input, Output
from layout.base_layout import base_layout
import pages.home as home
import pages.visual_analysis as visual_analysis
import pages.statistical_analysis as statistical_analysis
import pages.advanced_analysis as advanced_analysis
import pages.summary as summary
import pages.not_found as not_found

# Tworzenie instancji aplikacji
app = Dash(__name__)
app.title = "Analiza Danych"

# Ustawienie głównego layoutu
app.layout = base_layout()


# Callback do obsługi routing
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/":
        return home.layout()
    elif pathname == "/analiza-wizualna":
        return visual_analysis.layout()
    elif pathname == "/analiza-statystyczna":
        return statistical_analysis.layout()
    elif pathname == "/zaawansowana-analiza":
        return advanced_analysis.layout()
    elif pathname == "/podsumowanie":
        return summary.layout()
    else:
        return not_found.layout()


# Uruchomienie serwera
if __name__ == "__main__":
    app.run_server(debug=True)
