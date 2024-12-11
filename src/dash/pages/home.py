from dash import html


def layout():
    return html.Div([
        html.Div([
            html.H1("Analiza przestępczości w Chicago na podstawie danych z lat 2005–2017"),
            html.P([
                "Niniejszy projekt opiera się na analizie publicznie dostępnych danych dotyczących przestępczości w Chicago, "
                "udostępnionych na platformie Kaggle pod adresem ",
                html.A("Crimes in Chicago", href="https://www.kaggle.com/datasets/currie32/crimes-in-chicago/data",
                       target="_blank"),
                ". Dane obejmują szczegółowe informacje na temat przestępstw, takie jak daty, typy zdarzeń, lokalizacje oraz "
                "dodatkowe zmienne opisujące charakterystykę przestępstw, np. czy doszło do aresztowania lub czy incydent miał charakter domowy."
            ]),
        ], style={
            'maxWidth': '800px',
            'margin': 'auto',
            'padding': '20px',
            'textAlign': 'justify',
            'backgroundColor': '#f9f9f9',
            'borderRadius': '10px',
        })
    ])
