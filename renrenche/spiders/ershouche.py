# -*- coding: utf-8 -*-
import scrapy


class ErshoucheSpider(scrapy.Spider):
    name = 'ershouche'
    allowed_domains = ['renrenche.com']
    start_urls = ['https://www.renrenche.com/qd/ershouche/p1/']

    def parse(self, response):
        li_list = response.xpath("//ul[@class='row-fluid list-row js-car-list']/li")

        for index,li in enumerate(li_list):
            style = li.xpath("@style").get()
            tmp = li.xpath("./a[@class='thumbnail']/@href").get()

            if tmp is None or style == "display: none":
                continue
            else:
                car_url=response.urljoin(tmp)
            # print(car_url,index+1)

            yield scrapy.Request(car_url,callback=self.parse_car,meta={"info":(index,)})

    def parse_car(self,response):
        index = response.meta["info"]
        print("="*100)
        print(response.request.url)
        title = "".join(response.xpath("//div[@class='title']/h1/text()").getall()).strip()
        # print(response.request.url,index)
        print(title)
        price = response.xpath("//p[@id='zhimaicar-sale-price']/text()").getall()
        print(price)
        Options = 1
        city = 1
        owner_offer = 1
        org_price = 1
        registered_date = 1
        license_date = 1
        mileage = 1
        standard = 1
        speed_box = 1
        change_user = 1
        img_url = 1