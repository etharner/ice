from lxml.html import parse
import re

class HTMLParser:
    #site = 'http://ice-data.tinro.ru/'
    site = http://192.168.2.33/

    @staticmethod
    def parse_page():
        page = parse(site)
        urls = page.xpath('//a/@href')

        data_urls = {}
        for u in urls:
            if re.match('weekly/(\D*)/data', u):
                sea_name = re.match('weekly/(\D*)/.*', u).group(1)
                if sea_name not in data_urls.keys():
                    data_urls[sea_name] = {'old': HTMLParser.site + u}
                else:
                    data_urls[sea_name]['old'] = HTMLParser.site + u
            elif re.match('daily/(\D*)/data', u):
                sea_name = re.match('daily/(\D*)/.*', u).group(1)
                if sea_name not in data_urls.keys():
                    data_urls[sea_name] = {'new': HTMLParser.site + u}
                else:
                    data_urls[sea_name]['new'] = HTMLParser.site + u

        return data_urls
