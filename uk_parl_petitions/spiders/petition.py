
from datetime import datetime
from itertools import starmap

from dateutil import parser
import scrapy

PETITION_URL = 'petition.parliament.uk/petitions/{}'
SNAPSHOT_URL = 'https://web.archive.org/web/{}/{}'

class PetitionSpider(scrapy.Spider):
    name = 'petition'

    # e.g: scrapy crawl petition -a petition=300976 -o anti_conversion.csv
    def __init__(self, petition=None, last_crawled=None):
        if petition:
            self.petition_url = PETITION_URL.format(petition)
        else:
            self.petition_url = None
            
        if last_crawled:
            self.last_crawled = parser.parse(last_crawled)
        else:
            self.last_crawled = datetime.fromtimestamp(0)
            

    def parse(self):
        pass

    # Get all the snapshots:
    # https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server#basic-usage
    def start_requests(self):
        if self.petition_url:
            return [scrapy.http.Request(
                'https://web.archive.org/cdx/search/cdx?url={}'.format(
                self.petition_url), callback=self.parse_snapshots)]
        else:
            return []
    
    def parse_snapshots(self, response):
        snapshots = sorted(snap[1] for snap in
            filter(None, map(str.split, response.text.split('\n'))))

        # Yes, the various fields of the timestamps are just concatenated togther.

        indices = (0, 4, 6, 8, 10, 12, 14)
        slices = tuple(starmap(slice, zip(indices, indices[1:])))
        
        timestamps = (datetime(*map(int, map(snap.__getitem__, slices)))
            for snap in snapshots)
        
        for snap, ts in filter(
            lambda t: t[1] > self.last_crawled, zip(snapshots, timestamps)):
            yield scrapy.http.Request(SNAPSHOT_URL.format(snap, self.petition_url),
                meta={'timestamp': ts}, callback=self.parse_signatures)
            
        yield scrapy.http.Request('https://'+self.petition_url,
            callback=self.parse_signatures)
        
    def parse_signatures(self, response):
        yield {
            'timestamp': response.meta.get(
                'timestamp', datetime.now()).isoformat().split('.')[0],
            'count': int(response.css('span.count').xpath(
                '@data-count').extract_first()),
            'title': response.css('h1>span.heading-secondary').xpath(
                'following-sibling::text()').extract_first().strip(),
            'deadline': parser.parse(''.join(response.css('li.meta-deadline').xpath(
                'child::text()').extract())).isoformat()
        }
            

