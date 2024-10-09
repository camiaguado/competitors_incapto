import scrapy

def parse_syra_product(response):
    products = response.css('ul#product-grid li.grid__item')
    
    # Verifica que has encontrado productos en la página
    if not products:
        print("No se encontraron productos")
        return
    
    for product in products:
        product_name = product.css('h3.card__heading a::text').get().strip()
        price_250 = product.xpath('.//span[@class="price-low-v2"]/span[@class="money"]/text()').get()
        price_1_kilo = product.xpath('.//span[@class="price-high-v2"]/span[@class="money"]/text()').get()
        product_origin = product.xpath('.//div[@class="product-origin"]/text()').get().strip()

        product_url = product.css('a::attr(href)').get()  # Extraer el enlace del producto
        full_product_url = response.urljoin(product_url)  # Convertir el enlace relativo en absoluto

        # Primero yield los datos básicos del producto
        yield {
            'competitor': "Syra Coffee",
            'product_name': product_name,
            'product_origin': product_origin,
            'price_250': str(price_250) if price_250 else None,
            'price_500': None,
            'price_1_kilo': str(price_1_kilo) if price_250 else None,
            'product_url': full_product_url
        }

        # Luego hacer la solicitud de la página individual del producto
#         yield scrapy.Request(url=full_product_url, callback=parse_syra_product_page, meta={
#             'product_name': product_name,
#             'product_origin': product_origin,
#             'price_250': price_250,
#             'price_1_kilo': price_1_kilo
#         })

# # def parse_syra_product_page(response):
# #     # Obtener datos pasados
# #     product_name = response.meta['product_name']
# #     product_origin = response.meta['product_origin']
# #     price_low = response.meta['price_low']
# #     price_high = response.meta.get('price_high')

# #     # Seleccionar molienda "Café en grano" y tamaño "250GR"
# #     grind_option = response.xpath('//select[@name="properties[Ground]"]/option[contains(text(), "Café en grano")]/text()').get()
# #     size_option = response.xpath('//select[@name="options[Peso]"]/option[contains(text(), "250GR.")]/@value').get()
# #     price = response.xpath('//select[@class="select_select hidden"]/option[contains(@varid, "250GR.")]/@varprice').get()

# #     # Almacenar los datos si se encontraron las opciones y precio
# #     if grind_option and size_option and price:
# #         yield {
# #             'product_name': product_name,
# #             'product_origin': product_origin,
# #             'price_low': price_low,
# #             'price_high': price_high,
# #             'grind_option': grind_option.strip(),
# #             'size_option': size_option.strip(),
# #             'price_250g': price.strip()
# #         }
