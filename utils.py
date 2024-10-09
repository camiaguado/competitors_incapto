import json
def format_price(price):
    """Función para formatear los precios en el formato XX,XX€"""
    if price is not None:
        return f"{price:.2f}".replace('.', ',') + "€"
    return None


def filter_json_scraper(json_file, timestamp):
    # Cargar los datos del archivo JSON
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise ValueError(f"Error al procesar el archivo {json_file}. Formato JSON inválido.")

    if not data:
        raise ValueError(f"No se encontraron datos válidos en el archivo {json_file}.")

    # Definir los orígenes permitidos
    allowed_origins = ["El Salvador", "Guatemala", "Etiopia", "Etiopía", "Ethiopia", "Brasil", "Colombia", "Perú", "Burundi", "Sumatra", "México", "Rwanda", "Uganda"]

    # Filtrar los productos
    filtered_data = []
    for product in data:
        product_name = product.get("product_name", "").lower()
        product_origin = product.get("product_origin", "")

        # Normalizar el nombre "Etiopia", "Ethiopia", etc. a "Etiopía"
        if product_origin.lower() in ["ethiopia", "etiopia"]:
            product_origin = "Etiopía"

        # Comprobar que el nombre no contenga "blend" y que el origen esté en la lista de permitidos
        if "blend" not in product_name and product_origin in allowed_origins:
            product["product_origin"] = product_origin  # Actualizar el origen normalizado
            filtered_data.append(product)

    # Guardar el archivo JSON limpio con timestamp
    clean_file = json_file.replace("_output", f"_output_clean_{timestamp}")
    with open(clean_file, "w") as f:
        json.dump(filtered_data, f, indent=4)

    return clean_file
