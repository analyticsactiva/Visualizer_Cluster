import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher
import yaml
from yaml.loader import SafeLoader

def cluster_label(cluster):
    dic_cluster = {
        1: 'Práctico y Consciente',
        2: 'Versátil y Ahorrador',
        3: 'Vigilante de la salud',
        4: 'Multitasking protector',
        5: 'Tradicional Saludable'
    }
    return dic_cluster[cluster]

def plot_df(df,normalize=True):
    #labels = df['Etiqueta_Cluster'].value_counts(normalize=True).index
    values = df['Cluster'].value_counts(normalize=normalize).values * 100

    labels = np.around(values, decimals=2)

    #trace = go.Pie(labels=labels, values=values)

    fig,ax = plt.subplots()

    ax.pie(values,labels=labels,shadow=False)
    #ax.legend(df['Etiqueta_Cluster'].values)

    x = np.arange(10)

    #for i in range(5):
    #    ax.plot(x, i * x, label='$y = %ix$'%i)

    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # Put a legend to the right of the current axis
    ax.legend(df['Etiqueta_Cluster'].values,loc='center left', bbox_to_anchor=(1, 0.5))

    #return plotly.iplot([trace], filename = 'pie_chart')
    return fig,ax



def agrupar_columnas_binarias(df):
    # Crear un DataFrame vacío para las nuevas columnas agrupadas
    df_agrupado = pd.DataFrame()

    # Obtener los nombres base (rango, categoria, etc.) sin los sufijos
    columnas_base = set(col.split('_')[0] for col in df.columns)

    for base in columnas_base:
        try:
            # Filtrar las columnas que corresponden a cada grupo
            cols_grupo = [col for col in df.columns if col.startswith(base)]
            # Sumar las columnas del mismo grupo
            df_agrupado[base] = df[cols_grupo].idxmax(axis=1).apply(lambda x: int(x.split('_')[-1]))
        except:
            df_agrupado[base] = df[base]
    return df_agrupado

seg_columns = ['ID','SEXO_1','SEXO_2','RANGOEDAD_1','RANGOEDAD_2','RANGOEDAD_3','RANGOEDAD_4',
               'V_GSE_1_1', 'V_GSE_1_2', 'V_GSE_1_3', 'V_GSE_1_4','Cluster']

dict_sex = {
    1:'Hombre',
    2:'Mujer'
}

dict_edad = {
    1:'15 a 17 años',
    2:'18 a 35 años',
    3:'36 a 55 años',
    4:'56 a 80 años'
}

dict_gse = {
    1:'ABC1',
    2:'C2',
    3:'C3',
    4:'D'
}


with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

hashed_passwords = Hasher(['Baf60255', 'activa1']).generate()

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('main', fields = {'Form name': 'Activa Research'})


if st.session_state["authentication_status"]:

    cols = st.columns(4)

    # the 3rd column
    with cols[3]:
        authenticator.logout("Logout", "main")
    #authenticator.logout('Logout', 'main')
    #st.write(f'Bienvenido *{st.session_state["name"]}*')
    #st.title('Some content')

    st.image('logo-activa.svg',width=100)

    st.title('Visualizador')

    # ------------------------ Cargar archivo ---------------------------------

    uploaded_file = st.file_uploader("Elegir Archivo", type = 'csv')
    # uploaded_file = st.file_uploader("Elegir Archivo", type = 'xlsx')
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        # df = pd.read_excel(uploaded_file)

        bd_seg = agrupar_columnas_binarias(df[seg_columns])
        bd_seg.rename(columns={'V':'GSE'}, inplace=True)
        bd_seg['Etiqueta_Cluster'] = bd_seg.Cluster.apply(cluster_label)

        bd_seg['GSE'] = bd_seg.GSE.map(dict_gse)
        bd_seg['SEXO'] = bd_seg.SEXO.map(dict_sex)
        bd_seg['RANGOEDAD'] = bd_seg.RANGOEDAD.map(dict_edad)

        Sexo_txt = ('Hombre','Mujer')

        sexo = st.multiselect('Sexo',Sexo_txt)

        Edad_txt = ('15 a 17 años','18 a 35 años','36 a 55 años','56 a 80 años')

        edad = st.multiselect('Rango Edad',Edad_txt)

        GSE_txt = ('ABC1','C2','C3','D')

        gse = st.multiselect('Grupo Socioeconómico', GSE_txt)

        df = bd_seg

        submit = st.button('Graficar')
        if submit:
            
            if sexo:
                #st.text(f"SEXO: {sexo}")
                df = df[df['SEXO'].isin(sexo)]
            if edad:
                #st.text(f"EDAD:  {edad}")
                df = df[df['RANGOEDAD'].isin(edad)]
            if gse:
                #st.text(f"GSE: {gse}")
                df = df[df['GSE'].isin(gse)]
            
            fig,ax = plot_df(df,normalize=True)
            st.pyplot(fig)

            #fig,ax = plot_df(df,normalize=False)
            #st.pyplot(fig)

elif st.session_state["authentication_status"] == False:
    st.error('Usuario/Contraseña incorrecta')
elif st.session_state["authentication_status"] == None:
    st.warning('Por favor ingrese su usuario y contraseña')