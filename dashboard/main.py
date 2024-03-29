"""Dashboard com apresentação dos KPIs da central de atendimentos."""
import pandas as pd
import plotly.express as px
import plotly.io as pio
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
from datetime import datetime
from time import gmtime, strftime
from dash_bootstrap_templates import load_figure_template
from df_manipulation import upload_db


load_figure_template("minty")
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])

# --------------------------------------------------------------------------- #
# Base de dados completa (histórico e simulação)
df = upload_db()

# --------------------------------------------------------------------------- #
# Layout do app
ggplot = pio.templates["ggplot2"]  # Tema gráficos
app.layout = dbc.Container([
    # Linha 1 - Header
    dbc.Row([
        dbc.Col(html.H1("Dashboard Central de Atendimentos"),
                className="text-center", width=12)
    ]),
    # Linha 2 - Picker
    dbc.Row([
        dbc.Col(
            dcc.DatePickerSingle(
                id="my-date-picker",
                min_date_allowed="2021-01-01",
                max_date_allowed="2022-12-31",
                initial_visible_month="2021-12-31",
                date="2021-12-31",
                display_format='DD/MM/Y'
            ), width=12, className="text-center"),
    ], className="mt-3"),
    dbc.Row([
        dbc.Col([html.H5("Slider do número de trabalhadores em 2022"),
            dcc.Slider(
                id="slider-trabalhadores",
                min=4, max=9, step=1, value=4)],
            width=12),
    ], className="mt-3"),
    # Linha 3 - KPIs de percentual e clientes atendidos e Tempo Médio
    dbc.Row([
        dbc.Col(
            dbc.Card(
                [dbc.CardHeader(html.H3("Atendimento em até 1 minuto (%)")),
                 dbc.CardBody(html.H2(id="output-percent-atendimento"))]
            ), width=6, className="text-center"),
        dbc.Col(
            dbc.Card(
                [dbc.CardHeader(html.H3(
                    "Número de chamados atendidos no dia")),
                 dbc.CardBody(html.H2(id="output-chamados"))]
            ), width=6, className="text-center"),
    ], className="mt-3"),
    # Linha 3.5 - Gráficos e picker de gráficos para cada um dos KPIS
    dbc.Row([

        dbc.Col([
                html.Div([dcc.Dropdown(["Bar Plot", "Histogram",
                                        "Scatter Plot",
                                        "Box Plot"], 'Bar Plot',
                                       id='crossfilter-percentil')]),
                dcc.Graph(id="grafico-percentil"),
                ], width=6, className="text-center"),
        dbc.Col([
                html.Div([dcc.Dropdown(["Bar Plot", "Histogram",
                                        "Scatter Plot",
                                        "Box Plot"], 'Bar Plot',
                                       id='crossfilter-num-chamadas')]),
                dcc.Graph(id="grafico-chamados")], width=6,
                className="text-center"),
    ], className="mt-1"),
    # Linha 4 - KPIs de tempo médio de atendimento
    dbc.Row(dbc.Col(html.Hr(style={'borderWidth': "0.3vh",
                                   "width": "100%",
                                   "borderColor": "#000000",
                                   "borderStyle": "solid"}), width=12),),
    dbc.Row([
        dbc.Col(
            dcc.Slider(
                id="slider-percentil-espera",
                min=0, max=100, step=5, value=90
            ), width=6, className="text-center"),
        dbc.Col(
            dcc.Slider(
                id="slider-percentil-atendimento",
                min=0, max=100, step=5, value=50
            ), width=6, className="text-center")
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                [dbc.CardHeader(html.H3("Espera para percentil "
                                        "selecionado (min)")),
                 dbc.CardBody(html.H2(id="output-media-espera"))]
            ), width=6, className="text-center"),
        dbc.Col(
            dbc.Card(
                [dbc.CardHeader(html.H3("Tempo de atendimento para "
                                        "o percentil (min)")),
                 dbc.CardBody(html.H2(id="output-media-atendimento"))]
            ), width=6, className="text-center"),
    ]),
    # Linha 4.5 Gráficos do TM de atend e do TM de Espera
    dbc.Row([
        dbc.Col([
                html.Div([dcc.Dropdown(["Bar Plot", "Histogram",
                                        "Scatter Plot", "Box Plot"],
                                       'Bar Plot',
                                       id='crossfilter-espera')]),
                dcc.Graph(id="grafico-espera"),
                ], width=6, className="text-center"
                ),
        dbc.Col([
                html.Div([dcc.Dropdown(["Bar Plot", "Histogram",
                                        "Scatter Plot",
                                        "Box Plot"], 'Bar Plot',
                                       id='crossfilter-atendimento')]),
                dcc.Graph(id="grafico-atendimento"),
                ], width=6, className="text-center"
                ),
    ]),
    dbc.Row(dbc.Col(html.Hr(style={'borderWidth': "0.3vh",
                                   "width": "100%",
                                   "borderColor": "#000000",
                                   "borderStyle": "solid"}), width=12),),
    # Linha 5 - Taxa de abandono ("service_length" < 30s)
    dbc.Row([
        dbc.Col(
            dbc.Card(
                [dbc.CardHeader(html.H3("Taxa de desistência (%)")),
                 dbc.CardBody(html.H2(id="output-percent-desistencia"))]
            ), width=6, className="text-center"),
        dbc.Col(
            dbc.Card(
                [dbc.CardHeader(html.H3("Utilização operadores (%)")),
                 dbc.CardBody(html.H2(id="output-utilizacao"))]
            ), width=6, className="text-center"),
    ], className="mt-3"),
    # Linha 5.5 Graficos de desistencia e utl
    dbc.Row([
        dbc.Col([
            html.Div([dcc.Dropdown(["Bar Plot", "Histogram", "Scatter Plot",
                                    "Box Plot"], 'Bar Plot',
                                   id='crossfilter-desistencia')]),
            dcc.Graph(id="grafico-desistencia"),
        ], width=6, className="text-center"
        ),
        dbc.Col([
                html.Div([dcc.Dropdown(["Bar Plot", "Histogram",
                                        "Scatter Plot",
                                        "Box Plot"], 'Bar Plot',
                                       id='crossfilter-utl')]),
                dcc.Graph(id="grafico-utl"),
                ], width=6, className="text-center"
                ),
    ])

],
    fluid=True,
    style={'padding': 40, 'background-image':
           'url("/assets/.jpeg")',
           'background-size': 'cover'})


