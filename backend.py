# %%
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import datetime
from datetime import datetime




# %%
API_KEY=st.secrets['ESIOS_API_KEY']

# %%
def download_esios_id(id,fecha_ini,fecha_fin,agrupacion):
                       token = API_KEY
                       
                       cab = dict()
                       cab ['x-api-key']= token
                       url_id = 'https://api.esios.ree.es/indicators'
                       url=f'{url_id}/{id}?geo_ids[]=8741&time_agg=average&start_date={fecha_ini}T00:00:00&end_date={fecha_fin}T23:59:59&time_trunc={agrupacion}'
                       print(url)
                       response = requests.get(url, headers=cab).json()
                       print(response)

                       return response
                       

# %%
id='10391'
fecha_ini='2024-01-01'
fecha_fin='2024-12-31'
agrupacion='day'


# %%
datos_origen =download_esios_id(id,fecha_ini,fecha_fin,agrupacion)


# %%
datos=pd.DataFrame(datos_origen['indicator']['values'])
datos

# %%
#datos=datos[datos['geo_name'].str.contains('Península')]

# %%
datos = (datos
         .assign(datetime=lambda vh_: pd #formateamos campo fecha, desde un str con diferencia horaria a un naive
                      .to_datetime(vh_['datetime'],utc=True)  # con la fecha local
                      .dt
                      .tz_convert('Europe/Madrid')
                      .dt
                      .tz_localize(None)
                ) 
             #.drop(['datetime','datetime_utc','tz_time','geo_id','geo_name'],
             #      axis=1) #eliminamos campos
             
             .loc[:,['datetime','value']]
             )

datos

# %%
meses = {
    'January': 'Enero',
    'February': 'Febrero',
    'March': 'Marzo',
    'April': 'Abril',
    'May': 'Mayo',
    'June': 'Junio',
    'July': 'Julio',
    'August': 'Agosto',
    'September': 'Septiembre',
    'October': 'Octubre',
    'November': 'Noviembre',
    'December': 'Diciembre'
}

# %% [markdown]
# ### Esta es la tabla de valores horarios tratada

# %%
#datos['fecha']=datos['datetime'].dt.strftime('%d/%m/%Y')
#datos['fecha']=pd.to_datetime(datos['fecha'],format='%d/%m/%Y')
datos['fecha']=datos['datetime'].dt.date
#datos['fecha']=pd.to_datetime(datos['fecha']).dt.date
datos['hora']=datos['datetime'].dt.hour
datos['dia']=datos['datetime'].dt.day
datos['mes']=datos['datetime'].dt.month
datos['año']=datos['datetime'].dt.year
datos.set_index('datetime', inplace=True)
datos

# %%
datos.dtypes

# %%
def obtener_fecha_reg_max():
    
    ultimo_registro= datos['fecha'].max()
    
    return ultimo_registro

# %%
ultimo_registro=obtener_fecha_reg_max()
ultimo_registro

# %%
primer_registro=datos['fecha'].min()

# %%
def obtener_dias():
    dias=(ultimo_registro-primer_registro).days
    
    return dias

# %%
fecha_hoy=datetime.today().date()
fecha_hoy

# %%
hora=datetime.now().hour
hora

# %% [markdown]
# 
# if hora>14:
#     st.rerun()
#     flag=False

# %%
valor_minimo_horario=datos['value'].min()
valor_maximo_diario=datos['value'].max()
valor_minimo_horario,valor_maximo_diario

# %% [markdown]
# ### Copia para escala de colores

# %% [markdown]
# datos_horarios=datos
# datos_horarios
# 

# %% [markdown]
# ### Agrupación por días

# %%
datos_dias=datos.reset_index()
datos_dias

# %%
datos_dia=datos.drop(columns=['hora'])
datos_dia['fecha']=pd.to_datetime(datos['fecha'],format='%d/%m/%Y')
#datos_dia['fecha']=datos_dia['fecha'].dt.strftime('%d/%m/%Y')


datos_dia=datos_dia.resample('D').mean()
datos_dia['value']=datos_dia['value'].round(2)

