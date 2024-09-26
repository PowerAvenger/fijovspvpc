import streamlit as st
import pandas as pd
from backend import obtener_datos_horarios, obtener_tabla_filtrada,grafico_horario_consumo,grafico_horario_coste,grafico_horario_precio,obtener_datos_por_periodo,graf_consumos_queso,graf_costes_queso
import datetime
import numpy as np
#from datetime import datetime

#Definimos constantes
#dias_periodo=30
iee=0.051127
iva=0.21
tp_boe=26.36
tp_margen_pvpc=3.12

#Inicializamos variables
pot_con=4.0
consumo_anual=4000
precio_ene=12.0
tp_fijo=40.0
#porcentajes_consumo=[40,40,20]

#obtenemos datos de backend


#configuramos la web y cabecera
st.set_page_config(
    page_title="fijovspvpc",
    page_icon=":bulb:",
    layout='wide',
    initial_sidebar_state='collapsed'
)
st.title('Comparador de precios fijos vs new PVPC 2024')
st.caption(f"Dedicado a **Fernando Sánchez Rey-Maeso** y a **Alfonso Zárate Conde** por sus contribuciones a la causa. Copyright by **Jose Vidal** :ok_hand:")
url_apps = "https://powerappspy-josevidal.streamlit.app/"
st.write("Visita mi mini-web de [PowerAPPs](%s) con un montón de utilidades." % url_apps)
url_linkedin = "https://www.linkedin.com/posts/jfvidalsierra_powerapps-activity-7216715360010461184-YhHj?utm_source=share&utm_medium=member_desktop"
st.write("Deja tus comentarios y propuestas en mi perfil de [Linkedin](%s)" % url_linkedin)


if 'porcentajes_consumo' in st.session_state:
    porcentajes_consumo=st.session_state['porcentajes_consumo']

#barra lateral con herramientas opcionales
st.sidebar.header('Herramientas adicionales')
with st.sidebar.form('form2'):
        st.subheader('Calcular Tp BOE anual')
        precio_tp_dia=st.number_input('potencia €/kW dia',min_value=0.072,max_value=0.164,step=.001, format="%f")
        precio_tp_año=round(precio_tp_dia*366,2)
        if precio_tp_año<tp_boe:
            precio_tp_año=tp_boe

        st.form_submit_button('Calcular')
        st.write(f'Precio Tp anual en €/kW año = {precio_tp_año}')



#precios_3p=st.sidebar.toggle('Usar tres precios de energía')
#if precios_3p:
#    with st.sidebar.container(border=True):
    #with st.sidebar.form('form3'):
            
#            st.subheader('Unidades en c€/kWh')
            
            
#            precio_fijo_p1=st.number_input('Precio P1',value=0.1600,step=0.001,format='%0.3f') #,
#            precio_fijo_p2=st.number_input('Precio P2',value=0.1300,step=0.001,format='%0.3f')
#            precio_fijo_p3=st.number_input('Precio P3',value=0.110,step=0.001,format='%0.3f')

#            precios_fijos=[precio_fijo_p1,precio_fijo_p2,precio_fijo_p3]
            #st.write(precios_fijos)
#            precio_ene=np.sum(np.multiply(porcentajes_consumo,precios_fijos)) #/100
#            st.write(f'El precio fijo medio es {precio_ene:.2f}')
            #st.write(porcentajes_consumo)

            #st.form_submit_button('Calcular')   



ultimo_registro,dias_registrados,df_datos_horarios_combo=obtener_datos_horarios()
#dias_periodo=dias_registrados #cambiar a dias_registrados
#ultimo_registro=obtener_fecha_reg_max()

# Establecemos layout de introducción de datos
col1,col2,col3=st.columns(3)
with col1:
    with st.form('Form1'):
        st.subheader('1. Introduce datos de potencia y consumo')
        pot_con=st.slider('Potencias Contratadas P1,P2 (kW)',min_value=1.0,max_value=9.9,step=.1,value=pot_con)
        consumo_anual=st.slider('Consumo :blue[ANUAL] estimado (kWh)',min_value=500, max_value=5000,step=100,value=consumo_anual)
        
        st.form_submit_button('Actualizar cálculos')
        
