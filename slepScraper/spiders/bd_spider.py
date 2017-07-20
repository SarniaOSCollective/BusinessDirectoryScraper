import scrapy
from scrapy import Request


# TODO: Next page doesn't work on page 10. Fix this.
# TODO: Make sure all data is being selected properly (year is not set correctly)

class BDSpider(scrapy.Spider):
    name = "bd"
    start_urls = [
        'http://www.sarnialambton.on.ca/business',
    ]

    def parse(self, response):
        businesses = response.css('div.card-business')

        for business in businesses:
            relative_url = business.css('a::attr(href)').extract_first()
            absolute_url = response.urljoin(relative_url)

            yield Request(absolute_url, callback=self.parse_page, meta={'URL': absolute_url})

        next_page = response.css('a[title="next"]::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            print(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
        else:
            print('no more things to scrape')

    def parse_page(self, response):
        url = response.meta.get('URL')

        # Parse the locations area of the page
        locations = response.css('address::text').extract()
        # Takes the City and Province and removes unicode and removes whitespace,
        # they are still together though.
        city_province = locations[1].replace(u'\xa0', u' ').strip()
        # List of all social links that the business has
        social = response.css('.entry-content > div:nth-child(2) a::attr(href)').extract()

        add_info = response.css('ul.list-border li').extract()

        yield {
            'title': response.css('h1.entry-title::text').extract_first().strip(),
            'description': response.css('p.mb-double::text').extract_first(),
            'phone_number': response.css('div.mb-double ul li::text').extract_first(default="").strip(),
            'email': response.css('div.mb-double ul li a::text').extract_first(default=""),
            'address': locations[0].strip(),
            'city': city_province.split(' ', 1)[0].replace(',', ''),
            'province': city_province.split(' ', 1)[1].replace(',', '').strip(),
            'zip_code': locations[2].strip(),
            'website': response.css('.entry-content > div:nth-child(2) > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)::attr(href)').extract_first(default=''),
            'facebook': response.css('.entry-content > div:nth-child(2) > ul:nth-child(2) > li:nth-child(2) > a:nth-child(1)::attr(href)').extract_first(default=''),
            'twitter': response.css('.entry-content > div:nth-child(2) > ul:nth-child(2) > li:nth-child(3) > a:nth-child(1)::attr(href)').extract_first(default=''),
            'linkedin': response.css('.entry-content > div:nth-child(2) > ul:nth-child(2) > li:nth-child(4) > a:nth-child(1)::attr(href)').extract_first(default=''),
            'year': response.css('.list-border > li:nth-child(1)::text').extract_first(default="").strip(),
            'employees': response.css('.list-border > li:nth-child(2)::text').extract_first(default="").strip(),
            'key_contact': response.css('.list-border > li:nth-child(3)::text').extract_first(default="").strip(),
            'naics': response.css('.list-border > li:nth-child(4)::text').extract_first(default="").strip(),
            'tags': response.css('ul.biz-tags li a::text').extract(),
        }
