
from flask import Flask, make_response, Response, abort
from flask import Flask, render_template
from markupsafe import escape
import pandas as pd
import db.db as dbm
from db.db import PackageType
 

PATH = '/packages/stats'

# TDODO: THIS IS MOCK DATABASE FOR INITIAL TESTING
from datetime import date

def dataframe_to_string_list(df):
    headers = list(df.columns)
    header_string = "\t".join(headers)
    rows = [header_string]
    for _, row in df.iterrows():
        row_string = "\t".join(map(str, row))
        rows.append(row_string)
    return rows




# TDODO: THIS IS MOCK DATABASE FOR INITIAL TESTING
from datetime import date

test_database_spec = [
        (PackageType.BIOC, 'affy', '2023-09-01'), 
        (PackageType.BIOC, 'affydata', '2023-08-01'),
        (PackageType.ANNOTATION, 'BSgenome.Hsapiens.UCSC.hg38', '2019-01-01'),
        (PackageType.ANNOTATION, 'BSgenome.Scerevisiae.UCSC.sacCer3', '2021-12-01')
    ]

db = dbm.DatabaseService(dbm.TestDatabaseConnection)
db.create()
db.populate(123, date(2023, 10, 1), test_database_spec)

df1 = db.get_download_counts(PackageType.ANNOTATION)

# df1['year'] = [d.year for d in df1['date']]
# df1['month'] = [d.month for d in df1['date']]

import numpy as np
# x = df1.drop_duplicates(subset=['package', 'year'])

df2 = df1.copy()
df2['year'] = [d.year for d in df2['date']]
df2 = df2.loc[:, ['category', 'package', 'year']].drop_duplicates()
df2.reset_index(drop=True, inplace=True)

data2 = {
    'category': df2['category'],
    'package': df2['package'],
    'date': [date(d, 12, 31) for d in df2['year']],
    'ip_count': np.random.randint(10, 1000, df2.shape[0]),
    'download_count': np.random.randint(20, 2000, df2.shape[0])
}
df2 = pd.DataFrame(data2)


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

result = dataframe_to_text_tab(df1, df2)

pass