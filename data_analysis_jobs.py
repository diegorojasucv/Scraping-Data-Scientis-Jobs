"""
OBJETIVO: Calcular el porcentaje de apariciones de los lenguages de programacion y bibliotecas en las solicitudes de empleo para la posición de Data Scientist.
ELABORADO POR: Diego Rojas
FECHA DE ELABORACIÓN: Julio 2020
"""

import pandas as pd
import numpy as np
from pymongo import MongoClient
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec

# Seleccionamos la base de datos y la coleccion en Mongodb
client = MongoClient('localhost')
db = client['indeed']
col = db['data_scientist_jobs']

df = pd.DataFrame.from_dict(col.find(
                                    {},
                                    {
                                        '_id':0, 
                                        'title':1, 
                                        'item1':1, 
                                        'item2':1, 
                                        'item3':1
                                    }))

# Creamos una varibale que concatene todas las descripciones
df['all_item'] = df['item1'].astype(str) + ' ' + df['item2'].astype(str) + ' ' + df['item3'].astype(str)
df_all_item = pd.DataFrame(df['all_item'])

# Eliminados duplicados de posiciones que se repiten en varias paginas
df_all_item = df_all_item.drop_duplicates()

# Separamos cada una de las palabras en un nuevo dataframe
s = df_all_item.all_item.str.split(expand = True).stack().str.capitalize()
s.index = s.index.droplevel(-1)
s.name = 'all_item_2'
df_split = pd.DataFrame(s)

# Lo unimos al dataframe sin duplicados
df_split_all_item = df_all_item.join(df_split)

# Volvemos a eliminar duplicados. Esto lo hacemos para evitar que se repita un lenguage o biblioteca en la misma publicación 
df_split_all_item = df_split_all_item.drop_duplicates()

# Agrupamos para ver cuantas veces se repita cada palabra
df_grouped = df_split_all_item.groupby(['all_item_2']).size().reset_index(name = 'count').sort_values(by = 'count', ascending = False)

# Creamos una funcion para que corregir o homogeneizar algunas palabras
def correciones(texto):
    texto_corregido = (
        texto.replace('Sci-kit','Scikit-learn').replace('Sklearn','Scikit-learn')
        .replace('Slq','Sql').replace('Mysql','Sql').replace('Postgresql','Sql')
        .replace('Ggplot2','Ggplot').replace('Non-sql','Nosql').replace("Python's",'Python')
        .str.strip()
        )                    
    return texto_corregido

df_grouped['all_item_2'] = correciones(df_grouped['all_item_2'])
df_grouped = df_grouped.rename(columns = {"all_item_2": "Lenguages_all"})

# Realizamos el análisis para los lenguajes de programacion

# Filtramos por los lenguajes
filter_lenguages = ['Python','Sql','R','Spark','Hadoop','Java','C++'
                    ,'Sas','Hive','Matlab','Scala','Nosql','C','Pig'
                    ,'Go','Stata','C#','Weka','Cassandra','Mongodb'
                    ,'Impala','Ruby','Julia']

df_lenguajes = df_grouped[df_grouped.Lenguages_all.isin(filter_lenguages)]

# Contamos la cantidad de palabras
df_lenguages_grouped = pd.DataFrame(df_lenguajes.groupby('Lenguages_all')['count'].sum())

# Calculamos el % que aparece cada palabra dentro del total de lenguajes
df_lenguages_grouped['total'] = df_lenguages_grouped['count'].sum(axis = 0)
df_lenguages_grouped['percentage'] = round((df_lenguages_grouped['count']/df_lenguages_grouped['total'])*100,2)
df_lenguages_grouped = pd.DataFrame(df_lenguages_grouped).reset_index()

# Nos quedamos con los que tienen una participación mayor al 3%
df_lenguages_grouped['Lenguages'] = np.where(df_lenguages_grouped.percentage<3.0, 'Others', df_lenguages_grouped.Lenguages_all)
df_lenguages_grouped = pd.DataFrame(df_lenguages_grouped.groupby('Lenguages')['percentage'].sum()).reset_index().sort_values(by = 'percentage', ascending = False)

# Realizamos el analisis para las bibliotecas 

# Filtramos por las bibliotecas
filter_Libraries = ['Tensorflow','Scikit-learn','Pandas','Numpy'
                    ,'Pytorch','Keras','Pyspark','Matplotlib'
                    ,'Seaborn','Docker','Flask','Ggplot','Shiny'
                    ,'H2o','PowerBI','Qlikview','Django','Dplyr'
                    ,'Elasticsearch','Qliksense','Cognos','Spotfire']

df_bibliotecas = df_grouped[df_grouped.Lenguages_all.isin(filter_Libraries)].rename(columns = {"Lenguages_all": "Libraries_all"})

# Contamos la cantidad de palabras
df_Libraries_grouped = pd.DataFrame(df_bibliotecas.groupby('Libraries_all')['count'].sum()).reset_index()

# Calculamos el % que aparece cada palabra dentro del total de bibliotecas
df_Libraries_grouped['total'] = df_Libraries_grouped['count'].sum(axis = 0)
df_Libraries_grouped['percentage'] = round((df_Libraries_grouped['count']/df_Libraries_grouped['total'])*100,2)

# Nos quedamos con los que tienen una participación mayor al 4%
df_Libraries_grouped['Libraries'] = np.where(df_Libraries_grouped.percentage<4.0, 'Others', df_Libraries_grouped.Libraries_all)
df_Libraries_grouped = pd.DataFrame(df_Libraries_grouped.groupby('Libraries')['percentage'].sum()).reset_index().sort_values(by = 'percentage', ascending = False)

# Ahora realizamos dos gráfico tipo torta

fig = plt.figure(1, figsize = (15,10))
the_grid = GridSpec(2, 2)

# Gráfico para Programming Lenguages
ax = plt.subplot(the_grid[0, 0], aspect = 1, title = 'Programming Lenguages')

data = df_lenguages_grouped.percentage
ingredients = df_lenguages_grouped.Lenguages

def func(pct, allvals):
    absolute = int(pct/100.*np.sum(allvals))
    return "{:.1f}%".format(pct, absolute)

wedges, texts, autotexts = ax.pie(data, autopct = lambda pct:func(pct, data),
                                    textprops = dict(color = "w"))

ax.legend(wedges, ingredients,
        loc = "center left",
        bbox_to_anchor = (1, 0, 0.5, 1),
        fontsize = 13)

plt.setp(autotexts, size = 12, weight = "bold")

# Gráfico para las Libraries
ax = plt.subplot(the_grid[0, 1], aspect = 1, title = 'Libraries')

data = df_Libraries_grouped.percentage
ingredients = df_Libraries_grouped.Libraries

def func(pct, allvals):
    absolute = int(pct/100.*np.sum(allvals))
    return "{:.1f}%".format(pct, absolute)

wedges, texts, autotexts = ax.pie(data, autopct = lambda pct: func(pct, data),
                                    textprops = dict(color = "w"))

ax.legend(wedges, ingredients,
            loc = "center left",
            bbox_to_anchor = (1, 0, 0.5, 1),
            fontsize = 13)

plt.setp(autotexts, size = 12, weight = "bold")

plt.suptitle("% Programming Skills Required for Data Scientist Jobs", fontsize = 16, fontweight = 'bold')

plt.show()