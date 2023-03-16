from genericpath import exists
import requests
import json
from pathlib import Path
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import os
from .pdfparse import parse_file
import traceback
 
 
def download_pdf(driver,url,path, timeout=20):
    if "azores.gov.pt" in url: 
        id_contrato_azores = url.split("/")[-1]
        url = 'https://jo.azores.gov.pt/api/public/ato/{}/pdfOriginal'.format(id_contrato_azores)
        print(url)
 
    o=len(list(path.glob("*.pdf")))
    driver.get(url)
    end_time = time.time() + timeout
    while o==len(list(path.glob("*.pdf"))):
        time.sleep(0.25)
        print("waiting...")
        if time.time() > end_time:
            print("File not found within time")
            return False
 
    if o<len(list(path.glob("*.pdf"))):
        return sorted(path.iterdir(), key=os.path.getmtime)[-1]
  
def ScrapeBase(pdf_folder):
 
    PAGES_TO_CRAWL = 1 # Numero de paginas a obter
    
    API_url = 'https://www.base.gov.pt/Base4/pt/resultados/'
    
    query = {
        'type': 'search_contratos',
        'query': 'tipo=2&tipocontrato=5&desdedatafecho=2022-01-01&atedatafecho=2022-01-31&pais=187&distrito=0&concelho=0',
        'sort': '-publicationDate',
        'size': 25
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
        "Accept-Encoding": "*",
        "Connection": "keep-alive",
        "Accept": "application/json"
    }
    
    # Obter lista de contratos
    contratos = []
    for page in range(PAGES_TO_CRAWL):
        query['page'] = page
        request = requests.post(API_url, data=query) # fazer pedido POST
        data = request.json() # descodificar resposta
        contratos.extend(data['items']) # adicionar detalhes extra
        
    
    detalhe_contrato_url = 'https://www.base.gov.pt/Base4/pt/detalhe/?type=contratos&id='
    
    detalhe_anuncio_url = 'https://www.base.gov.pt/Base4/pt/detalhe/?type=anuncios&id={}'
    
    anuncio_path_base = Path(pdf_folder)
    
    
    details_query = {
        'type': "detail_contratos"
    }
    
    
    options = Options()
    options.add_experimental_option('prefs', {
        "download.default_directory": str(anuncio_path_base),#Change default directory for downloads
        #"download.prompt_for_download": False, #To auto download the file
        #"download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome 
        })
    driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
    
    # Obter detalhes de cada contrato
    for contrato in contratos:
        details_query["id"] = contrato["id"]
        request = requests.post(API_url, data=details_query) #fazer pedido post para detalhes
        print(request.text)
        data = request.json() #descodificar a resposta
        contrato["extra_details"] = data #adicionar detalhes extra
 
        try:     
            anuncio_id=data["announcementId"]
        
            BASE_URL = 'https://www.base.gov.pt/Base4/pt/resultados/'
            query = {
                'type': 'detail_anuncios',
                'id': anuncio_id
            }
            
            response = requests.post(BASE_URL, data=query, headers=headers, timeout=20)
            
            time.sleep(0.25)
            print(detalhe_anuncio_url.format(anuncio_id))
            try:
                data = response.json()
 
                anuncio_url = data["reference"]
    
                fn = download_pdf(driver,anuncio_url,anuncio_path_base)
                if fn:
                    data["path_anuncio"] = str(fn)
                    data["pdf_anuncio"] = parse_file(str(fn))
                    with open('base_gov_data.json', 'w') as f:
                        json.dump(contratos, f)
                
                else:
                    print("PDF não encontrado!")
 
            
                contrato["anuncio_details"] = data
            except:
                print("PDF não encontrado!")
                print(detalhe_anuncio_url.format(anuncio_id))
                print(traceback.format_exc())
        except:
            print("handled successfully")
            print(traceback.format_exc())
    
    driver.close()
    print(f'Total de contratos: {len(contratos)}')
    with open('base_gov_data_2015.json', 'w') as f:
        json.dump(contratos, f)
