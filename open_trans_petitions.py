
import os
import subprocess as sp

import jinja2
from matplotlib import pyplot as plt
import pandas as pd

def crawl_petition(pid, last_crawled=None):
    try:
        os.remove('tmp.csv')
    except:
        pass
    args = [
        'scrapy', 'crawl', 'petition', '-a', 'petition={}'.format(pid), '-o', 'tmp.csv']
    if last_crawled:
        args += ['-a', 'last_crawled={}'.format(last_crawled)]
    sp.run(args, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    df = pd.read_csv('tmp.csv').sort_values('timestamp')
    df['timestamp'] = pd.to_datetime(df.timestamp)
    df['deadline'] = pd.to_datetime(df.deadline)
    return df

PETITIONS = {
    'nhs_transition': 704793,
    'self_id': 701159,
    'cass': 700217,
    'nhs_wards': 703861,
    'nhs_hormones': 704447,
    'gc_equality': 712741,
    'funding': 705870,
    'non_binary': 700312
}

PETITION_URL = 'https://petition.parliament.uk/petitions/{}'

def get_and_save_petition(name):
    fname = name + '.csv'
    try:
        existing_df = pd.read_csv(fname)
        existing_df['timestamp'] = pd.to_datetime(existing_df.timestamp)
        existing_df['deadline'] = pd.to_datetime(existing_df.deadline)
        last_crawled = existing_df.timestamp.max().isoformat()
    except:
        existing_df = pd.DataFrame()
        last_crawled = None
    new_df = pd.concat((existing_df, crawl_petition(PETITIONS[name], last_crawled)), axis=0)
    new_df.sort_values('timestamp').to_csv(fname, index=False)
    return new_df

if __name__ == '__main__':    
    petition_dfs = {k: get_and_save_petition(k) for k in PETITIONS.keys()}

    plt.xticks(rotation=30, ha='right')
    for df in sorted(petition_dfs.values(), key=lambda df: df['count'].max(), reverse=True):
        plt.plot(df['timestamp'], df['count'], marker='o', label=df.title.loc[0])
    plt.xlabel('date')
    plt.ylabel('signatures')
    plt.title('Open Parliamentary Petitions on Trans Issues')
    plt.legend(loc='lower left', bbox_to_anchor=(-0.1, -0.75))
    plt.savefig('all_open_trans_petitions.png', bbox_inches='tight')

    pd.concat(list(petition_dfs.values())).to_csv('open_trans_petitions.csv')

    titles = {k: df.title.loc[0] for k, df in petition_dfs.items()}
    by_deadline = sorted(
        [(k, petition_dfs[k].deadline.loc[0]) for k in PETITIONS.keys()],
    key=lambda p: p[1])
    links = [
        (PETITION_URL.format(PETITIONS[p]), '{} ({})'.format(titles[p], ts.date().isoformat()))
    for p, ts in by_deadline]

    loader = jinja2.FileSystemLoader(searchpath="./")
    env = jinja2.Environment(loader=loader)
    template = env.get_template('trans_petitions_template.html')
    with open('index.html', 'w') as index:
        index.write(template.render(petitions=links))
