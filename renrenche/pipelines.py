# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from scrapy.conf import settings
class RenrenchePipeline(object):
    def __init__(self):
        self.client = MongoClient()
        # renrenche5 未对重复数据处理
        # renrenche6 在spider中对重复数据进行处理
        self.collection = self.client["renrenche6"]["esc"]

    def process_item(self, item, spider):
        title = item["title"]
        car_url = item["car_url"]
        city_name = item["city_name"]
        area = item["area"]
        sold_out_tips=item['sold_out_tips']
        basic_info = item['first_page_json']['data']['content']['basic_info']
        city_id = item['city_id']
        mileage = basic_info['mileage']
        price = basic_info["price"]
        licensed_date = basic_info["licensed_date"]
        format_licensed_diff = basic_info["format_licensed_diff"]
        fuel_type = basic_info["fuel_type"]
        licensed_city = basic_info["licensed_city"]
        transfer_records = basic_info["transfer_records"]
        newcar_price = basic_info["newcar_price"]
        service_price_config = item['first_page_json']['data']['content']['service_price_config']
        speed_box = basic_info['vehicle_config']['变速箱']
        speed_box_type = basic_info['vehicle_config']['变速箱类型']
        service_price = service_price_config["chargeInfo"]["service_price"]
        sellersaid = item['anotherpage_json']['data']['sellersaid']
        surveyor = item['anotherpage_json']['data']['surveyor']
        avatar_content = sellersaid['content']
        owner_name = sellersaid['owner_name']
        inspector_name = surveyor['inspector_data']['inspector_name']
        sum_up_comments= surveyor['inspector_data']['sum_up_comments']


        new_item = {
            'title':title,
            'car_url':car_url,
            'mileage_wan':mileage,
            'city_id':city_id,
            'city_name':city_name,
            'area':area,
            'sold_out_tips':sold_out_tips,
            'price_wan':price,
            'newcar_price': newcar_price,
            'licensed_date':licensed_date,
            'format_licensed_diff':format_licensed_diff,
            'fuel_type':fuel_type,
            'licensed_city':licensed_city,
            'transfer_records':transfer_records,
            '过户数':len(transfer_records),
            'speed_box':speed_box,
            'speed_box_type':speed_box_type,
            'service_price_dollar':service_price,
            'avatar_content':avatar_content,
            'owner_name':owner_name,
            'inspector_name':inspector_name,
            'sum_up_comments':sum_up_comments,
        }

        self.collection.insert(new_item)
        return new_item