# --------------------------------------------------------------------------- #
# Callbacks

# KPIs
@app.callback(
    [Output("output-percent-atendimento", "children"),
     Output("output-chamados", "children"),
     Output("output-media-atendimento", "children"),
     Output("output-media-espera", "children"),
     Output("output-percent-desistencia", "children"),
     Output("output-utilizacao", "children")],
    [Input("my-date-picker", "date"),
     Input("slider-percentil-espera", "value"),
     Input("slider-percentil-atendimento", "value"),
     Input("slider-trabalhadores", "value")]
)
def update_kpis(dia, slider1, slider2, trabalhadores):
    """Calcula os KPIs de acordo com a data."""
    # Percentual atendido em até 1 minuto
    dff = df.loc[(df["date"] == dia) & (
        (df["workers"] == 0) | (df["workers"] == trabalhadores))]
    percent = dff["meets_standard"].mean()
    # Chamados por dia
    callers = dff.groupby(["date"])["daily_caller"].max()[dia]
    # Média tempo de atendimento
    media_atendimento = dff.groupby(
        ["date"])["service_length"].quantile(q=slider2 / 100)[dia]
    media_atendimento = strftime("%M:%S", gmtime(media_atendimento))
    # Média tempo de espera
    media_espera = dff.groupby(
        ["date"])["wait_length"].quantile(q=slider1 / 100)[dia]
    media_espera = strftime("%M:%S", gmtime(media_espera))
    # Taxa de desistência
    if len(dff) > 0:
        taxa_desistencia = len(dff.loc[dff["service_length"] < 30]) / len(dff)
    else:
        taxa_desistencia = 0
    # Percentual de utilização
    if dia > "2021-12-31":
        n_atendentes = trabalhadores
    else:
        n_atendentes = 4
    horas_disponiveis = 10 * 60 * 60 * n_atendentes
    utilizacao = dff["service_length"].sum() / horas_disponiveis
    # Retorna os valores
    return (f"{percent * 100 :.2f}%", f"{callers}",
            f"{media_atendimento}", f"{media_espera}",
            f"{taxa_desistencia * 100 :.2f}%", f"{utilizacao * 100 :.2f}%")


