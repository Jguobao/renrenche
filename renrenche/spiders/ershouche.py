# -*- coding: utf-8 -*-
import scrapy
import re
import json

class ErshoucheSpider(scrapy.Spider):
    name = 'ershouche'
    allowed_domains = ['renrenche.com']
    start_urls = ['https://www.renrenche.com/qd/ershouche/p1/']

    def parse(self, response):
        print("=" * 100)
        print(response.request.url)
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

        next_url =  response.xpath("//a[@rrc-event-name='switchright']/@href").get()
        if next_url != "javascript:void(0);":
            next_url = response.urljoin(next_url)
            yield scrapy.Request(next_url,callback=self.parse,)

    def parse_car(self,response):
        index = response.meta["info"]

        car_url = response.request.url
        title = "".join(response.xpath("//div[@class='title']/h1/text()").getall()).strip()
        # print(response.request.url,index)
        script_tag = response.xpath("/html/head/script[not(@type)][last()]").get()
        logId = re.findall(r"logId: '(\w+)',?",script_tag)[0]
        car_encrypt_id = re.findall(r"car_encrypt_id: '(\w+)',?",script_tag)[0]
        city_name = re.findall(r"cityName: '(\w+)',?",script_tag)[0]
        # 价格
        price_json_url = "https://www.renrenche.com/lurker/v1/detail/pricemap?plog_id={}&cid={}".format(logId,
                                                                                                        car_encrypt_id)

        anotherpage_json_url = "https://www.renrenche.com/lurker/v1/detail/anotherpage?plog_id={}&cid={}".format(logId,car_encrypt_id)
        # 图片json
        img_json_url = "https://www.renrenche.com/lurker/v1/detail/imagebook?plog_id={}&cid={}".format(logId, car_encrypt_id)
        # 主页
        first_page_json_url = "https://www.renrenche.com/lurker/v1/detail/firstpage?plog_id={}&cid={}&city_name={}".format(logId,car_encrypt_id,city_name)
        #车主评论与检测说明
        lurker_json_url = "https://www.renrenche.com/lurker/v1/detail/anotherpage?plog_id={}".format(logId)
        item = dict(title=title,car_url=car_url,price_json_url=price_json_url,first_page_json_url=first_page_json_url,img_json_url=img_json_url,anotherpage_json_url=anotherpage_json_url)

        yield scrapy.Request(price_json_url,callback=self.parse_price,meta={"item":item})

    def parse_price(self,response):
        item = response.meta.get("item")
        price_json = json.loads(response.body.decode())
        item['price_json'] = price_json
        first_page_json_url = item['first_page_json_url']
        yield scrapy.Request(first_page_json_url, callback=self.parse_first_page, meta={"item": item})
    
    def parse_first_page(self,response):
        item = response.meta["item"]
        parse_first_page = json.loads(response.body.decode())
        item['first_page_json'] = parse_first_page
        anotherpage_json_url = item["anotherpage_json_url"]
        yield scrapy.Request(anotherpage_json_url, callback=self.parse_anotherpage, meta={"item": item})

        #img_json_url = item['img_json_url']
        #yield scrapy.Request(img_json_url, callback=self.parse_img, meta={"item": item})
    #不保存图片
    def parse_img(self,response):
        item = response.meta["item"]
        parse_img_json = json.loads(response.body.decode())
        item['parse_img_json'] = parse_img_json
        anotherpage_json_url = item["anotherpage_json_url"]
        yield scrapy.Request(anotherpage_json_url, callback=self.parse_img, meta={"item": item})

    def parse_anotherpage(self,response):
        item =  response.meta["item"]
        anotherpage_json = json.loads(response.body.decode())
        item['anotherpage_json'] = anotherpage_json
        yield item