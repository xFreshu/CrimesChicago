from dash import html


def layout():
    return html.Div(
        style={
            "backgroundColor": "#0000aa",  # Niebieskie tło
            "color": "white",  # Biały tekst
            "fontFamily": "Courier New, monospace",  # Styl klasycznego systemu
            "textAlign": "center",  # Wyśrodkowanie tekstu
            "height": "100vh",  # Pełna wysokość widoku
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
            "alignItems": "center",
        },
        children=[
            html.H1(":(", style={"fontSize": "72px", "marginBottom": "20px"}),  # Smutna buźka
            html.P("Your PC ran into a problem and needs to restart.", style={"fontSize": "24px"}),
            html.P("Error Code: 404_PAGE_NOT_FOUND", style={"fontSize": "20px", "marginBottom": "30px"}),
            html.P(
                "If you want to restart the application, try the following:",
                style={"fontSize": "18px"}
            ),
            html.Ul(
                [
                    html.Li("Check the URL for typos.", style={"fontSize": "18px"}),
                    html.Li("Go back to the homepage.", style={"fontSize": "18px"}),
                ],
                style={"textAlign": "left", "display": "inline-block", "margin": "10px 0"}
            ),
            html.P(
                "Your system will reboot automatically in 15 seconds...",
                style={"fontSize": "16px", "marginTop": "20px", "fontStyle": "italic"}
            ),
        ],
    )