# Gráficos
@app.callback(
    Output("grafico-percentil", "figure"),
    [Input("my-date-picker", "date"),
     Input("crossfilter-percentil", "value"),
     Input("slider-trabalhadores", "value")]
)
def update_figures_percentual(dia, tipo, trabalhadores):
    """Função de callback dos gráficos dos KPIs."""
    if dia == "2021-12-31T00:00:00":
        dia = "2021-12-31"

    # Gráficos para cada um dos KPIS
    mes = df.loc[(df["date"].dt.month == datetime.strptime(
        dia, '%Y-%m-%d').month) & (df["date"].dt.year == datetime.strptime(
            dia, '%Y-%m-%d').year)
                 & ((df["workers"] == 0) | (df["workers"] == trabalhadores))]

    # Gráficos do percentual
    percent_std = round(mes.groupby(["date"])["meets_standard"].mean(), 2)

    if tipo == "Bar Plot":
        try:
            percent_graph = px.bar(mes.groupby(["date"]),
                                   x=mes["date"].unique(),
                                   y=percent_std,
                                   height=345,
                                   color=percent_std,
                                   color_continuous_scale="darkmint",
                                   labels={"x": "Data",
                                           "y": "Atendimentos até "
                                           "1 minuto (%)"})
        except ValueError:
            percent_graph = px.bar(mes.groupby(["date"]),
                                   x=mes["date"].unique(),
                                   y=percent_std,
                                   height=345,
                                   color=percent_std,
                                   color_continuous_scale="darkmint",
                                   labels={"x": "Data",
                                           "y": "Atendimentos até "
                                           "1 minuto (%)"})
        percent_graph.update_yaxes(range=[min(percent_std)*0.75, 1], tick0=0)

        percent_graph.add_shape(  # add a horizontal "target" line
            type="line", line_color="red", line_width=1, opacity=0.85,
            line_dash="dash",
            x0=1, x1=0, xref="paper", y0=0.9, y1=0.9, yref="y")

        percent_graph.update_coloraxes(colorbar_title="Até 1 minuto")
        percent_graph.update_layout(coloraxis_colorbar_tickformat=".0%")
        percent_graph.update_layout(yaxis_tickformat=".0%")
        percent_graph.update_traces(
            hovertemplate='<b>%{x}</b><br>Percentual: %{y:.2%}')

    elif tipo == "Scatter Plot":
        percent_graph = px.scatter(mes.groupby(["date"]),
                                   x=mes["date"].unique(),
                                   y=percent_std,
                                   height=345,
                                   color=percent_std,
                                   color_continuous_scale="darkmint",
                                   labels={"x": "Data",
                                           "y": "Atendimentos até "
                                           "1 minuto (%)"})
        percent_graph.add_shape(  # add a horizontal "target" line
            type="line", line_color="red", line_width=1, opacity=0.85,
            line_dash="dash",
            x0=1, x1=0, xref="paper", y0=0.9, y1=0.9, yref="y")
        percent_graph.update_coloraxes(colorbar_title="Até 1 minuto")
        percent_graph.update_layout(coloraxis_colorbar_tickformat=".0%")
        percent_graph.update_layout(yaxis_tickformat=".0%")
        percent_graph.update_traces(
            hovertemplate='<b>%{x}</b><br>Percentual: %{y:.2%}')

    elif tipo == "Histogram":
        percentil_std = pd.DataFrame()
        percentil_std["mean"] = percent_std.values
        percentil_std["Valor"] = pd.cut(percentil_std["mean"], bins=[
                                        0, 0.899, 1.1], include_lowest=True,
                                        labels=["abaixo de 90%",
                                                "acima de 90%"])

        percent_graph = px.histogram(percentil_std,
                                     x=percentil_std["mean"],
                                     height=345,
                                     color=percentil_std["Valor"],
                                     opacity=1,
                                     color_discrete_sequence=["#EB1A00",
                                                              "#110052"],
                                     marginal="box")

        percent_graph.update_xaxes(
            title_text='Percentual atendido em até 1 minuto', tickformat=".1%")
        percent_graph.update_yaxes(title_text='Frequência')
        percent_graph.update_coloraxes(colorbar_title="% Acima de 90%")
        percent_graph.update_traces(
            hovertemplate="<b>%{y} Repetições</b><br>%{x:.1%} Atendidos<br>"
            "<extra></extra>")

    elif tipo == "Box Plot":
        percent_graph = px.box(mes.groupby(["date"]),
                               x=percent_std,
                               height=345)
        percent_graph.update_xaxes(
            title_text='Percentual da meta ao longo do mês')

    percent_graph.update_layout(template="plotly_white")

    return percent_graph


