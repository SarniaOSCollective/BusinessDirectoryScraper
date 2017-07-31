import scrapy
from scrapy import Request
from bs4 import BeautifulSoup


# Add location so that it doesn't cause an IndexError
# e.g http://www.sarnialambton.on.ca/business/cranberrys-catering
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
        city = ""
        province = ""
        website = ""
        facebook = ""
        twitter = ""
        linkedin = ""
        year = ""
        key_contact = ""
        naics = ""
        employees = ""
        tags = ""

        # Parse the locations area of the page
        locations = response.css('address::text').extract()
        # Takes the City and Province and removes unicode and removes whitespace,
        # they are still together though.
        city_province = locations[1].replace(u'\xa0', u' ').strip()
        # List of all social links that the business has
        social = response.css('.entry-content > div:nth-child(2) a::attr(href)').extract()
        add_info = response.css('ul.list-border li').extract()

        # try and except's for city, province and tags to avoid IndexErrors
        try:
            city = city_province.split(',', 1)[0]
        except:
            pass

        try:
            province = city_province.split(',', 1)[1].strip()
        except:
            pass

        try:
            tags = response.css('ul.biz-tags li a::text').extract()
        except:
            pass

        for link in social:
            soup = BeautifulSoup(link)
            if 'facebook' in link:
                text = soup.get_text()
                facebook = text
            elif 'twitter' in link:
                text = soup.get_text()
                twitter = text
            elif 'linkedin' in link:
                text = soup.get_text()
                linkedin = text
            else:
                pass

        for info in add_info:
            soup = BeautifulSoup(info)
            if 'Year' in info:
                # If the row has "Year" extract using BeautifulSoup and get the last 4
                text = soup.get_text()
                year = text[-4:]
            elif 'Key' in info:
                text = soup.get_text()
                key_contact = text.replace('Key Contact: ', '')
            elif 'NAICS' in info:
                text = soup.get_text()
                naics = text.replace('NAICS Code: ', '')
            elif 'F/T' in info:
                text = soup.get_text()
                employees = text.replace('F/T Employees: ', '')
            else:
                pass

        yield {
            'title': response.css('h1.entry-title::text').extract_first().strip(),
            'description': response.css('p.mb-double::text').extract_first(),
            'phone_number': response.css('div.mb-double ul li::text').extract_first(default="").strip(),
            'email': response.css('div.mb-double ul li a::text').extract_first(default=""),
            'address': locations[0].strip(),
            'city': city,
            'province': province,
            'zip_code': locations[2].strip(),
            'website': website,
            'facebook': facebook,
            'twitter': twitter,
            'linkedin': linkedin,
            'year': year,
            'employees': employees,
            'key_contact': key_contact,
            'naics': naics,
            'tags': tags,
        }
