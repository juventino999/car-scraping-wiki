from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor


# This version uses pagination to get all search results. Check the 'unpaginated' branch for a faster implementation that doesn't paginate. 

class Buddy(CrawlSpider):
    name = 'wikipedia.org'
    allowed_domains = ['wikipedia.org']
    start_urls = ["https://en.wikipedia.org/w/index.php?title=Special:Search&limit=500&offset=0&ns0=1&search=deepcat%3A%22Cars+of+the+United+States%22&advancedSearch-current={%22fields%22:{%22deepcategory%22:[%22Cars%20of%20the%20United%20States%22]}}"]
    rules = (
        Rule(LinkExtractor(restrict_css='a[title="Next 500 results"]')), # this allows for pagination: follow all links that have the title "Next 500 results," which should iterate through the different pages of search results
        Rule(LinkExtractor(allow='wiki/', deny=('Main_Page', 'Wikipedia:', 'Portal', 'Special:', 'Help')), callback='parse_page'), # follow all links in search results, but not sidebar links. Once on a page from search results, parse its contents for data
        )
    
    """
    Once on a car's page, get the model years
    # look at all the <tr> tags 
    # if one has a <th> child with an <a> child with the title "Model year", get the td sibling and save it as 'model_years'
    # if no such <th> exists, look for a <th> child with the text 'Production', get the td sibling sibling text and save
    # if neither exist, drop the obs
    # do this in pipeline instead? not sure how to implement
    """
    def parse_get_years(self, response): # take the page
        table_entries = response.css('table')[0].css('tr') # get the first table on the page, then get all <tr> objects from the table
        
        def model_year(entry):
            for c in entry.css('th + td ::text'): # look at the text of each <td> that is next to a <th>
                if ('Model year' in entry.xpath('th/a/@title').extract()): # if the <th> next to it says 'Model year', 
                    return(c) # take the text from <td>
                elif ('Production' in entry.xpath('th/text()').extract()): 
                    return(c)
                
        model_years = [model_year(entry) for entry in table_entries] # iterate thru all the <tr> tags on the page
        
        model_years = model_years[0].extract() # get the text
        model_years = model_years.replace('\u2013', '-') # some dashes were encoded as '\u2013' even when setting 'FEED_EXPORT_ENCODING': 'utf-8',
        model_years = model_years.replace('present', '2024') 
        model_years = model_years.replace('Present', '2024') 
        alphas = 'QWERTYUIOPLKJHGFDSAZXCVBNM qwertyuiopasdfghjklzxcvbnm()'
        model_years = model_years.translate(str.maketrans('', '', alphas)) # remove non-numeric characters from model years
        
        if len(model_years) == 9: # remove single year cars and cars with errors (more than length 9)
           return(model_years) # limitation: cars with non-consecutive production might get the second part of it lopped off (see Ford Taurus)
    
    """Return either the make or the model from the car's page"""
    def parse_get_make_model(self, response, make_or_model):
         make_model = response.css('header h1 span ::text')[0].get() # take the make and model together to be the title of the page
         make_model = make_model.split(' ')
         make = make_model[0]
         model = (' ').join(make_model[1:])
         if make_or_model == 'make':
             return(make)
         elif make_or_model == 'model':
             return(model)
         else:
             raise ValueError
    
    def parse_page(self, response):
        yield{
            'make': self.parse_get_make_model(response, 'make'),
            'model': self.parse_get_make_model(response, 'model'),
            'model_years': self.parse_get_years(response)
            }

process = CrawlerProcess(
    settings={
        "FEEDS": {
            "data/cars.json": {"format": "json"},
        },
        #'FEED_EXPORT_ENCODING': 'utf-8',
        'USER_AGENT': 'University webscraping assignment; n.a.panetta@lse.ac.uk',
        'ITEM_PIPELINES': {"spiders.pipelines.MakePipeline": 300, 
                           "spiders.pipelines.YearPipeline": 500, 
                           "spiders.pipelines.ModelPipeline": 400} # see pipelines.py
    }
)

print('test')
if __name__ == "__main__":
    process.crawl(Buddy)
    process.start()