@app.callback(
    Output("grafico-chamados", "figure"),
    [Input("my-date-picker", "date"),
     Input("crossfilter-num-chamadas", "value"),
     Input("slider-trabalhadores", "value")]
)
# tipo_percent,tipo_num_chamadas):
def update_figures_chamadas(dia, tipo, trabalhadores):
    """Função de callback dos gráficos dos KPIs."""
    if dia == "2021-12-31T00:00:00":
        dia = "2021-12-31"

    mes = df.loc[(df["date"].dt.month == datetime.strptime(
        dia, '%Y-%m-%d').month) & (df["date"].dt.year == datetime.strptime(
            dia, '%Y-%m-%d').year)
                 & ((df["workers"] == 0) | (df["workers"] == trabalhadores))]

    if tipo == "Bar Plot":
        # Gráficos número de atendimentos BARPLOT
        maximo_mes = max(mes.groupby(["date"])["daily_caller"].max())
        try:
            callers_graph = px.bar(mes.groupby(["date"]),
                                   x=mes["date"].unique(),
                                   y=mes.groupby(["date"])[
                "daily_caller"].max(),
                height=345,
                color=mes.groupby(["date"])[
                "daily_caller"].max(),
                color_continuous_scale="darkmint",
                labels={"x": "Data", "y": "Nº de Chamadas no Dia"})
        except ValueError:
            callers_graph = px.bar(mes.groupby(["date"]),
                                   x=mes["date"].unique(),
                                   y=mes.groupby(["date"])[
                "daily_caller"].max(),
                height=345,
                color=mes.groupby(["date"])[
                "daily_caller"].max(),
                color_continuous_scale="darkmint",
                labels={"x": "Data", "y": "Nº de Chamadas no Dia"})
        callers_graph.update_yaxes(
            range=[maximo_mes*0.75, maximo_mes*1.1], tick0=0)
        callers_graph.update_coloraxes(colorbar_title="Valores")
        callers_graph.update_traces(
            hovertemplate="<b>%{y} Chamadas</b><br>Data:%{x}<br>"
            "<extra></extra>")

    elif tipo == "Histogram":
        callers_graph = px.histogram(mes.groupby(["date"]),
                                     x=mes.groupby(["date"])[
            "daily_caller"].max(),
            height=275)

        callers_graph.update_xaxes(title_text='Número de chamadas')
        callers_graph.update_yaxes(title_text='Frequência')
        callers_graph.update_traces(
            hovertemplate="<b>%{y} Repetições</b><br>Num. Chamadas:%{x}<br>"
            "<extra></extra>")

    elif tipo == "Scatter Plot":
        maximo_mes = max(mes.groupby(["date"])["daily_caller"].max())
        callers_graph = px.scatter(mes.groupby(["date"]),
                                   x=mes["date"].unique(),
                                   y=mes.groupby(["date"])[
            "daily_caller"].max(),
            height=345,
            color=mes.groupby(["date"])[
            "daily_caller"].max(),
            color_continuous_scale="darkmint",
            labels={"x": "Data", "y": "Nº de Chamadas no Dia"})
        callers_graph.update_yaxes(
            range=[maximo_mes*0.75, maximo_mes*1.1], tick0=0)
        callers_graph.update_coloraxes(colorbar_title="Valores")
        callers_graph.update_traces(
            hovertemplate="<b>%{y} Chamadas</b><br>Data:%{x}<br>"
            "<extra></extra>")

    elif tipo == "Box Plot":
        callers_graph = px.box(mes.groupby(["date"]),
                               x=mes.groupby(["date"])["daily_caller"].max(),
                               height=345)
        callers_graph.update_xaxes(
            title_text='Chamadas atendidas ao longo do mês')

    callers_graph.update_layout(template="plotly_white")
    return callers_graph


