import scrapy
import json
import requests


class TrendyolSpider(scrapy.Spider):
    name = 'trendyol'
    allowed_domains = ['trendyol.com']
    start_urls = ['https://www.trendyol.com/supermarket-x-c103799?pi=1']
    products = []
    custom_settings = {
        "DOWNLOAD_DELAY": 1
    }

    def parse(self, response):
        url = "https://public.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/supermarket-x-c103799?pi=2&culture=tr-TR&userGenderId=2&pId=0&scoringAlgorithmId=2&categoryRelevancyEnabled=false&isLegalRequirementConfirmed=false&searchStrategyType=DEFAULT&productStampType=TypeA&fixSlotProductAdsIncluded=true&searchAbDeciderValues=Suggestion_A%2CRelevancy_3%2CFilterRelevancy_1%2CListingScoringAlgorithmId_1%2CSmartlisting_2%2CFlashSales_1%2CStoreAds_2&offset=18"
        headers = {
            'Cookie': '__cfruid=2728dac9d28a585bf5a6189f2fbed691119ccc74-1673357920; _cfuvid=mwqvf4Msahgaz1FoPCEnVy6yQRy31Zev4BlCqix.nzk-1673357920723-0-604800000; __cflb=02DiuFo6dq2oaeSzjVDtZq29bSZMcYKtw2xvAG6cgCwCg'
        }
        data = requests.request("GET", url, headers=headers)
        totalCount = data.json()['result']['totalCount']
        pageCount = round(totalCount/24)

        for page in range(1, pageCount, 1):
            urlPage = f"https://www.trendyol.com/supermarket-x-c103799?pi={page}"
            yield scrapy.Request(url=urlPage, callback=self.parse)

            products = response.xpath(
                '//div[@class="p-card-chldrn-cntnr card-border"]/a/@href').getall()

        for item in products:
            yield scrapy.Request(url="https://www.trendyol.com" + item, callback=self.parseItems)

        if page == pageCount-1:
            jsonString = json.dumps(self.products, ensure_ascii=False)
            jsonFile = open("data.json", "w", encoding='utf8')
            jsonFile.write(jsonString)
            jsonFile.close()

    def parseItems(self, response):
        data = {
            "url": response.url,
            "id": response.url.split("-")[-1],
            "title": response.xpath('//h1[@class="pr-new-br"]/span/text()').get(),
            "price": response.xpath('//span[@class="prc-dsc"]/text()').get(),
            "image": response.xpath('//meta[@name="twitter:image:src"]/@content').get(),
        }
        self.products.append(data)
