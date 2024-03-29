
from datetime import datetime
from multiprocessing import Process
import os

import jinja2
from matplotlib import pyplot as plt
import pandas as pd
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def read_petition_csv(path):
    df = pd.read_csv(path).sort_values('timestamp')
    df['timestamp'] = pd.to_datetime(df.timestamp)
    return df

def crawl_petition(petition_id, last_crawled=None):
    settings = get_project_settings()
    work_dir = os.getcwd()
    
    csv_path = '{}/{}.csv'.format(work_dir, petition_id)
    
    settings['FEEDS'] = {csv_path: {'format': 'csv'}}
    
    process = CrawlerProcess(settings)
    process.crawl('petition', petition=petition_id, last_crawled=last_crawled)
    proc = Process(target=process.start)
    proc.start()
    proc.join()
    
    df = read_petition_csv(csv_path)
    os.remove(csv_path)
    
    return df

def petition_rows(fname, petition_id):
    try:
        existing_df = read_petition_csv(fname)
        ts = existing_df.timestamp.max().isoformat()
    except:
        existing_df = pd.DataFrame()
        ts = None

        
    petition_df = pd.concat(
        (existing_df, crawl_petition(petition_id, last_crawled=ts)))

    petition_df.to_csv(fname, index=False)
    
    return petition_df

def petition_chart(crawl=True):
    if crawl:
        tra_df = petition_rows('tra_ehrc.csv', 627984)
        gc_df = petition_rows('gc_ehrc.csv', 623243)
    else:
        tra_df =  read_petition_csv('tra_ehrc.csv')
        gc_df =  read_petition_csv('gc_ehrc.csv')
    
    plt.figure()
    plt.xticks(rotation=30, ha='right')
    plt.plot(tra_df['timestamp'], tra_df['count'], label='pro trans')
    plt.plot(gc_df['timestamp'], gc_df['count'], label='anti trans')
    plt.xlabel('date')
    plt.ylabel('signatures')
    plt.title('''Signatures for the UK Parliament Petitions regarding the Equality Act's definition of sex''')
    plt.legend()
    plt.savefig('ehrc_petitions.png', bbox_inches='tight', pad_inches=0.3)
    
def render_template():
    loader = jinja2.FileSystemLoader(searchpath="./")
    env = jinja2.Environment(loader=loader)
    template = env.get_template('ehrc_template.html')
    with open('index.html', 'w') as index:
        index.write(template.render(updated=datetime.now().ctime()))
    
if __name__ == '__main__':
    petition_chart()
    render_template()
