
from flask import Flask, make_response, Response, abort
from flask import Flask, render_template
from markupsafe import escape
import pandas as pd
from db import PackageType
 

PATH = '/packages/stats'

from datetime import date

def dataframe_to_string_list(df):
    headers = list(df.columns)
    header_string = "\t".join(headers)
    rows = [header_string]
    for _, row in df.iterrows():
        row_string = "\t".join(map(str, row))
        rows.append(row_string)
    return rows




# TDODO: REMOVE
# from datetime import date



def dataframe_to_text_tab(df1: pd.DataFrame, df2: pd.DataFrame) -> [str]:
    # TODO fill in empty month zeroes.
    MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df1['month'] = [MONTH_NAMES[d.month - 1] for d in df1['date']]
    df2['month'] = 'all'
    df = pd.concat([df1, df2], ignore_index=True)
    df.drop('category', axis=1, inplace=True)

    df.sort_values(by=['package', 'date'], inplace=True)
    df['year'] = [d.year for d in df['date']]
    df = df[['package', 'year', 'month', 'ip_count', 'download_count']]
    df.columns = ['Package','Year','Month','Nb_of_distinct_IPs', 'Nb_of_downloads']
    result = ['\t'.join(map(str, row._asdict().values())) for row in df.itertuples()]
    return df

pass