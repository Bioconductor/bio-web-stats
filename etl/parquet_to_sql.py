# pip install pandas fastparquet
# for f in /path/to/directory/*; do mv "$f" "$f.parquet"; done
"""utility for converting parquet files to sqlite3.

1. download the parquet files from S3
2. add the file extensions:
for f in  ~/temp/parquet//*; do mv "$f" "$f.parquet"; done
3. Run this script
"""
import pandas as pd
import fastparquet

"""
CREATE TABLE stats (
        category TEXT, 
        package TEXT, 
        date DATE, 
        ip_count BIGINT, 
        download_count BIGINT)
"""


from sqlalchemy import create_engine

df = pd.read_parquet('~/temp/parquet/', engine='fastparquet')
df['date'] = df['date'].dt.date

# Create engine
# TODO must be in specific directory
engine = create_engine('sqlite:///dev.db')

# Write DataFrame to database
df.to_sql('stats', engine, index=False, if_exists='replace')