with col2:
    #with st.form('Form2'):
    with st.container(border=True):
        st.subheader('2.Introduce datos del contrato a precio fijo')
        tp_fijo=st.slider('Precio ofertado: término de potencia (€/kW año)',min_value=tp_boe,max_value=60.0,step=.1,value=tp_fijo)
        precios_3p=st.toggle('Usar tres precios de energía')
        if precios_3p:
            col21,col22,col23=st.columns(3)
            with col21:           
                precio_fijo_p1=st.number_input('Precio P1',value=0.1600,step=0.001,format='%0.3f') #,
            with col22:
                precio_fijo_p2=st.number_input('Precio P2',value=0.1300,step=0.001,format='%0.3f')
            with col23:
                precio_fijo_p3=st.number_input('Precio P3',value=0.110,step=0.001,format='%0.3f')

            precios_fijos=[precio_fijo_p1,precio_fijo_p2,precio_fijo_p3]
            #st.write(precios_fijos)
            precio_ene=np.sum(np.multiply(porcentajes_consumo,precios_fijos)) #/100
            st.write(f'El precio fijo medio es :red[{precio_ene:.2f}]c€/kWh')
        else:
            precio_ene=st.slider('Precio ofertado: término de energía (c€/kWh)',min_value=5.0, max_value=30.0,step=.1,value=precio_ene)
        #st.form_submit_button('Calcular coste fijo')
        
with col3:
    with st.form('Form3'):
        st.subheader('3.Introduce datos del periodo a analizar')
        
        ultimo_registro_mostrar=ultimo_registro.strftime('%d.%m.%Y')
        st.caption(f'El último registro PVPC disponible es del  :blue[{ultimo_registro_mostrar}]')

        st.caption(f'Número de dias registrados 2024: :blue[{dias_registrados}]')
        fechas_periodo=st.date_input('Selecciona el periodo a analizar',(datetime.date(2024, 1, 1),ultimo_registro),min_value=datetime.date(2024, 1, 1),max_value=ultimo_registro,format="DD.MM.YYYY")
        fecha_inicio,fecha_fin=fechas_periodo 
        fecha_inicio=pd.to_datetime(fecha_inicio)
        fecha_fin=pd.to_datetime(fecha_fin) #datetime.date(2024, 1, 31)
        dias_periodo=(fecha_fin-fecha_inicio).days +1
        #st.write(dias_periodo)
        consumo_periodo=round(consumo_anual*dias_periodo/366) #consumo del periodo seleccionado. año bisiesto
        #fecha_fin=st.date_input('Selecciona la fecha final',min_value=fecha_inicio,max_value=ultimo_registro,format="DD.MM.YYYY")
        #st.write(fecha_inicio)
        #fecha_hoy=datetime.today().date
        #st.write(fecha_hoy)
        #st.write(ultimo_registro)
        #fecha_mes_ini=fecha_hoy.replace(day=1)
        #rango_fechas=st.date_input('Selecciona el rango de fechas',min_value=datetime.date(2024, 1, 1),max_value=ultimo_registro,format="DD.MM.YYYY")
        #st.write(rango_fechas)
        #fecha_fin=rango_fechas[0]

        #fecha_fin=pd.to_datetime(fecha_fin)
        
            #submitted3=st.form_submit_button('Enviar')
        #else:
        #mes_analisis==2024

        st.form_submit_button('Actualizar periodo')  

df_datos_horarios_combo_filtrado_consumo,pt_horario_filtrado,media_precio_perfilado,coste_pvpc_perfilado=obtener_tabla_filtrada(df_datos_horarios_combo, fecha_inicio, fecha_fin, consumo_periodo)

## CÁLCULOS
# Cálculo del PVPC
tp_pvpc=tp_boe+tp_margen_pvpc
tp_coste_pvpc=tp_pvpc*pot_con*dias_periodo/366
te_pvpc=media_precio_perfilado
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
    st.subheader('Datos resumen del periodo analizado',divider='gray')
    fecha_inicio_mostrar=fecha_inicio.strftime('%d.%m.%Y')
    fecha_fin_mostrar=fecha_fin.strftime('%d.%m.%Y')
    #st.write(f'Periodo seleccionado del {fecha_inicio_mostrar} al {fecha_fin_mostrar}') 
    st.markdown(f':blue-background[Periodo seleccionado del {fecha_inicio_mostrar} al {fecha_fin_mostrar}]')
    
    col101,col102,col103=st.columns(3)
    with col101:
        st.metric('Consumo periodo (kWh)', consumo_periodo)
    with col102:
        st.metric('Precio medio del PVPC (c€/kWh)',round(te_pvpc*100,2),help='Precio medio del PVPC perfilado en el periodo seleccionado (c€/kWh)')

