"""
OBJETIVO: Extraer la descripcion de cargo de los puestos de Data Scientist en USA publicados en la pagina web de emples Indeed.
ELABORADO POR: Diego Rojas
FECHA DE ELABORACIÓN: Julio 2020
"""
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from time import sleep
from pymongo import MongoClient

#Creamos una colección en Mongodb donde vamos a guardar los datos de los libros
client = MongoClient('localhost')
db = client['indeed']
col = db['data_scientist_jobs']
    
# Definimos el User Agent
opts = Options()
opts.add_argument("user-agent = Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36")

url_todas = ['https://www.indeed.com/jobs?q = data+scientist&l = United+States&fromage = last']
for i in range (10, 310, 10):
    url = 'https://www.indeed.com/jobs?q = data+scientist&l = United+States&fromage = last&start = ' + str(i)
    url_todas.append(url)

#Antes de continuar, creamos una función que elimine la tabulación y saltos de linea
def limpieza(texto):
    texto_corregido = (
        texto.replace('\n', ' ').replace('\t', ' ').replace(',',' ')
        .replace('.',' ').replace('(',' ').replace(')',' ').replace(':',' ')
        .replace('/',' ').replace(';',' ')
        )
    return texto_corregido

# Ejecutar el proceso hasta que llegue a la ultima url
PAGINA = 1

#Recorremos cada uno de los urls
for url in url_todas:
    
    driver = webdriver.Chrome(executable_path = r"C:\Users\dar12\Downloads\Web Scraping\chromedriver.exe", chrome_options = opts)
    driver.get(url)

    # Mientras la PAGINA en la que me encuentre, sea menor que la maxima PAGINA que voy a sacar... sigo ejecutando...
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[@class = "jobsearch-SerpJobCard unifiedRow row result clickcard"]//h2//a[@target = "_blank"]')))

    links_productos = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[@class = "jobsearch-SerpJobCard unifiedRow row result clickcard"]//h2//a[@target = "_blank"]')))

    links_de_la_PAGINA = []
    id = 1
    for a_link in links_productos:
        links_de_la_PAGINA.append(a_link.get_attribute("href"))
    print('PAGINA ',str(PAGINA),' iniciada') 

    for link in links_de_la_PAGINA:

        try:
        # Voy a cada uno de los links de los detalles de los productos
            driver.get(link)

            try:
                title = driver.find_element(By.XPATH, '//div[@class = "jobsearch-JobInfoHeader-title-container"]//h3').text
                title = limpieza(title)
            except:
                title = 'N.D'
            try:
                item1 = driver.find_element(By.XPATH, '//div[@id = "jobDescriptionText"]//ul[1]').text
                item1 = limpieza(item1)
            except:
                item1 = 'N.D' 
            try:
                item2 = driver.find_element(By.XPATH, '//div[@id = "jobDescriptionText"]//ul[2]').text
                item2 = limpieza(item2)
            except:
                item2 = 'N.D'
            try:
                item3 = driver.find_element(By.XPATH, '//div[@id = "jobDescriptionText"]//ul[3]').text
                item3 = limpieza(item3)
            except:
                item3 = 'N.D'             

            #Agregamos una variable con la fecha en que estamos haciendo la extracción
            fecha_subida = str(date.today())
        
            #Inserto los datos en la colección de Mongodb
            col.insert_one({
                'title': title,
                'item1': item1,
                'item2': item2,
                'item3': item3,
                'fecha_subida':fecha_subida
            })
            id+ = 1
            
            # Piso el boton de retroceso
            driver.back()
        
        except Exception as e:
            print (e)
            # Si sucede algún error regreso y sigo con el siguiente job.
            driver.back()

    print('PAGINA ',str(PAGINA),' finalizada')    
    PAGINA+ = 1
    print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
    driver.close()
 