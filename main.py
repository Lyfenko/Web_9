import scrapy
from scrapy.crawler import CrawlerProcess


class QuoteItem(scrapy.Item):
    tags = scrapy.Field()
    author = scrapy.Field()
    quote = scrapy.Field()


class AuthorItem(scrapy.Item):
    fullname = scrapy.Field()
    date_born = scrapy.Field()
    born_location = scrapy.Field()
    bio = scrapy.Field()


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com/"]

    def parse(self, response):
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
        item["date_born"] = response.css("span.author-born-date::text").extract_first()
        item["born_location"] = response.css(
            "span.author-born-location::text"
        ).extract_first()
        item["bio"] = response.css("div.author-description::text").extract_first()
        yield item


if __name__ == "__main__":
    process = CrawlerProcess(
        settings={
            "FEEDS": {
                "quotes.json": {"format": "json"},
                "authors.json": {"format": "json"},
            }
        }
    )
    process.crawl(QuotesSpider)
    process.start()
