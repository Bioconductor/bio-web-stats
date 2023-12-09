"""Export access_log tables from server stats.bioconductor.org."""
import csv
import io
import gzip
import psycopg2
import sqlite3
from datetime import datetime as dt

from psql_connection import psql_get_connection
year = "2022"
source_db = f'/mnt/data/home/biocadmin/download_dbs/download_db_{year}.sqlite'
chunk_size = 1000000
output_path = '/home/ubuntu'

sql_select_command = """
select strftime(
        '%Y-%m-%d',
        substr(day_month_year, 8, 4) || '-' || case
            substr(day_month_year, 4, 3)
            when 'Jan' then '01'
            when 'Feb' then '02'
            when 'Mar' then '03'
            when 'Apr' then '04'
            when 'May' then '05'
            when 'Jun' then '06'
            when 'Jul' then '07'
            when 'Aug' then '08'
            when 'Sep' then '09'
            when 'Oct' then '10'
            when 'Nov' then '11'
            when 'Dec' then '12'
        end || '-' || substr(day_month_year, 1, 2)
    ) AS "date",
    ips as "c-ip",
    statuscode as "sc-status",
    biocrepo as "category",
    "package"
from access_log
"""


def export_chunked_tsv(db_path, query, chunk_size, output_path):
    """Export the table in chunks."""

    target_connection = psql_get_connection()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    offset = 0
    while True:
        with io.StringIO() as f:
            writer = csv.writer(f, delimiter='\t')
            cursor.execute(f"{sql_select_command} LIMIT {chunk_size} OFFSET {offset}")
            rows = cursor.fetchall()

            if not rows:
                break

            writer.writerows(rows)
            f.seek(0)
            target_cursor = target_connection.cursor()
            target_cursor.copy_from(f, 'bioc_web_downloads')
            target_connection.commit()
            target_cursor.close()
            # end with
            print(offset)
        offset += chunk_size
        # end while

    conn.close()
    target_connection.close()


print('start at ' +dt.now().strftime("%Y-%m-%d %H:%M:%S"))
export_chunked_tsv(source_db, sql_select_command, chunk_size, output_path)
print('end at ' +dt.now().strftime("%Y-%m-%d %H:%M:%S"))
