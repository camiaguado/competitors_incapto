from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
from utils import filter_json_scraper
import os
import json
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Obtener el timestamp actual para los nombres de archivos
def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

@app.get("/")
def read_root():
    return {"Hola": "Incapto api"}

# Endpoint 1: Procesar el scraping completo
@app.get("/scrape/{site}")
def scrape(site: str):
    timestamp = get_timestamp()
    output_file = f"{site}_output_{timestamp}.json"
    print('hola entra aqui MAIN')
    print('HIZO FETCHHHH')

    try:
        # Ejecuta el spider de Scrapy con el sitio seleccionado
        result = subprocess.run(
            ["scrapy", "crawl", "competitor", "-a", f"target_site={site}", "-o", output_file],
            capture_output=True, text=True, check=True
        )
        print("Scrapy execution output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error executing Scrapy:", e.stderr)
        return {"status": "Error", "details": e.stderr}

    # Verifica si el comando fue exitoso y el archivo fue creado correctamente
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        try:
            clean_file = filter_json_scraper(output_file, timestamp)  # Pasar el timestamp

            # Leer el contenido del archivo limpio (clean_file)
            with open(clean_file, 'r') as f:
                cleaned_data = json.load(f)

            # Devolver los datos como respuesta
            return {"status": "Success", "data": cleaned_data}
            
        except ValueError as e:
            return {"status": "Error", "details": str(e)}
    else:
        return {"status": "Error", "details": f"Output file {output_file} is empty or does not exist."}


# Endpoint 2: Obtener los datos limpios directamente del archivo sin ejecutar scraping
@app.get("/data/{site}")
def get_clean_data(site: str):
    # Busca todos los archivos que coincidan con el patrón "{site}_output_clean"
    matching_files = sorted(
        [f for f in os.listdir() if f.startswith(f"{site}_output_clean")],
        key=lambda x: os.path.getmtime(x),  # Ordenar por fecha de modificación
        reverse=True  # Archivos más recientes primero
    )

    # Verifica si hay algún archivo que coincida
    if not matching_files:
        return {"status": "Error", "details": f"No se encontraron archivos para el sitio {site}"}

    # Selecciona el archivo más reciente
    clean_file = matching_files[0]
    
    # Verifica si el archivo limpio existe y tiene contenido
    if os.path.exists(clean_file) and os.path.getsize(clean_file) > 0:
        try:
            # Leer el contenido del archivo limpio
            with open(clean_file, 'r') as f:
                cleaned_data = json.load(f)

            # Devolver los datos como respuesta
            return {"status": "Success", "data": cleaned_data}
        except ValueError as e:
            return {"status": "Error", "details": f"Error al leer el archivo: {str(e)}"}
    else:
        return {"status": "Error", "details": f"Output clean file {clean_file} is empty or does not exist."}