@app.callback(
    Output("grafico-atendimento", "figure"),
    [Input("my-date-picker", "date"),
     Input("crossfilter-atendimento", "value"),
     Input("slider-trabalhadores", "value"),
     Input("slider-percentil-atendimento", "value")]
)
def update_figures_atendimentos(dia, tipo, trabalhadores, quantil):
    """Função de callback dos gráficos dos KPIs."""
    if dia == "2021-12-31T00:00:00":
        dia = "2021-12-31"

    mes = df.loc[(df["date"].dt.month == datetime.strptime(
        dia, '%Y-%m-%d').month) & (df["date"].dt.year == datetime.strptime(
            dia, '%Y-%m-%d').year)
                 & ((df["workers"] == 0) | (df["workers"] == trabalhadores))]

    if tipo == "Bar Plot":
        try:
            atendimento_plot = px.bar(mes.groupby(["date"]),
                                      x=mes["date"].unique(),
                                      y=mes.groupby(["date"])[
                "service_length"].quantile(q=quantil / 100),
                height=345,
                labels={"x": "Data", "y": "Tempo para o percentil de "
                        f"{quantil}% (s)"})
        except ValueError:
            atendimento_plot = px.bar(mes.groupby(["date"]),
                                      x=mes["date"].unique(),
                                      y=mes.groupby(["date"])[
                "service_length"].quantile(q=quantil / 100),
                height=345,
                labels={"x": "Data", "y": "Tempo para o percentil de "
                        f"{quantil}% (s)"})

        atendimento_plot.update_layout(coloraxis_colorbar_tickformat="s")
        atendimento_plot.update_layout(coloraxis=dict(colorscale="darkmint"))

        atendimento_plot.update_traces(marker=dict(color=mes.groupby(
            ["date"])["service_length"].quantile(q=quantil / 100),
                                                   coloraxis="coloraxis"))

    elif tipo == "Box Plot":
        atendimento_plot = px.box(mes,
                                  x="date",
                                  y="service_length",
                                  notched=True,
                                  height=345)
        atendimento_plot.update_xaxes(title_text='Data')
        atendimento_plot.update_yaxes(title_text='Tempo de atendimento (s)')

    elif tipo == "Scatter Plot":
        atendimento_plot = px.scatter(mes,
                                      x="date",
                                      y="service_length",
                                      height=345,
                                      color="service_length",
                                      color_continuous_scale="darkmint",
                                      size_max=10)
        atendimento_plot.update_xaxes(title_text='Data')
        atendimento_plot.update_yaxes(title_text='Tempo de atendimento (s)')

    elif tipo == "Histogram":
        atendimento_plot = px.histogram(mes,
                                        x="service_length",
                                        height=345, marginal="box")
        atendimento_plot.update_xaxes(title_text='Tempo de atendimento (s)')
        atendimento_plot.update_yaxes(title_text='Frequência')

        atendimento_plot.update_traces(
            hovertemplate="<b>Frequência:%{y}</b><br>Tempo atendimento:%{x}"
            "<br><extra></extra>")

    return atendimento_plot


