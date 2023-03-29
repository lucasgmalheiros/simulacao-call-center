"""Dashboard com apresentação dos KPIs da central de atendimentos."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
from datetime import date, datetime
from time import gmtime, strftime
from df_manipulation import clean_original_data, clean_arena_data


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SIMPLEX])

# --------------------------------------------------------------------------- #
# Base de dados reais de 2021
df = pd.read_csv("https://raw.githubusercontent.com/lucasgmalheiros"
                 "/projeto-simulacao-VCBC/main/calls.csv")

df = clean_original_data(df)
print(df.head())

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
                min_date_allowed=min(df["date"]),
                max_date_allowed=max(df["date"]),
                initial_visible_month=max(df["date"]),
                date=max(df["date"]),
                display_format='DD/MM/Y'
            ), width=12, className="text-center"),
        # dbc.Col(
        #     dcc.Slider(
        #         id="my-slider",
        #         min=4, max=6, step=1
        #     ), width=6, className="text-center")
    ], className="mt-3"),
    # Linha 3 - KPIs de percentual e clientes atendidos
    dbc.Row([
        dbc.Col(
            dbc.Card(
                [dbc.CardHeader(html.H3("Atendimento em até 1 minuto (%)")),
                 dbc.CardBody(html.H2(id="output-percent-atendimento"))]
            ), width=6, className="text-center"),
        dbc.Col(
            dbc.Card(
                [dbc.CardHeader(html.H3("Número de chamados no dia")),
                 dbc.CardBody(html.H2(id="output-chamados"))]
            ), width=6, className="text-center"),
    ], className="mt-3"),
    # Linha 3.5 - Gráficos e picker de gráficos para cada um dos KPIS
    dbc.Row([

        dbc.Col([
                html.Div([dcc.Dropdown(["Bar Plot", "Histogram", "Scatter Plot",
                         "Bubble Plot", "Box Plot"], 'Bar Plot', id='crossfilter-percentil')]),
                dcc.Graph(id="grafico-percentil"),
                ]),
        dbc.Col([
                html.Div([dcc.Dropdown(["Bar Plot", "Histogram", "Scatter Plot",
                         "Bubble Plot", "Box Plot"], 'Bar Plot', id='crossfilter-num-chamadas')]),
                dcc.Graph(id="grafico-chamados")]),
    ], className="mt-1"),
    # Linha 4 - KPIs de tempo médio de atendimento
    dbc.Row([
        dbc.Col(
            dbc.Card(
                [dbc.CardHeader(html.H3("Tempo médio de atendimento (min)")),
                 dbc.CardBody(html.H2(id="output-media-atendimento"))]
            ), width=6, className="text-center"),
        dbc.Col(
            dbc.Card(
                [dbc.CardHeader(html.H3("Tempo médio de espera (min)")),
                 dbc.CardBody(html.H2(id="output-media-espera"))]
            ), width=6, className="text-center"),
    ]),
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
])


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
    [Input("my-date-picker", "date")]
)
def update_kpis(dia):
    """Calcula os KPIs de acordo com a data."""
    # Percentual atendido em até 1 minuto
    dff = df.loc[df["date"] == dia]
    percent = dff["meets_standard"].mean()
    # Chamados por dia
    callers = df.groupby(["date"])["daily_caller"].max()[dia]

    # Média tempo de atendimento
    media_atendimento = df.groupby(["date"])["service_length"].mean()[dia]
    media_atendimento = strftime("%M:%S", gmtime(media_atendimento))
    # Média tempo de espera
    media_espera = df.groupby(["date"])["wait_length"].mean()[dia]
    media_espera = strftime("%M:%S", gmtime(media_espera))
    # Taxa de desistência
    if len(dff) > 0:
        taxa_desistencia = len(df.loc[(df["service_length"] < 30) &
                                      (df["date"] == dia)]) / len(dff)
    else:
        taxa_desistencia = 0
    # Percentual de utilização
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
     Input("crossfilter-percentil", "value")]
)
def update_figures_percentual(dia, tipo):
    """Função de callback dos gráficos dos KPIs."""
    if dia == "2021-12-31T00:00:00":
        dia = "2021-12-31"
    # Gráficos para cada um dos KPIS
    mes = df.loc[df["date"].dt.month ==
                 datetime.strptime(dia, '%Y-%m-%d').month]

    # Gráficos do percentual
    percent_std = round(mes.groupby(["date"])["meets_standard"].mean(), 2)
    print("percent \n", type(percent_std))
    if tipo == "Bar Plot":
        try: 
            percent_graph = px.bar(mes.groupby(["date"]),
                                x=mes["date"].unique(),
                                y=percent_std,
                                height=275,
                                color=percent_std,
                                color_continuous_scale="Bluered_r",
                                labels={"x": "Data", "y":"Atendimentos até 1 minuto"})
        except: 
            percent_graph = px.bar(mes.groupby(["date"]),
                                x=mes["date"].unique(),
                                y=percent_std,
                                height=275,
                                color=percent_std,
                                color_continuous_scale="Bluered_r",
                                labels={"x": "Data", "y":"Atendimentos até 1 minuto"})
        percent_graph.update_yaxes(range=[max(percent_std)*0.75, 1], tick0=0)

        percent_graph.add_shape(  # add a horizontal "target" line
            type="line", line_color="red", line_width=1, opacity=0.85, line_dash="dash",
            x0=1, x1=0, xref="paper", y0=0.9, y1=0.9, yref="y")
    
    elif tipo == "Scatter Plot":
        percent_graph = px.scatter(mes.groupby(["date"]),
                                x=mes["date"].unique(),
                                y=percent_std,
                                height=275,
                                color=percent_std,
                                color_continuous_scale="Bluered_r",
                                labels={"x": "Data", "y":"Atendimentos até 1 minuto"})
        percent_graph.add_shape(  # add a horizontal "target" line
            type="line", line_color="red", line_width=1, opacity=0.85, line_dash="dash",
            x0=1, x1=0, xref="paper", y0=0.9, y1=0.9, yref="y")
    elif tipo == "Histogram":

        percentil_std = pd.DataFrame()
        percentil_std["mean"] = percent_std.values
        print(percentil_std)
        percentil_std["cat"] = pd.cut(percentil_std["mean"], bins=[0,0.9,1.1], include_lowest=True, labels=["abaixo_90","acima_90"])
        print(percentil_std)

        percent_graph =px.histogram(percentil_std,
                               x=percentil_std["mean"],
                               height=275, color = percentil_std["cat"], color_discrete_map= {"acima_90": "blue", "abaixo_90": "red"})
    
        
    elif tipo == "Bubble Plot":
        percent_graph = px.scatter(mes.groupby(["date"]),
                                x=mes["date"].unique(),
                                y=percent_std,
                                height=275,
                                color=percent_std,
                                color_continuous_scale="Bluered_r",
                                size = mes.groupby(["date"])["daily_caller"].max(),
                                labels={"x": "Data", "y":"Atendimentos até 1 minuto"})
        percent_graph.add_shape(  # add a horizontal "target" line
            type="line", line_color="red", line_width=1, opacity=0.85, line_dash="dash",
            x0=1, x1=0, xref="paper", y0=0.9, y1=0.9, yref="y")
        
    elif tipo == "Box Plot":
        percent_graph =px.box(mes.groupby(["date"]),
                               x=percent_std,
                               height=275)

    

    percent_graph.update_layout(template=ggplot)
    return percent_graph


@app.callback(
    Output("grafico-chamados", "figure"),
    [Input("my-date-picker", "date"),
     Input("crossfilter-num-chamadas", "value")]
)
def update_figures_chamadas(dia, tipo):  # tipo_percent,tipo_num_chamadas):
    """Função de callback dos gráficos dos KPIs."""
    if dia == "2021-12-31T00:00:00":
        dia = "2021-12-31"
    mes = df.loc[df["date"].dt.month ==
                 datetime.strptime(dia, '%Y-%m-%d').month]
    print("mes \n",mes)
    if tipo == "Bar Plot":
        # Gráficos número de atendimentos BARPLOT
        maximo_mes  =max(mes.groupby(["date"])["daily_caller"].max())
        callers_graph = px.bar(mes.groupby(["date"]),
                               x=mes["date"].unique(),
                               y=mes.groupby(["date"])["daily_caller"].max(),
                               height=275,
                               color=mes.groupby(["date"])["daily_caller"].max(),
                               color_continuous_scale="bluered",
                               labels={"x": "Data", "y":"Nº de Chamadas no Dia"})
        callers_graph.update_yaxes(range=[maximo_mes*0.75, maximo_mes*1.1], tick0=0)
    elif tipo == "Histogram":
        callers_graph = px.histogram(mes.groupby(["date"]),
                               x=mes.groupby(["date"])["daily_caller"].max(),
                               height=275)
                               

    elif tipo == "Scatter Plot":
        maximo_mes  =max(mes.groupby(["date"])["daily_caller"].max())
        callers_graph = px.scatter(mes.groupby(["date"]),
                               x=mes["date"].unique(),
                               y=mes.groupby(["date"])["daily_caller"].max(),
                               height=275,
                               color=mes.groupby(["date"])["daily_caller"].max(),
                               color_continuous_scale="bluered",
                               labels={"x": "Data", "y":"Nº de Chamadas no Dia"})
        callers_graph.update_yaxes(range=[maximo_mes*0.75, maximo_mes*1.1], tick0=0)
    elif tipo == "Bubble Plot":
        percent_std = round(mes.groupby(["date"])["meets_standard"].mean(), 2)

        maximo_mes  =max(mes.groupby(["date"])["daily_caller"].max())
        callers_graph = px.scatter(mes.groupby(["date"]),
                               x=mes["date"].unique(),
                               y=mes.groupby(["date"])["daily_caller"].max(),
                               size = percent_std,
                               height=275,
                               color=mes.groupby(["date"])["daily_caller"].max(),
                               color_continuous_scale="bluered",
                               labels={"x": "Data", "y":"Nº de Chamadas no Dia"})
        callers_graph.update_yaxes(range=[maximo_mes*0.75, maximo_mes*1.1], tick0=0)
    elif tipo == "Box Plot":
        callers_graph = px.box(mes.groupby(["date"]),
                               x=mes.groupby(["date"])["daily_caller"].max(),
                               height=275)
    
    callers_graph.update_layout(template=ggplot)
    return callers_graph


# --------------------------------------------------------------------------- #
# Run server
if __name__ == '__main__':
    app.run_server(debug=True)
