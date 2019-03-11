# -*- coding: utf-8 -*-
import scrapy
import re
import json
from copy import deepcopy
import time
class ErshoucheSpider(scrapy.Spider):
    name = 'ershouche'
    allowed_domains = ['renrenche.com']
    # start_urls = ['https://www.renrenche.com/qd/ershouche/p1/']
    start_urls = ['https://www.renrenche.com/']

    def parse(self, response):
        div_list = response.xpath("//div[@class='area-city-letter']/div")
        for divs in div_list:
            area = divs.xpath(".//span/text()").get()
            a_list = divs.xpath(".//a")
            for a in a_list:
                city_url = a.xpath("./@href").get()
                city_url = response.urljoin(city_url)+"ershouche/p1"
                city_id = a.xpath("./@rrc-event-name").get()

                city_name = a.xpath("./text()").get()
                print("#"*100)
                print(city_name)
                print(city_url)
                yield scrapy.Request(city_url,callback=self.parse_detail,meta=deepcopy({'info':[city_id,city_name,area]}))

    #城市页面
    def parse_detail(self, response):
        info = response.meta.get("info")
        print("="*100)
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

            yield scrapy.Request(car_url,callback=self.parse_car,meta=deepcopy({'info':info,'num':0}))

        next_url =  response.xpath("//a[@rrc-event-name='switchright']/@href").get()
        if next_url != "javascript:void(0);":
            next_url = response.urljoin(next_url)
            yield scrapy.Request(next_url,callback=self.parse_detail,meta={'info':info})
    def parse_car(self,response):
        city_id, city_name,area = response.meta["info"]
        num = response.meta["num"]
        info = response.meta["info"]
        car_url = response.request.url
        sold_out_tips = response.xpath("//div[@class='sold-out-tips']/text()").get()
        # title = "".join(response.xpath("//div[@class='title']/h1/text()").getall()).strip()
        title = "".join(response.xpath('//p[@class="title-buy rrcttf6861a996e433db75a6b279b5f99f4b6e"]/text()').getall()).strip()
        if sold_out_tips == "已下架":
            if num<5:
                print("*"*100,"已下架")
                num += 1
                print(num)
                print(response.request.url)
                time.sleep(5)
                yield scrapy.Request(response.request.url, callback=self.parse_detail, meta={'info': info,'num':num},dont_filter=True)
            elif num ==5:
                with open("fail.txt","w+") as f:
                    json.dump({"title":title,"car_url":car_url},f,ensure_ascii=False)
        else:
            # print( title)

            # print(response.request.url,index)
            script_tag = response.xpath("/html/head/script[not(@type)][last()]").get()

            logId = re.findall(r"logId: '(\w+)',?",script_tag)[0]
            car_encrypt_id = re.findall(r"car_encrypt_id: '(\w+)',?",script_tag)[0]
            # city_name = re.findall(r"cityName: '(\w+)',?",script_tag)[0]
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

            item = dict(title=title,car_url=car_url,city_id=city_id,sold_out_tips=sold_out_tips,city_name=city_name,area=area,price_json_url=price_json_url,first_page_json_url=first_page_json_url,img_json_url=img_json_url,anotherpage_json_url=anotherpage_json_url)

            yield scrapy.Request(price_json_url,callback=self.parse_price,meta=deepcopy({"item":item}))

    def parse_price(self,response):
        item = response.meta.get("item")
        price_json = json.loads(response.body.decode())
        item['price_json'] = price_json
        first_page_json_url = item['first_page_json_url']
        yield scrapy.Request(first_page_json_url, callback=self.parse_first_page, meta=deepcopy({"item": item}))
    
    def parse_first_page(self,response):
        item = response.meta["item"]
        parse_first_page = json.loads(response.body.decode())
        item['first_page_json'] = parse_first_page
        anotherpage_json_url = item["anotherpage_json_url"]
        yield scrapy.Request(anotherpage_json_url, callback=self.parse_anotherpage, meta=deepcopy({"item": item}))

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