@app.callback(
    Output("grafico-espera", "figure"),
    [Input("my-date-picker", "date"),
     Input("crossfilter-espera", "value"),
     Input("slider-trabalhadores", "value"),
     Input("slider-percentil-espera", "value")]
)
def update_figures_espera(dia, tipo, trabalhadores, quantil):
    """Função de callback dos gráficos dos KPIs."""
    if dia == "2021-12-31T00:00:00":
        dia = "2021-12-31"

    mes = df.loc[(df["date"].dt.month == datetime.strptime(
        dia, '%Y-%m-%d').month) & (df["date"].dt.year == datetime.strptime(
            dia, '%Y-%m-%d').year)
                 & ((df["workers"] == 0) | (df["workers"] == trabalhadores))]

    if tipo == "Bar Plot":  # gráfico da mediana para o percentil de 90%
        try:
            espera_plot = px.bar(mes.groupby(["date"]),
                                 x=mes["date"].unique(),
                                 y=mes.groupby(
                                     ["date"])["wait_length"].quantile(
                                     q=quantil / 100),
                                 height=345, color=mes.groupby(
                                     ["date"])["wait_length"].quantile(
                                         q=quantil / 100),
                                 color_continuous_scale="darkmint")

        except ValueError:
            espera_plot = px.bar(mes.groupby(["date"]),
                                 x=mes["date"].unique(),
                                 y=mes.groupby(
                                     ["date"])["wait_length"].quantile(
                                     q=quantil / 100),
                                 height=345, color=mes.groupby(
                                     ["date"])["wait_length"].quantile(
                                         q=quantil / 100),
                                 color_continuous_scale="darkmint")

        espera_plot.add_shape(  # add a horizontal "target" line
            type="line", line_color="red", line_width=1, opacity=0.85,
            line_dash="dash",
            x0=1, x1=0, xref="paper", y0=60, y1=60, yref="y")
        espera_plot.update_xaxes(title_text='Data')
        espera_plot.update_yaxes(title_text=f'Espera percentil {quantil}% (s)')

    elif tipo == "Box Plot":

        espera_plot = px.box(mes,
                             x="date",
                             y="wait_length",
                             color="meets_standard",
                             notched=True,
                             color_discrete_map={"acima de 90%": "blue",
                                                 "abaixo de 90%": "red"},
                             labels={"meets_standard": "Cumpre a meta"},
                             height=345)
        espera_plot.update_xaxes(title_text='Data')
        espera_plot.update_yaxes(title_text='Tempo de espera')

    elif tipo == "Histogram":
        espera_plot = px.histogram(mes,
                                   x="wait_length",
                                   height=345, marginal="box")
        espera_plot.update_xaxes(title_text='Tempo de espera')
        espera_plot.update_yaxes(title_text='Frequência')

    elif tipo == "Scatter Plot":
        mes["meets_standard"] = mes["meets_standard"].replace(
            {True: "Sim", False: "Não"})
        espera_plot = px.scatter(mes,
                                 x="date",
                                 y="wait_length",
                                 color="meets_standard",
                                 height=345,
                                 labels={"meets_standard": "Cumpre a meta"})
        espera_plot.add_shape(  # add a horizontal "target" line
            type="line", line_color="red", line_width=1, opacity=0.85,
            line_dash="dash",
            x0=1, x1=0, xref="paper", y0=60, y1=60, yref="y")
        espera_plot.update_xaxes(title_text='Data')
        espera_plot.update_yaxes(title_text='Tempo de espera')

    return espera_plot


