import json
from ...utils import format_price
def parse_cafedefinca(response):
    products = response.xpath('//*[@class="products columns-3"]/li')
    
    if not products:
        print("No se encontraron productos")
        return
    
    for product in products:
        product_name = product.xpath('.//h2[@class="woocommerce-loop-product__title"]/text()').get().strip()
        product_origin = product.xpath('.//div[@class="pais"]/text()').get().strip()
        product_url = product.css('a::attr(href)').get()
        full_product_url = response.urljoin(product_url)
        
        # Hacer una nueva solicitud para cada URL de producto y extraer los detalles (grano y pesos)
        yield response.follow(full_product_url, callback=parse_cafedefinca_product, meta={'product_name': product_name, 'product_origin': product_origin, 'product_url': full_product_url})


def parse_cafedefinca_product(response):
    product_name = response.meta['product_name']
    product_origin = response.meta['product_origin']
    product_url = response.meta['product_url']
    
    # Inicializar los precios a None por defecto
    price_250 = None
    price_1_kilo = None
    
    # Extraer las variaciones del producto
    variations = response.xpath('//form[@class="variations_form cart"]/@data-product_variations').get()
    if variations:
        variations_data = json.loads(variations)
        for variation in variations_data:
            weight = variation['attributes'].get('attribute_pa_peso')
            grano = variation['attributes'].get('attribute_pa_grano-molido')

            if grano == 'grano':  # Solo tomamos la opción "GRANO"
                if weight == '250gr':
                    price_250 = variation['display_price']
                elif weight == '1kg':
                    price_1_kilo = variation['display_price']


    # Solo generar el objeto si al menos uno de los precios no es None
    if price_250 or price_1_kilo:
        product_data = {
            'competitor': "Café de finca",
            'product_name': product_name,
            'product_origin': product_origin,
            'price_250': format_price(price_250) if price_250 else None,
            'price_500': None,  # No se extrae en este sitio
            'price_1_kilo': format_price(price_1_kilo) if price_1_kilo else None,
            'product_url': product_url
        }

        # Devolver la información del producto para que Scrapy lo capture
        yield product_data
