import pandas as pd

file_name = 'etl/weblog_sample_short.tsv'
column_names = 'date time x-edge-location sc-bytes c-ip cs-method cs(Host) cs-uri-stem sc-status cs(Referer) cs(User-Agent) cs-uri-query cs(Cookie) x-edge-result-type x-edge-request-id x-host-header cs-protocol cs-bytes time-taken x-forwarded-for ssl-protocol ssl-cipher x-edge-response-result-type cs-protocol-version fle-status fle-encrypted-fields c-port time-to-first-byte x-edge-detailed-result-type sc-content-type sc-content-len sc-range-start sc-range-end'.split(' ')
df = pd.read_csv(file_name, delimiter='\t', skiprows=2, header=None)


old_script = [
  {
    "Name": "col0",
    "Type": "string"
  },
  {
    "Name": "col1",
    "Type": "string"
  },
  {
    "Name": "col2",
    "Type": "string"
  },
  {
    "Name": "col3",
    "Type": "bigint"
  },
  {
    "Name": "col4",
    "Type": "string"
  },
  {
    "Name": "col5",
    "Type": "string"
  },
  {
    "Name": "col6",
    "Type": "string"
  },
  {
    "Name": "col7",
    "Type": "string"
  },
  {
    "Name": "col8",
    "Type": "bigint"
  },
  {
    "Name": "col9",
    "Type": "string"
  },
  {
    "Name": "col10",
    "Type": "string"
  },
  {
    "Name": "col11",
    "Type": "string"
  },
  {
    "Name": "col12",
    "Type": "string"
  },
  {
    "Name": "col13",
    "Type": "string"
  },
  {
    "Name": "col14",
    "Type": "string"
  },
  {
    "Name": "col15",
    "Type": "string"
  },
  {
    "Name": "col16",
    "Type": "string"
  },
  {
    "Name": "col17",
    "Type": "bigint"
  },
  {
    "Name": "col18",
    "Type": "double"
  },
  {
    "Name": "col19",
    "Type": "string"
  },
  {
    "Name": "col20",
    "Type": "string"
  },
  {
    "Name": "col21",
    "Type": "string"
  },
  {
    "Name": "col22",
    "Type": "string"
  },
  {
    "Name": "col23",
    "Type": "string"
  },
  {
    "Name": "col24",
    "Type": "bigint"
  },
  {
    "Name": "col25",
    "Type": "bigint"
  },
  {
    "Name": "col26",
    "Type": "bigint"
  },
  {
    "Name": "col27",
    "Type": "double"
  },
  {
    "Name": "col28",
    "Type": "string"
  },
  {
    "Name": "col29",
    "Type": "string"
  },
  {
    "Name": "col30",
    "Type": "bigint"
  },
  {
    "Name": "col31",
    "Type": "bigint"
  },
  {
    "Name": "col32",
    "Type": "bigint"
  }
]

# print(df)
pass

for i in range(0,len(old_script)):
    old_script[i]['Name'] = column_names[i]
    
print(old_script)