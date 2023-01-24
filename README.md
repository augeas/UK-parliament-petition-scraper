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

This may one day may be used to demonstrate the merits of [scrapy](https://scrapy.org/) (a *scraping*
framework) for *scraping things* over
[Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), a perfectly fine HTML
parser.

Unfortunately, scraping winth Beautiful Soup, does rather tend to make for rather pithy Medium articles
and, err.. ...[letters to Nature](https://www.nature.com/articles/d41586-020-02558-0).




