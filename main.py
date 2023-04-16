import scrapy
from scrapy.crawler import CrawlerProcess
from itemadapter import ItemAdapter
import json


class QuoteItem(scrapy.Item):
    tags = scrapy.Field()
    author = scrapy.Field()
    quote = scrapy.Field()


class AuthorItem(scrapy.Item):
    fullname = scrapy.Field()
    born_date = scrapy.Field()
    born_location = scrapy.Field()
    description = scrapy.Field()


class MainPipline:
    quotes = []
    authors = []

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if "fullname" in adapter.keys():
            self.authors.append(adapter.asdict())
        if "quote" in adapter.keys():
            self.quotes.append(adapter.asdict())
        return item

    def close_spider(self, spider):
        with open("quotes.json", "w", encoding="utf-8") as fd:
            json.dump(self.quotes, fd, ensure_ascii=False)
        with open("authors.json", "w", encoding="utf-8") as fd:
            json.dump(self.authors, fd, ensure_ascii=False)


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com/"]
    custom_settings = {"ITEM_PIPELINES": {MainPipline: 100}}

    def parse(self, response, *args):
        for quote in response.css("div.quote"):
            item = QuoteItem()
            item["tags"] = quote.css("div.tags a.tag::text").extract()
            item["author"] = quote.css("span small::text").extract_first()
            item["quote"] = quote.css("span.text::text").extract_first()
            yield item

            author_url = quote.css("span > a::attr(href)").extract_first()
            yield response.follow(author_url, self.parse_author)

        next_page = response.css("li.next a::attr(href)").extract_first()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_author(self, response):
        item = AuthorItem()
        item["fullname"] = response.css("h3.author-title::text").extract_first()
        item["born_date"] = response.css("span.author-born-date::text").extract_first()
        item["born_location"] = response.css(
            "span.author-born-location::text"
        ).extract_first()
        item["description"] = response.css(
            "div.author-description::text"
        ).extract_first()
        yield item


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.start()
    print("THE END")
