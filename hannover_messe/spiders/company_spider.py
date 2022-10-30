import scrapy

class CompanySpider(scrapy.Spider):
    name = "companies"
    base_url = "https://www.hannovermesse.de"

    def start_requests(self):
        letter_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
                       'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
                       'y', 'z', 'numbers', 'others']
        # letter_list = ['a']
        urls = [self.base_url
                + '/en/expo/exhibitor-short-index/index-2?letter='
                + letter for letter in letter_list]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        company_detail_links = response.css("o-exhibitor-snippet::attr(href)")
        yield from response.follow_all(company_detail_links, self.parse_detail)

    def parse_detail(self, response):

        def extract_with_css(query):
            return response.css(query).get(default='')
        
        def extract_with_xpath(query, idx=0):
            if idx <= 0:
                return response.xpath(query).get()
            else:
                return response.xpath(query)[idx].get()

        def extract_with_xpath_search(query, keyword=None):
            results = response.xpath(query).get()
            ret = ''
            if keyword:
                for result in results:
                    res = str(result).lower()
                    if res.startswith(keyword.lower()):
                        ret = res[res.find('+'):]
            return ret

        yield {
            'name': extract_with_xpath('.//c-page-intro/template[@slot="headline"]/h1/text()'),
            'slogan': extract_with_xpath('.//c-page-intro/template[@slot="subline"]/p/text()'),
            'full_name': extract_with_xpath('.//c-navigation-tabs-dynamic/template/c-tabs/template[@slot="content"]/div/div/div/div/h2/text()'),
            'description': extract_with_xpath('.//c-detail-profil/template[@slot="content"]/div/div/p/text()'),
            'location': extract_with_xpath('.//c-navigation-tabs-dynamic/template/c-tabs/template[@slot="content"]/div/div/div/div/ul/li/text()'),
            'zip_code': extract_with_xpath('.//c-navigation-tabs-dynamic/template/c-tabs/template[@slot="content"]/div/div/div/div/ul/li/text()', idx=1),
            'country': extract_with_xpath('.//c-navigation-tabs-dynamic/template/c-tabs/template[@slot="content"]/div/div/div/div/ul/li/text()', idx=2),
            'phone': extract_with_xpath_search('.//c-navigation-tabs-dynamic/template/c-tabs/template[@slot="content"]/div/div/div/div/ul/li/text()', keyword='phone'),
            'fax': extract_with_xpath_search('.//c-navigation-tabs-dynamic/template/c-tabs/template[@slot="content"]/div/div/div/div/ul/li/text()', keyword='fax'),
            'email': '',
            'website': extract_with_css('o-link::attr(href)'),
            'logo': extract_with_xpath('.//head/meta[@property="og:image"]/@content'),
            'video': extract_with_xpath('.//o-video/@src'),
        }
