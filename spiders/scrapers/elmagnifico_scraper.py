import scrapy
import json
from ...utils import format_price


# Definir los orígenes permitidos
allowed_origins = ["El Salvador", "Guatemala", "Etiopía", "Brasil", "Colombia", "Perú", "Burundi", "Sumatra", "México", "Rwanda", "Uganda"]

def parse_elmagnifico(response):
    # Capturar todos los productos en la lista de productos
    products = response.css('ul.products li.product')
    
    # Verifica si se encontraron productos
    if not products:
        print("No se encontraron productos en la página de listado.")
        return
    else:
        print(f"Se encontraron {len(products)} productos en la página de listado.")

    for idx, product in enumerate(products, 1):
        product_name = product.css('h2.woocommerce-loop-product__title::text').get().strip()

        # Filtrar por los orígenes permitidos
        if any(origin.lower() in product_name.lower() for origin in allowed_origins):
            product_url = product.css('a.woocommerce-LoopProduct-link::attr(href)').get()
            full_product_url = response.urljoin(product_url)

            # Mostrar por consola que estamos enviando la solicitud para este producto
            print(f"Producto #{idx}: {product_name} | URL: {full_product_url}")
            
            # Realiza una nueva solicitud a la URL del producto para obtener los detalles
            yield scrapy.Request(url=full_product_url, callback=parse_product_details, meta={'product_name': product_name, 'product_url': full_product_url})
        else:
            print(f"Producto #{idx} ({product_name}) no tiene un origen permitido y será omitido.")

def parse_product_details(response):
    # Obtener el nombre del producto y la URL desde los meta datos
    product_name = response.meta['product_name']
    product_url = response.meta['product_url']
    
    print(f"Procesando detalles del producto: {product_name} | URL: {product_url}")
    
    # Obtener las variaciones del producto en la página
    variations = response.css('form.variations_form').xpath('@data-product_variations').get()

    if not variations:
        print(f"No se encontraron variaciones para el producto: {product_name}")
        return

    try:
        # Convertir las variaciones a un diccionario JSON
        variations_data = json.loads(variations.replace('&quot;', '"'))
    except json.JSONDecodeError as e:
        print(f"Error al decodificar variaciones para {product_name}: {e}")
        return

    # Inicializar las variables de precio
    price_250 = price_500 = price_1_kilo = None

    # Iterar sobre las variaciones de cantidades y capturar los precios
    for variation in variations_data:
        cantidad = variation['attributes'].get('attribute_pa_cantidad')
        price = variation['display_price']

        if cantidad == '250-gr':
            price_250 = price
        elif cantidad == '500-gr':
            price_500 = price
        elif cantidad == '1-kg':
            price_1_kilo = price

    # Asumimos que el origen está en el nombre del producto
    product_origin = next((origin for origin in allowed_origins if origin.lower() in product_name.lower()), None)

    # Mostrar los detalles obtenidos por consola
    print(f"Producto: {product_name} | Origen: {product_origin} | Precio 250g: {price_250} | Precio 500g: {price_500} | Precio 1kg: {price_1_kilo}")

    # Si se ha obtenido algún dato válido, devolvemos el producto
    if product_origin:
        yield {
            'competitor': 'El magnífico',
            'product_name': product_name,
            'product_origin': product_origin,
            'price_250': format_price(price_250) if price_250 else None,
            'price_500': format_price(price_500) if price_250 else None,
            'price_1_kilo': format_price(price_1_kilo) if price_250 else None,
            'product_url': product_url
        }
    else:
        print(f"No se encontró un origen válido para el producto: {product_name}")
