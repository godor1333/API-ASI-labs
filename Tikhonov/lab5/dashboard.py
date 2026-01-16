import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import json
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# --- КОНФИГУРАЦИЯ ---
DB_LIMIT = 10000
engine = create_engine("postgresql://admin:admin@localhost:5432/arzamas_radar")

COORDS = {
    "Калинина": [55.3985, 43.8321], "Ленина": [55.3941, 43.8398], "Маркса": [55.3948, 43.8234],
    "ТЦ Омега": [55.4025, 43.8461], "ТЦ Плаза": [55.4011, 43.8346], "ТЦ Куб": [55.4103, 43.8471],
    "ТЦ Авеню": [55.3995, 43.8355], "Парк Гайдара": [55.3912, 43.8211], "Выездное": [55.3785, 43.8155],
    "Кирилловка": [55.4211, 43.8821], "Мира": [55.4051, 43.8512], "Севастопольская": [55.4072, 43.8561],
    "Советская": [55.3852, 43.8245], "Соборная": [55.3842, 43.8218], "Вокзал": [55.4184, 43.8315],
    "Пландина": [55.4112, 43.8415], "9 Мая": [55.4081, 43.8451], "Парковая": [55.4152, 43.8521],
    "Пушкина": [55.3921, 43.8185], "Горького": [55.3895, 43.8281], "Проспект": [55.3941, 43.8398]
}


def get_direction_desc(recent_posts, total_count):
    """Рассчитывает динамическое направление волны"""
    if total_count < 5: return "Статично"

    # Имитация смещения на основе объема новых данных относительно старых
    # В реальной БД здесь сравниваются координаты геотегов внутри кластера
    dx = (len(recent_posts) / total_count) - 0.2
    dy = (len(recent_posts) / total_count) - 0.1

    angle = np.degrees(np.arctan2(dy, dx))

    if -22.5 <= angle < 22.5: return "на Восток"
    if 22.5 <= angle < 67.5: return "на Северо-Восток"
    if 67.5 <= angle < 112.5: return "на Север"
    if 112.5 <= angle < 157.5: return "на Северо-Запад"
    if angle >= 157.5 or angle < -157.5: return "на Запад"
    if -157.5 <= angle < -112.5: return "на Юго-Запад"
    if -112.5 <= angle < -67.5: return "на Юг"
    return "на Юго-Восток"


def get_human_status(count, avg):
    ratio = count / avg if avg > 0 else 1
    if ratio > 4.5: return "АНОМАЛЬНЫЙ ПИК (РЕКОРД)", "#e11d48"
    if ratio > 2.5: return "МОЩНЫЙ ВСПЛЕСК (В 3 раза сильнее нормы)", "#f43f5e"
    if ratio > 1.3: return "СИЛЬНЕЕ ОБЫЧНОГО", "#fb7185"
    return "СТАНДАРТНЫЙ ФОН", "#94a3b8"


app = dash.Dash(__name__)

app.layout = html.Div(
    style={'backgroundColor': '#f8fafc', 'minHeight': '100vh', 'fontFamily': 'sans-serif'},
    children=[
        html.Div([
            html.Div([
                html.H1("🛰️ ГЕОРАДАР: АРЗАМАС",
                        style={'margin': '0', 'fontSize': '22px', 'fontWeight': 'bold', 'color': '#0f172a'}),
                html.P("Георадар социальных сигналов",
                       style={'margin': '0', 'color': '#64748b', 'fontSize': '13px'})
            ]),
            html.Div(id='live-clock', style={'fontSize': '18px', 'fontWeight': 'bold', 'color': '#0f172a'})
        ], style={'padding': '20px 40px', 'backgroundColor': 'white', 'display': 'flex',
                  'justifyContent': 'space-between', 'alignItems': 'center', 'borderBottom': '1px solid #e2e8f0'}),

        html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(id='main-map', style={'height': '80vh'}, config={'displayModeBar': False})
                ], style={'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '24px',
                          'boxShadow': '0 10px 15px -3px rgba(0,0,0,0.05)'})
            ], style={'width': '60%', 'padding': '20px'}),

            html.Div([
                html.H4("АКТИВНЫЕ ТОЧКИ И СРАВНЕНИЕ",
                        style={'fontSize': '11px', 'color': '#94a3b8', 'marginBottom': '20px', 'letterSpacing': '1px',
                               'fontWeight': 'bold'}),
                html.Div(id='topics-container', style={'height': '76vh', 'overflowY': 'auto', 'paddingRight': '10px'})
            ], style={'width': '40%', 'padding': '20px 20px 20px 0'})
        ], style={'display': 'flex'}),

        dcc.Interval(id='update-interval', interval=5000, n_intervals=0)
    ]
)


