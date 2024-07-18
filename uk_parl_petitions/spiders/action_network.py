
from datetime import datetime

from dateutil import parser

from uk_parl_petitions.spiders.petition import PetitionSpider

PETITION_URL = 'actionnetwork.org/petitions/{}'
SNAPSHOT_URL = 'https://web.archive.org/web/{}/{}'


class ActionNetworkSpider(PetitionSpider):

    name = 'action_network'

    # e.g: scrapy crawl action_newtork -a petition=open-letter-to-the-health-secretary -o streeting_fail.csv
    def __init__(self, petition=None, last_crawled=None):
        if petition:
            self.petition_url = PETITION_URL.format(petition)
        else:
            self.petition_url = None
            
        if last_crawled:
            self.last_crawled = parser.parse(last_crawled)
        else:
            self.last_crawled = datetime.fromtimestamp(0)

    def parse_signatures(self, response):
        yield {
            'timestamp': response.meta.get(
                'timestamp', datetime.now()).isoformat().split('.')[0],
            'count': int(''.join(
                filter(str.isdigit,
                response.css('div.action_status_running_total').xpath('text()').extract_first()))
            )
        }
