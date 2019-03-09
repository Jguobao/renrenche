# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

class RenrenchePipeline(object):
    def __init__(self):
        self.client = MongoClient()
        self.collection = self.client["renrenche"]["qd3"]

    def process_item(self, item, spider):
        title = item["title"]
        basic_info = item['first_page_json']['data']['content']['basic_info']

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


        new_item = {
            'title':title,
            'mileage':str(mileage)+"万公里",
            'price':str(price)+"万",
            'newcar_price': str(newcar_price) + "万",
            'licensed_date':licensed_date,
            'format_licensed_diff':format_licensed_diff,
            'fuel_type':fuel_type,
            'licensed_city':licensed_city,
            'transfer_records':transfer_records,
            '过户数':len(transfer_records),
            'speed_box':speed_box,
            'speed_box_type':speed_box_type,
            'service_price':str(service_price)+"元",
        }

        self.collection.insert(new_item)
        return new_item