datos_dia[['dia','mes','año']]=datos_dia[['dia','mes','año']].astype(int)


# %%
datos_dia

# %%
valor_minimo_diario=datos_dia['value'].min()
valor_maximo_diario=datos_dia['value'].max()
valor_minimo_diario,valor_maximo_diario

# %% [markdown]
# ### Agrupación por meses

# %%
datos

# %%
datos_mes=datos.drop(columns=['fecha','hora', 'dia'])
datos_mes=datos_mes.resample('M').mean()
datos_mes['value']=datos_mes['value'].round(2)

datos_mes[['mes','año']]=datos_mes[['mes','año']].astype(int)
datos_mes

# %% [markdown]
# ### Definimos la escala y sus límites

# %%
datos_limites = {
    'rango': [-10,20.01,40.01,60.01,80.01,100.01,10000],
    'valor_asignado': ['muy bajo', 'bajo','medio','alto','muy alto','chungo','xtrem'],
}

# %%
df_limites=pd.DataFrame(datos_limites)
df_limites

# %%
#etiquetas = df_limites['valor_asignado'][:-1]
etiquetas = df_limites['valor_asignado'][:-1]
etiquetas

# %% [markdown]
# ### Añadimos la columna escala a todas las tablas

# %% [markdown]
# datos_horarios['escala']=pd.cut(datos_horarios['value'],bins=df_limites['rango'],labels=etiquetas,right=True)
# #datos_horarios['escala']=pd.cut(datos_horarios['value'],bins=df_limites['rango'],labels=etiquetas)
# #datos_horarios['escala']=pd.cut(datos_horarios['value'],bins=df_limites['rango'],labels=df_limites['valor_asignado'],right=False)
# datos_horarios

# %% [markdown]
# lista_escala=datos_horarios['escala'].unique()
# lista_escala

# %%
datos_dia['escala']=pd.cut(datos_dia['value'],bins=df_limites['rango'],labels=etiquetas,right=False)
datos_dia

# %%
datos_mes['escala']=pd.cut(datos_mes['value'],bins=df_limites['rango'],labels=etiquetas,right=False)
datos_mes

# %% [markdown]
# ### Definimos los colores según la escala

# %%
colores = {
    'muy bajo': 'lightgreen',
    'bajo': 'green',
    'medio': 'blue',
    'alto': 'orange',
    'muy alto': 'red',
    'chungo': 'purple',
    'xtrem':'black'
}

# %% [markdown]
# datos_horarios['color']=datos_horarios['escala'].map(colores)
# datos_horarios

# %%
datos_dia['color']=datos_dia['escala'].map(colores)
datos_dia

# %% [markdown]
# ### Obtenemos la escala ordenada al revés para el gráfico horario

# %%
valor_asignado_a_rango = {row['valor_asignado']: row['rango'] for _, row in df_limites.iterrows()}

# %% [markdown]
# escala_horaria=['alto', 'medio', 'bajo', 'muy bajo', 'muy alto', 'chungo']
# escala_horaria

# %% [markdown]
# escala_ordenada_hora = sorted(escala_horaria, key=lambda x: valor_asignado_a_rango[x], reverse=True)
# escala_ordenada_hora

# %% [markdown]
# datos_horarios['color']=datos_horarios['escala'].map(colores)
# datos_horarios

# %% [markdown]
# datos_horarios['escala']=pd.Categorical(datos_horarios['escala'],categories=escala_ordenada_hora, ordered=True)
# datos_horarios

# %% [markdown]
# ### Obtenemos la escala ordenada al reves para el gráfico diario

# %%
escala_dia=datos_dia['escala'].unique()
escala_dia

# %%
escala_ordenada_dia = sorted(escala_dia, key=lambda x: valor_asignado_a_rango[x], reverse=True)
escala_ordenada_dia

# %%
datos_mes['color']=datos_mes['escala'].map(colores)
datos_mes

# %% [markdown]
# ### Obtenemos la escala ordenada al reves para el gráfico mensual

# %%
escala_mes= datos_mes['escala'].unique()
escala_mes

