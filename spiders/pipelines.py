from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

# drop the item if there isn't a valid model year
class YearPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('model_years'):
            return(item)
        else:
            raise DropItem()
            
# fix dashes and drop if there isn't a valid model
# also drops the edge case "Full-size Ford," which refers to a range of trucks already accounted for by other pages
class ModelPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        adapter['model'] = adapter['model'].replace('\u2013', '-')
        if adapter.get('model') and adapter.get('model') != "Full-size":
            return(item)
        else:
            raise DropItem()

# drop if the make is just numbers: edge case where the entries were made incorrectly in Wikipedia (see 1952 Ford)
class MakePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if not adapter.get('make').isnumeric(): #make sure there is a model and it isn't just numbers (some pages have the year as make)
            return(item)
        else:
            raise DropItem()