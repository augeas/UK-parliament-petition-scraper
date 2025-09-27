
from datetime import datetime
import os
import json
import subprocess as sp
import sys

from bokeh.embed import components
from bokeh.models import Legend
from bokeh.palettes import Category20
from bokeh.plotting import figure
from bokeh.resources import CDN
import jinja2
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
    'non_binary': 700312,
    'blockers': 702538,
    'athletes': 700219,
    'schools': 700221,
    'therapy': 700652
}

PETITION_URL = 'https://petition.parliament.uk/petitions/{}'

def get_and_save_petition(name, new=True):
    fname = name + '.csv'
    try:
        existing_df = pd.read_csv(fname)
        existing_df['timestamp'] = pd.to_datetime(existing_df.timestamp)
        existing_df['deadline'] = pd.to_datetime(existing_df.deadline)
        last_crawled = existing_df.timestamp.max().isoformat()
        if not new:
            return existing_df
    except:
        existing_df = pd.DataFrame()
        last_crawled = None
    new_df = pd.concat((existing_df, crawl_petition(PETITIONS[name], last_crawled)), axis=0)
    new_df.sort_values('timestamp').to_csv(fname, index=False)
    return new_df

if __name__ == '__main__':
    do_scrape = not sys.argv[-1] == 'dontscrape'
    petition_dfs = {k: get_and_save_petition(k, new=do_scrape) for k in PETITIONS.keys()}

    fig = figure(width=600, height=700, x_axis_type="datetime")
    fig.title.text = 'Open Parliamentary Petitions on Trans Issues'
    fig.xaxis.axis_label = 'date'
    fig.yaxis.axis_label = 'signatures (thousands)'
    fig.add_layout(Legend(), 'below')
    
    for df, colour in zip( 
        sorted(petition_dfs.values(), key=lambda df: df['count'].max(), reverse=True),
        Category20[(len(petition_dfs))]
    ):
        fig.line(df['timestamp'], df['count'] / 1000, line_width=2, color=colour, alpha=0.8,
           muted_color=colour, muted_alpha=0.2, legend_label=df.title.iloc[0])
        
    fig.legend.click_policy = 'mute'
    plt_script, plt_div = components(fig)

    pd.concat(list(petition_dfs.values())).to_csv('static/open_trans_petitions.csv', index=False)

    titles = {k: df.title.iloc[0] for k, df in petition_dfs.items()}
    by_deadline = sorted(
        [(k, petition_dfs[k].deadline.iloc[0]) for k in PETITIONS.keys()],
    key=lambda p: p[1])
    links = [
        {
            'url': PETITION_URL.format(PETITIONS[p]),
            'title': titles[p],
            'expires': ts.date().isoformat(),
            'id': PETITIONS[p]
        }
    for p, ts in by_deadline]
    id_dump = 'var petition_ids={};'.format(json.dumps(list(PETITIONS.values())))
    updated, _ = datetime.now().isoformat().split('.')
    loader = jinja2.FileSystemLoader(searchpath="./")
    env = jinja2.Environment(loader=loader)
    template = env.get_template('trans_petitions_template.html')
    with open('static/index.html', 'w') as index:
        index.write(template.render(
            petitions=links, id_dump=id_dump, updated=updated,
            resources = CDN.render(), plt_script=plt_script, plt_div=plt_div
        ))
