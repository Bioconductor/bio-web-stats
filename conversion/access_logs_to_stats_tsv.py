"""Export access_log tables from server stats.bioconductor.org."""
import csv
import gzip
import io
import sqlite3
from datetime import datetime as dt

import psycopg2

from bioc_webstats.aws_functions import psql_get_connection

# TODO Use AWS paraemter store
secret_name = "rds-db-credentials/cluster-BFK2EVT2EFIRT4B5XVC6PDOXIQ/postgres/1701682809099"
region_name = "us-east-1"
database_name = 'webstats'


def export_chunked_tsv(db_path, query, chunk_size, start_at=0):
    """Export the table in chunks."""


    target_connection = psql_get_connection(secret_name, region_name, database_name)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    record_count = 0
    offset = start_at
    while True:
        with io.StringIO() as f:
            writer = csv.writer(f, delimiter='\t')
            cursor.execute(f"{query} LIMIT {chunk_size} OFFSET {offset}")
            rows = cursor.fetchall()

            if not rows:
                break

            writer.writerows(rows)
            f.seek(0)
            target_cursor = target_connection.cursor()
            target_cursor.copy_from(f, 'bioc_web_downloads')
            target_connection.commit()
            record_count += len(rows)
            target_cursor.close()
            # end with
            print(offset)
        offset += chunk_size
        # end while

    conn.close()
    target_connection.close()
    return record_count

chunk_size = 100000

for year in range(2009, 2021):
    source_db = f'/mnt/data/home/biocadmin/download_dbs/download_db_{year}.sqlite'
    status_colname = 'errorcode' if year < 2020 else 'statuscode'
    # left(ips) due to cruft in the ip address column
    # name change as of 2019 errorcode -> statuscode
    sql_select_command = f"""
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
            SUBSTR(ips, 1, 30) as "c-ip",
            {status_colname} as "sc-status",
            biocrepo as "category",
            "package"
        from access_log
        """
    print('start at ' +dt.now().strftime("%Y-%m-%d %H:%M:%S" + "  " + str(year)))
    record_count = export_chunked_tsv(source_db, sql_select_command, chunk_size)
    print('end at ' +dt.now().strftime("%Y-%m-%d %H:%M:%S") + "Year=" + str(year) + " Total records=" + str(record_count))
