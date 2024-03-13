/*
Athena SQL to expose www.biconductor.org web logs as a SQL table
*/
CREATE EXTERNAL TABLE `bioc_web_logs_p`(
  `date` date COMMENT '', 
  `time` string COMMENT '', 
  `x-edge-location` string COMMENT '', 
  `sc-bytes` bigint COMMENT '', 
  `c-ip` string COMMENT '', 
  `cs-method` string COMMENT '', 
  `cs(host)` string COMMENT '', 
  `cs-uri-stem` string COMMENT '', 
  `sc-status` bigint COMMENT '', 
  `cs(referer)` string COMMENT '', 
  `cs(user-agent)` string COMMENT '', 
  `cs-uri-query` string COMMENT '', 
  `cs(cookie)` string COMMENT '', 
  `x-edge-result-type` string COMMENT '', 
  `x-edge-request-id` string COMMENT '', 
  `x-host-header` string COMMENT '', 
  `cs-protocol` string COMMENT '', 
  `cs-bytes` bigint COMMENT '', 
  `time-taken` double COMMENT '', 
  `x-forwarded-for` string COMMENT '', 
  `ssl-protocol` string COMMENT '', 
  `ssl-cipher` string COMMENT '', 
  `x-edge-response-result-type` string COMMENT '', 
  `cs-protocol-version` string COMMENT '', 
  `fle-status` bigint COMMENT '', 
  `fle-encrypted-fields` bigint COMMENT '', 
  `c-port` bigint COMMENT '', 
  `time-to-first-byte` double COMMENT '', 
  `x-edge-detailed-result-type` string COMMENT '', 
  `sc-content-type` string COMMENT '', 
  `sc-content-len` bigint COMMENT '', 
  `sc-range-start` bigint COMMENT '', 
  `sc-range-end` bigint COMMENT '')
PARTITIONED BY (year string, month string, day string)
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY '\t' 
LOCATION
  's3://web-stats-dev/weblogs/'
TBLPROPERTIES (
    'skip.header.line.count'='2'

  "projection.enabled" = "true",
  "projection.year.type" = "integer",
  "projection.year.range" = "2009,2027",
  "projection.year.format" = "yyyy",
  "projection.year.interval" = "1",
  "projection.year.interval.unit" = "YEARS",
  "projection.month.type" = "integer",
  "projection.month.range" = "1,12",
  "projection.month.format" = "MM",
  "projection.month.interval" = "1",
  "projection.month.interval.unit" = "MONTHS",
  "projection.day.type" = "integer",
  "projection.day.range" = "1,31",
  "projection.day.format" = "dd",
  "projection.day.interval" = "1",
  "projection.day.interval.unit" = "DAYS",
  "storage.location.template" = "s3://web-stats-dev/weblogs/${year}/${month}/${day}")
