# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from infoseeker.items import InfoseekerItem as InfoItem
from scrapy.http import Request


class SeekerSpider(CrawlSpider):
    name = 'seeker'
    allowed_domains = ['info.mzalendo.com']
    start_urls = ['http://info.mzalendo.com/position/member-national-assembly/?page=1']
    main_url = 'http://info.mzalendo.com/position/member-national-assembly/'
    domain = 'http://info.mzalendo.com'
    urls = []
    retrieving = False

    def parse_page(self, response):
        #default values
        result = {'name' : None}

        find_name = response.css('.object-titles h1::text').extract()
        if find_name:
            result['name'] = find_name[0]

        extract_first_headers = response.css('.constituency-party h3::text').extract()
        extract_first_info = response.css('.constituency-party li > a::text').extract()

        extract_second_headers = response.css('.contact-details h3::text').extract()
        extract_second_info = response.css('.contact-details p').extract()

        for key, value in zip(extract_first_headers, extract_first_info):
            result[key] = value

        for key, value in zip(extract_second_headers, extract_second_info):
            result[key] = value

        yield result


    def parse(self, response):
        if not self.retrieving:
            selector_list = response.css('.position')

            for selector in selector_list:
                self.urls.append(selector.css('a::attr(href)').extract()[0])

            found = response.css('.next::attr(href)').extract()
            if found:
                next_page = self.main_url + found[0] #uses ?page=2, ?page=3 format so appended to main url to avoid issues
            else:
                next_page = None

            if next_page is not None:
                yield response.follow(next_page, self.parse)
            else:
                self.retrieving = True

        #should run once all urls have been found
        for url in self.urls:
            yield Request(self.domain + url, callback=self.parse_page)