with col11:
    st.subheader('Datos adicionales oferta FIJO',divider='gray')
    st.markdown(f':blue-background[Obtén información del sobrecoste del término de potencia. Sección **Fernando Sánchez Rey-Maeso**]',help='Sobrecoste con respecto al margen regulado del PVPC')

    col111,col112,col113=st.columns(3)
    with col111:
        st.metric('Margen Tp (€/kW año)',tp_margen_fijo)
    with col112:
        st.metric('Sobrecoste Tp (€)',sobrecoste_tp) #,f'{sobrecoste_tp_porc} %','inverse') es el mismo que el anual
    with col113:
        with st.container(border=True):
            st.metric('Sobrecoste Tp ANUAL (€)',sobrecoste_tp_anual,f'{sobrecoste_tp_porc} %','inverse')
with col12:
    # Resultados a mostrar
    st.subheader(':orange-background[Resultados comparativa total factura]',divider='rainbow')
    st.markdown(f':blue-background[Incluye todos los términos excepto alquiler de medida. Sección **Alfonso Zárate Conde**]')

    col4,col5,col6=st.columns(3)
    with col4:
        st.metric('Coste PVPC (€)',coste_pvpc)
    with col5: 
        st.metric('Coste FIJO (€)', coste_fijo)
    with col6:
        with st.container(border=True):
            st.metric('Sobrecoste FIJO (€)', dif_pvpc_fijo,f'{dif_pvpc_fijo_porc} %','inverse')



##GRÁFICOS 1
grafico_consumo=grafico_horario_consumo(pt_horario_filtrado)
grafico_coste=grafico_horario_coste(pt_horario_filtrado)
grafico_precio=grafico_horario_precio(pt_horario_filtrado)

col20,col21,col22=st.columns(3)
with col20:
    # Algunos datos de salida a mostrar
    st.subheader('Gráfico de consumo perfilado REE 2.0TD',divider='gray')
    st.write(grafico_consumo)
    
with col21:
    st.subheader('Gráfico de coste del PVPC perfilado',divider='gray')
    st.write(grafico_coste)
    
with col22:
    st.subheader('Gráfico del PVPC medio horario perfilado',divider='gray')
    st.write(grafico_precio)



##GRÁFICOS 2
pt_periodos_filtrado, pt_periodos_filtrado_porc, totales_periodo=obtener_datos_por_periodo(df_datos_horarios_combo_filtrado_consumo)
graf_consumos_queso=graf_consumos_queso(pt_periodos_filtrado_porc)
graf_costes_queso=graf_costes_queso(pt_periodos_filtrado_porc)

col30,col31,col32=st.columns(3)
with col30:
    st.subheader('Distribución de consumos y costes en %',divider='gray')
    col301,col302=st.columns(2)
    with col301:
        st.write(graf_consumos_queso)
    with col302:
        st.write(graf_costes_queso)
    
#with col32:
#    st.subheader('Provisional',divider='gray')
    #st.write(grafico_precio)
#    st.write(pt_periodos_filtrado)
#    st.write(pt_periodos_filtrado_porc)
#    st.write(totales_periodo)

#obtenemos tabla con los tres porcentajes de consumo. usado para obtener el precio fijo de 3P
st.session_state['porcentajes_consumo']=pt_periodos_filtrado_porc['consumo']
#st.write(st.session_state['porcentajes_consumo'])

#st.text(f'El margen aplicado al término de potencia es {margenpot} €/kW año')
#st.text(f'El precio fijo ofertado es {precioene} c€/kWh')
#st.text(f'El coste del PVPC término de potencia es {tp_coste_pvpc}€')
#st.text(f'El coste del PVPC término de energía es {te_coste_pvpc}€')
#st.text(f'El coste total del PVPC es {coste_pvpc}€')
#st.text(f'El coste del FIJO término de potencia es {tp_coste_fijo}€')
#st.text(f'El coste del FIJO término de energía es {te_coste_fijo}€')
#st.text(f'El coste total del FIJO es {coste_fijo}€')



