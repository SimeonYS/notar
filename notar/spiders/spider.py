import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import NotarItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class NotarSpider(scrapy.Spider):
	name = 'notar'
	start_urls = ['https://www.notar.at/informationen/aktuelle-infos-veranstaltungen/seite-1/']

	def parse(self, response):
		articles = response.xpath('//div[@class="article articletype-0"]')
		for article in articles:
			date = article.xpath('.//time[@itemprop="datePublished"]/@datetime').get()
			post_links = article.xpath('.//a[@class="news-list__more"]/@href').get()
			yield response.follow(post_links, self.parse_post,cb_kwargs=dict(date=date))

		next_page = response.xpath('//li[@class="news-list__pagination__item news-list__pagination__item--next"]/a[@class="news-list__pagination__link"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h2/text()').get()
		content = response.xpath('//div[@class="news-single__text"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=NotarItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