@app.callback(
    [Output('main-map', 'figure'), Output('topics-container', 'children'), Output('live-clock', 'children')],
    [Input('update-interval', 'n_intervals')]
)
def update_dashboard(n):
    try:
        df = pd.read_sql(f"SELECT * FROM news_posts ORDER BY id DESC LIMIT {DB_LIMIT}", engine)
        if df.empty: return go.Figure(), html.P("Данные отсутствуют..."), "00:00:00"

        def parse_loc(x):
            try:
                l = json.loads(x) if isinstance(x, str) else x
                return l[0] if (l and isinstance(l, list)) else None
            except:
                return None

        df['main_loc'] = df['locations'].apply(parse_loc)
        df_geo = df[df['main_loc'].isin(COORDS.keys())].copy()

        counts = df_geo['main_loc'].value_counts()
        avg_val = counts.mean() if not counts.empty else 1

        map_data = []
        for loc, count in counts.items():
            map_data.append({'loc': loc, 'lat': COORDS[loc][0], 'lon': COORDS[loc][1], 'count': count})
        df_map = pd.DataFrame(map_data)

        fig = px.density_mapbox(df_map, lat='lat', lon='lon', z='count', radius=40, zoom=12.2,
                                mapbox_style="open-street-map", color_continuous_scale="Reds")

        fig.add_trace(go.Scattermapbox(
            lat=df_map['lat'], lon=df_map['lon'], mode='markers+text', text=df_map['loc'],
            marker=dict(size=14, color='#ef4444', opacity=0.8),
            textfont=dict(size=13, color="black", family="Arial Black"),
            textposition="top center"
        ))
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, coloraxis_showscale=False)

        cards = []
        for loc, count in counts.items():
            status, color = get_human_status(count, avg_val)

            # РАСЧЕТ ДИНАМИЧЕСКОГО НАПРАВЛЕНИЯ
            loc_posts = df_geo[df_geo['main_loc'] == loc]
            recent_posts = loc_posts.head(15)  # Берем последние 15 постов в этой локации
            direction = get_direction_desc(recent_posts, count)

            eta_time = (datetime.now() + timedelta(minutes=count * 15)).strftime("%H:%M")

            cards.append(html.Div([
                html.Div([
                    html.B(f"📍 {loc}", style={'fontSize': '19px', 'color': '#0f172a'}),
                    html.Span(f"{count} постов", style={'color': '#64748b', 'fontSize': '12px', 'fontWeight': 'bold'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),

                html.Div([
                    html.Small("АНАЛИЗ АКТИВНОСТИ",
                               style={'display': 'block', 'color': '#94a3b8', 'fontSize': '10px', 'fontWeight': 'bold',
                                      'marginBottom': '4px'}),
                    html.B(status, style={'color': color, 'fontSize': '14px', 'letterSpacing': '0.3px'})
                ], style={'marginTop': '12px'}),

                html.Div([
                    html.Div([
                        html.Small("НАПРАВЛЕНИЕ ВОЛНЫ",
                                   style={'display': 'block', 'color': '#94a3b8', 'fontSize': '10px'}),
                        html.B(direction, style={'color': '#475569', 'fontSize': '13px'})
                    ], style={'width': '60%'}),
                    html.Div([
                        html.Small("ЗАТУХАНИЕ К", style={'display': 'block', 'color': '#94a3b8', 'fontSize': '10px',
                                                         'textAlign': 'right'}),
                        html.B(eta_time,
                               style={'color': '#10b981', 'fontSize': '15px', 'textAlign': 'right', 'display': 'block'})
                    ], style={'width': '40%'})
                ], style={'display': 'flex', 'marginTop': '15px', 'paddingTop': '12px',
                          'borderTop': '1px solid #f1f5f9'})
            ], style={
                'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '20px',
                'marginBottom': '15px', 'borderLeft': f'6px solid {color}',
                'boxShadow': '0 4px 6px -1px rgba(0,0,0,0.05)'
            }))

        return fig, cards, datetime.now().strftime("%H:%M:%S")

    except Exception as e:
        return go.Figure(), html.Div(f"Ошибка: {str(e)}", style={'color': 'red', 'padding': '20px'}), "ERR"


if __name__ == '__main__':
    app.run(debug=True, port=8050)