@app.callback(
    Output("grafico-desistencia", "figure"),
    [Input("my-date-picker", "date"),
     Input("crossfilter-desistencia", "value"),
     Input("slider-trabalhadores", "value")]
)
def update_figures_desistencia(dia, tipo, trabalhadores):
    """Função de callback dos gráficos dos KPIs."""
    if dia == "2021-12-31T00:00:00":
        dia = "2021-12-31"

    mes = df.loc[(df["date"].dt.month == datetime.strptime(
        dia, '%Y-%m-%d').month) & (df["date"].dt.year == datetime.strptime(
            dia, '%Y-%m-%d').year)
                 & ((df["workers"] == 0) | (df["workers"] == trabalhadores))]

    mes["desiste"] = pd.cut(mes["service_length"], bins=[
                            0, 30, 1500000], include_lowest=True,
                            labels=["desistiu", "continuou"])

    desistencia_por_dia = mes.groupby(["date", "desiste"]).size().reset_index()
    desistencia_por_dia.columns = ["date", "categoria", "Freq"]
    desistencia_por_dia['percentage'] = mes.groupby(['date', 'desiste']).size(
    ).groupby(level=0).apply(lambda x:  x / float(x.sum())).values

    if tipo == "Bar Plot":
        try:
            desistencia_plot = px.bar(desistencia_por_dia, x="date",
                                      y="percentage", color="categoria",
                                      barmode="stack", text="Freq",
                                      height=345)
        except ValueError:
            desistencia_plot = px.bar(desistencia_por_dia, x="date",
                                      y="percentage", color="categoria",
                                      barmode="stack", text="Freq",
                                      height=345)

    elif tipo == "Histogram":
        # filtrar apenas aqueles que desistiram
        desistence = desistencia_por_dia.loc[
            desistencia_por_dia["categoria"] == "desistiu"]

        desistencia_plot = px.histogram(
            desistence, x="percentage", height=345, marginal="box")

    elif tipo == "Scatter Plot":
        desistence = desistencia_por_dia.loc[
            desistencia_por_dia["categoria"] == "desistiu"]
        desistencia_plot = px.scatter(
            desistence, x="date", y="percentage", height=345)

    elif tipo == "Box Plot":
        desistence = desistencia_por_dia.loc[
            desistencia_por_dia["categoria"] == "desistiu"]
        desistencia_plot = px.box(desistence, x="percentage", height=345)

    return desistencia_plot


@app.callback(
    Output("grafico-utl", "figure"),
    [Input("my-date-picker", "date"),
     Input("crossfilter-utl", "value"),
     Input("slider-trabalhadores", "value")]
)
def update_figures_utl(dia, tipo, trabalhadores):
    """Função de callback dos gráficos dos KPIs."""
    if dia == "2021-12-31T00:00:00":
        dia = "2021-12-31"

    mes = df.loc[(df["date"].dt.month == datetime.strptime(
        dia, '%Y-%m-%d').month) & (df["date"].dt.year == datetime.strptime(
            dia, '%Y-%m-%d').year)
                 & ((df["workers"] == 0) | (df["workers"] == trabalhadores))]

    if datetime.strptime(dia, '%Y-%m-%d').year < 2022:
        trabalhadores = 4

    horas_disponiveis = 10 * 60 * 60 * trabalhadores
    utilizacao = mes.groupby(
        "date")["service_length"].sum() / horas_disponiveis

    if tipo == "Bar Plot":
        try:
            utl_plot = px.bar(mes.groupby(["date"]),
                              x=mes["date"].unique(),
                              y=utilizacao,
                              height=345, labels={"x": "Data",
                                                  "y": "Utilização (%)"},
                              color=utilizacao,
                              color_continuous_scale="darkmint")
        except ValueError:
            utl_plot = px.bar(mes.groupby(["date"]),
                              x=mes["date"].unique(),
                              y=utilizacao,
                              height=345, labels={"x": "Data",
                                                  "y": "Utilização (%)"},
                              color=utilizacao,
                              color_continuous_scale="darkmint")

    if tipo == "Histogram":
        utl_plot = px.histogram(mes.groupby(
            "date"), x=utilizacao, height=345, marginal="box")

    if tipo == "Scatter Plot":
        utl_plot = px.scatter(mes.groupby(["date"]),
                              x=mes["date"].unique(),
                              y=utilizacao,
                              height=345)

    if tipo == "Box Plot":
        utl_plot = px.box(mes.groupby("date"), x=utilizacao, height=345)

    return utl_plot


# --------------------------------------------------------------------------- #
# Run server
if __name__ == '__main__':
    app.run_server(debug=True)
