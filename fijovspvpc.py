import streamlit as st
import pandas as pd
from backend import calcular_media_pvpc,obtener_dias,obtener_fecha_reg_max

#Definimos constantes
#dias_periodo=30
iee=0.051127
iva=0.21
tp_boe=26.36
tp_margen_pvpc=3.12

#Inicializamos variables
pot_con=3.0
consumo=3000
precio_ene=10.0
tp_fijo=40.0

#obtenemos datos de backend
dias_periodo=obtener_dias()
ultimo_registro=obtener_fecha_reg_max()


#configuramos la web y cabecera
st.set_page_config(
    page_title="fijovspvpc",
    page_icon=":bulb:",
    layout='wide',
)
st.title('Comparador precios fijos vs PVPC')
st.caption("Copyright by Jose Vidal :ok_hand:")
url_apps = "https://powerappspy-josevidal.streamlit.app/"
st.write("Visita mi mini-web de [PowerAPPs](%s) con un montón de utilidades." % url_apps)
url_linkedin = "https://www.linkedin.com/posts/jfvidalsierra_powerapps-activity-7216715360010461184-YhHj?utm_source=share&utm_medium=member_desktop"
st.write("Deja tus comentarios y propuestas en mi perfil de [Linkedin](%s)" % url_linkedin)

#barra lateral con herramientas opcionales
st.sidebar.header('Herramientas adicionales')
with st.sidebar.form('form2'):
        st.subheader('Calcular Tp anual')
        precio_tp_dia=st.number_input('potencia €/kW dia',min_value=0.072,max_value=0.164,step=.001, format="%f")
        precio_tp_año=round(precio_tp_dia*366,2)
        if precio_tp_año<tp_boe:
            precio_tp_año=tp_boe
        st.form_submit_button('Calcular')

        st.write(f'Precio Tp anual en €/kW año = {precio_tp_año}')
# Establecemos layout de introducción de datos
col1,col2,col3=st.columns(3)
with col1:
    with st.form('Form1'):
        st.subheader('1. Datos de potencia y consumo')
        pot_con=st.slider('Potencias Contratadas P1,P2 (kW)',min_value=1.0,max_value=9.9,step=.1,value=pot_con)
        consumo=st.slider('Consumo ANUAL estimado (kWh)',min_value=500, max_value=5000,step=100,value=consumo)
        consumo_periodo=round(consumo*dias_periodo/365)
        st.form_submit_button('Actualizar cálculos')
        
with col2:
    with st.form('Form2'):
        st.subheader('2.Datos del contrato a precio fijo')
        tp_fijo=st.slider('Precio ofertado: término de potencia (€/kW año)',min_value=tp_boe,max_value=60.0,step=.1,value=tp_fijo)
        precio_ene=st.slider('Precio ofertado: término de energía (c€/kWh)',min_value=5.0, max_value=30.0,step=.1,value=precio_ene)
        st.form_submit_button('Calcular coste fijo')
        
with col3:
    with st.form('Form3'):
        st.subheader('3.Datos del periodo a analizar')
        on = st.toggle('Habilitar selección por meses (próximamente)')
        mes_analisis=None
        #if on:
        #    mes_analisis=st.slider('Seleccionar periodo de cálculo (número del mes - año 2024)',min_value=1,max_value=7,step=1,value=1,key='key')
            #submitted3=st.form_submit_button('Enviar')
        #else:
        #mes_analisis==2024

        st.form_submit_button('Enviar')  

## CÁLCULOS
# Cálculo del PVPC
tp_pvpc=tp_boe+tp_margen_pvpc
tp_coste_pvpc=tp_pvpc*pot_con*dias_periodo/366
te_pvpc=calcular_media_pvpc(mes_analisis)/1000
te_coste_pvpc=round(te_pvpc*consumo_periodo,2)
coste_pvpc=round((tp_coste_pvpc+te_coste_pvpc)*(1+iee)*(1+iva),2)
# Cálculo del FIJO a fecha último registro
tp_margen_fijo=+round(tp_fijo-tp_boe,2)
tp_coste_fijo=tp_fijo*pot_con*dias_periodo/366
te_fijo=precio_ene/100
te_coste_fijo=round(te_fijo*consumo_periodo,2)
coste_fijo=float(f"{round((tp_coste_fijo+te_coste_fijo)*(1+iee)*(1+iva),2):.2f}")
# Cálculo de la diferencia PVPC menos FIJO
sobrecoste_tp=round(tp_coste_fijo-tp_coste_pvpc,2)
sobrecoste_tp_porc=round(100*sobrecoste_tp/tp_pvpc,2)
dif_pvpc_fijo=round(coste_fijo-coste_pvpc,2)
dif_pvpc_fijo_porc=round(100*dif_pvpc_fijo/coste_pvpc,2)
# Cálculo del FIJO ANUAL
tp_coste_fijo_anual=tp_fijo*pot_con
tp_coste_pvpc_anual=tp_pvpc*pot_con
sobrecoste_tp_anual=round(tp_coste_fijo_anual-tp_coste_pvpc_anual,2)

##SALIDA DE DATOS
col10,col11,col12=st.columns(3)
with col10:
    # Algunos datos de salida a mostrar
    st.subheader('Datos adicionales PVPC',divider='gray')
    col101,col102=st.columns([0.6,0.4])
    with col101:
        st.caption(f'El último registro PVPC disponible es del  :blue[{ultimo_registro}]')
        st.caption(f'Dias registros 2024: :blue[{dias_periodo}]')
        st.caption(f'El consumo realizado es :blue[{consumo_periodo}] kWh')
        
    with col102:
        st.metric('Precio medio del PVPC (c€/kWh)',round(te_pvpc*100,2),help='Precio medio del PVPC (c€/kWh)')
with col11:
    st.subheader('Datos adicionales oferta FIJO',divider='gray')
    col111,col112,col113=st.columns(3)
    with col111:
        st.metric('Margen Tp (€/kW año)',tp_margen_fijo)
    with col112:
        st.metric('Sobrecoste Tp (€)',sobrecoste_tp,f'{sobrecoste_tp_porc} %','inverse')
    with col113:
        with st.container(border=True):
            st.metric('Sobrecoste Tp ANUAL (€)',sobrecoste_tp_anual,f'{sobrecoste_tp_porc} %','inverse')
with col12:
    # Resultados a mostrar
    st.subheader(':blue-background[Resultados]',divider='rainbow')
    col4,col5,col6=st.columns(3)
    with col4:
        st.metric('Coste PVPC (€)',coste_pvpc)
    with col5: 
        st.metric('Coste FIJO (€)', coste_fijo)
    with col6:
        with st.container(border=True):
            st.metric('Sobrecoste FIJO (€)', dif_pvpc_fijo,f'{dif_pvpc_fijo_porc} %','inverse')




#st.text(f'El margen aplicado al término de potencia es {margenpot} €/kW año')
#st.text(f'El precio fijo ofertado es {precioene} c€/kWh')
#st.text(f'El coste del PVPC término de potencia es {tp_coste_pvpc}€')
#st.text(f'El coste del PVPC término de energía es {te_coste_pvpc}€')
#st.text(f'El coste total del PVPC es {coste_pvpc}€')
#st.text(f'El coste del FIJO término de potencia es {tp_coste_fijo}€')
#st.text(f'El coste del FIJO término de energía es {te_coste_fijo}€')
#st.text(f'El coste total del FIJO es {coste_fijo}€')