# %%
escala_ordenada_mes = sorted(escala_mes, key=lambda x: valor_asignado_a_rango[x], reverse=True)
escala_ordenada_mes

# %% [markdown]
# ### Esta tabla se usa para el gráfico grande de barras diario

# %%

datos_dia['escala']=pd.Categorical(datos_dia['escala'],categories=escala_ordenada_dia, ordered=True)
datos_dia

# %% [markdown]
# ### Estos datos se usan para el grafico de barras mensual

# %%
datos_mes['escala']=pd.Categorical(datos_mes['escala'],categories=escala_ordenada_mes, ordered=True)
datos_mes

# %% [markdown]
# ### Estos datos se usan para el quesito

# %%
datos_dia_queso=datos_dia.groupby(['escala'])['escala'].count()
datos_dia_queso=datos_dia_queso.reset_index(name='num_dias')
datos_dia_queso


# %% [markdown]
# ### Gráfico de barras principal

# %%
#datos_dia.reset_index()
#datos_dia.rename(columns={'datetime','fecha'},inplace=True)
datos_dia
#datos_dia['datetime'].rename['fecha']

# %%
datos_dia.dtypes

# %%
def graf_ecv_anual():
    graf_ecv_anual=px.bar(datos_dia, x='fecha', y='value', 
        color='escala',
        color_discrete_map=colores,
        category_orders={'escala':escala_ordenada_dia},
        labels={'value':'precio medio diario €/MWh', 'escala':'escala_cv'},
        title="Precios medios del mercado diario OMIE. Año 2024")
    graf_ecv_anual.update_xaxes(
        showgrid=True
    )
    graf_ecv_anual.update_traces(
        marker_line_width=0
    )

    return graf_ecv_anual

# %%
graf_ecv_anual()

# %%
def graf_ecv_mensual():
    graf_ecv_mensual=px.bar(datos_mes, x='mes', y='value',
        color='escala',
        color_discrete_map=colores,
        category_orders={'escala':escala_ordenada_mes},
        labels={'value':'precio medio mensual €/MWh', 'escala':'escala_cv'},
        title="Precios medios mensuales. Año 2024"
        )
    #graf_ecv_mensual.update_xaxes(
    #    showgrid=True
    
    #graf_ecv_mensual.update_traces(
    #   marker_line_width=0
    #)

    return graf_ecv_mensual

# %%
graf_ecv_mensual()

# %% [markdown]
# ### Gráfico de queso

# %%
def graf_ecv_anual_queso():
    graf_ecv_anual_queso=px.pie(datos_dia_queso, values='num_dias', names='escala',
        color='escala',
        color_discrete_map=colores,
        #marker=dict(colors=colores),
        category_orders={'escala':escala_ordenada_dia},
        labels={'num_dias':'num_dias', 'escala':'escala_cv'},
        title="% y número de días según la Escala CV. Año 2024",
        width=500
        )
    
    return graf_ecv_anual_queso

# %%
graf_ecv_anual_queso()

# %% [markdown]
# ## Cálculo del precio medio del PVPC

# %%
def filtrar_mes(mes):
    if mes !=None:
        filtro_mes=datos['mes']==mes
        datos_filtrados_mes=datos[filtro_mes]
    else:
        datos_filtrados_mes=datos
    
    pvpc_media=datos_filtrados_mes['value'].mean()
    
    return datos_filtrados_mes


# %%
def calcular_media_pvpc(mes):
    if mes !=None:
        datos_filtrados_mes=datos
    else:
        datos_filtrados_mes=filtrar_mes(mes)
    
    pvpc_media=datos_filtrados_mes['value'].mean()
    #pvpc_media

    return pvpc_media

# %%
calcular_media_pvpc(1)

# %%

datos_filtrados_mes=filtrar_mes(1)
datos_filtrados_mes


# %% [markdown]
# datos_filtrados_dia=datos_filtrados.resample('D').mean()
# datos_filtrados_dia

# %%


# %%


# %% [markdown]
# def graf_dia():
#     graf_dia=px.line(datos_filtrados_dia,x='fecha',y='value')
#     
#     return graf_dia

# %% [markdown]
# graf_dia()

# %%



