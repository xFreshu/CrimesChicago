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
            html.P(
                "W projekcie korzystam z danych obejmujących lata 2005–2017, które stanowią przekrojową bazę umożliwiającą analizę "
                "trendów przestępczości w czasie oraz identyfikację istotnych wzorców przestrzennych i czasowych."),
            html.H2("Cel analizy"),
            html.Ul([
                html.Li(
                    "Analiza wizualna danych – przygotowanie wykresów i interaktywnych dashboardów, które pozwolą na szybkie zrozumienie rozkładu i trendów danych."),
                html.Li(
                    "Analiza statystyczna – weryfikacja hipotez statystycznych oraz obliczenie kluczowych statystyk opisowych."),
                html.Li(
                    "Zaawansowana analiza danych – możliwe wykorzystanie technik takich jak analiza predykcyjna, modelowanie danych przestrzennych lub analiza skupień."),
                html.Li("Podsumowanie i wnioski – wyciągnięcie istotnych wniosków na podstawie uzyskanych wyników."),
            ]),
            html.H2("Technologie i narzędzia"),
            html.P("W trakcie realizacji projektu wykorzystuję:"),
            html.Ul([
                html.Li("Python – jako główny język programowania."),
                html.Li("Pandas i DataFrame – do manipulacji danymi i ich przygotowania do analizy."),
                html.Li("Dash – do budowy interaktywnych wizualizacji i aplikacji analitycznej."),
            ]),
            html.P(
                "Na obecnym etapie przewiduję rozszerzenie narzędzi o dodatkowe biblioteki lub technologie, w zależności od potrzeb wynikających z dalszych etapów analizy."),
            html.H2("Autor"),
            html.P(
                "Projekt realizowany jest przez Łukasza Przybysza, a kod i analizy są opracowywane samodzielnie w ramach poszerzania wiedzy i praktycznych umiejętności w dziedzinie analizy danych.")
        ], style={
            'maxWidth': '800px',
            'margin': 'auto',
            'padding': '20px',
            'textAlign': 'justify',
            'backgroundColor': '#f9f9f9',
            'borderRadius': '10px',
        })
    ])
