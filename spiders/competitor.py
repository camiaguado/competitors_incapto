import scrapy
from .scrapers.syra_scraper import parse_syra_product
from .scrapers.cafedefinca_scraper import parse_cafedefinca
from .scrapers.elmagnifico_scraper import parse_elmagnifico
from .scrapers.incapto_scraper import parse_incapto


class CompetitorSpider(scrapy.Spider):
    
    print('hola entra aqui CompetitorSpider')

    
    name = "competitor"
    
    def __init__(self, *args, **kwargs):
        super(CompetitorSpider, self).__init__(*args, **kwargs)
        self.target_site = kwargs.get('target_site', 'syra')  # Por defecto Syra

    def start_requests(self):
        # URLs por sitio
        urls = {
            'syra': 'https://syra.coffee/collections/coffee',
            'cafedefinca': 'https://cafedefinca.eu/categoria-producto/cafe/',
            'elmagnifico': 'https://cafeselmagnifico.com/categoria-producto/cafe/?_per_page=40',
            'incapto': 'https://incapto.com/cafe-de-origen/'
        }

        # Verificar si la URL está disponible
        url = urls.get(self.target_site)
        if not url:
            raise ValueError('Sitio no reconocido')

        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if self.target_site == 'syra':
            yield from parse_syra_product(response)
        elif self.target_site == 'cafedefinca':
            yield from parse_cafedefinca(response)
        elif self.target_site == 'elmagnifico':
            yield from parse_elmagnifico(response)
        elif self.target_site == 'incapto':
            yield from parse_incapto(response)
