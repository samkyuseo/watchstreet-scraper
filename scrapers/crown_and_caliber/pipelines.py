# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import datetime
from pathlib import Path
from datetime import datetime
from scrapy.exporters import JsonItemExporter


class CrownAndCaliberPipeline(object):

    path = (
        Path(os.getcwd())
        / "data"
        / f"data-{datetime.today().strftime('%Y-%m-%d')}.json"
    )

    def open_spider(self, spider):
        self.file = open(self.path, "wb")
        self.exporter = JsonItemExporter(self.file)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
