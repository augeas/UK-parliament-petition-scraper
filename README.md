# UK-parliament-petition-scraper
How to use the WayBack Machine to scrape the growth in signatures for UK Parliament petitions.

If one has ever wondered about the dynamics of online petition signing, the
[WayBack Machine](https://archive.org/web/) may be able to help, it has an
[API](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server).

For example for the petition to
[Make LGBT conversion therapy illegal in the UK](https://petition.parliament.uk/petitions/300976):

```
scrapy crawl petition -a petition=300976 -o anti_conversion.csv
```

Substitute the ID from the URL of the petition of your choice.
(Run in the same directory as `scrapy.cfg`, having installed scrapy with `pip3 install scrapy`.)

Then:

```python
from matplotlib import pyplot as plt
import pandas as pd

df = pd.read_csv('anti_conversion.csv').sort_values('timestamp')
df['timestamp'] = pd.to_datetime(df.timestamp)
df['delta'] = df[['count']].diff()
df = df[df.delta >1]

plt.xticks(rotation=30, ha='right')
plt.plot(df['timestamp'], df['count'])
plt.xlabel('date')
plt.ylabel('signatures')
plt.title('''Signatures for the UK parliament "Ban LGBT Conversion 'Therapy'" Petition''')
plt.show()
```

![Signatures for the UK parliament "Ban LGBT Conversion 'Therapy'" Petition](https://github.com/augeas/UK-parliament-petition-scraper/blob/master/anti_conversion.png)

There's also a spider for the "Action Network", for example, the "[Open Letter to the Health Secretary](https://actionnetwork.org/petitions/open-letter-to-the-health-secretary)" with regard to continuing the [ban on puberty blockers](https://trans-express.lgbt/post/756244126854512641/there-is-a-pro-transgender-labour-revolt-against) from the outgoing Conservative Government.

```bash
scrapy crawl action_network -a petition=open-letter-to-the-health-secretary -o streeting_fail.csv
```

Or, there's the [petition to reverse the suspension of 7 Labour MPs](https://actionnetwork.org/petitions/keir-starmer-reverse-the-7-mps-suspension/)
with regard to the [child benefit cap](https://www.aljazeera.com/news/2024/7/24/what-is-the-uks-two-child-cap-on-benefits-and-will-labour-reverse-it).

```bash
scrapy crawl action_network -a petition=keir-starmer-reverse-the-7-mps-suspension -o starmer_fail.csv
```


This may one day may be used to demonstrate the merits of [scrapy](https://scrapy.org/) (a *scraping*
framework) for *scraping things* over
[Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), a perfectly fine HTML
parser.

Unfortunately, scraping with Beautiful Soup, does rather tend to make for rather pithy Medium articles
and, err.. ...[letters to Nature](https://www.nature.com/articles/d41586-020-02558-0).




