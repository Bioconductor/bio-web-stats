/*
view bioc_web_downloads
package and categories are inferred from the uri
Select only package downloads, which must have a valid category and end with a package tarball
The package tarball must be in the form 
    :<package_name>_<version>.tar.<compression>,
    where compression is gz, zip, or tgz
The category is extracted from the start of the uri, and must be in the form:
    /packages/<version>/<category>/...
Valid categories are: bioc, workflows, data/experiment, data/annotation

Note: Wherever a '//' appears in the uri-stem, it is treated as a single '/'
Note: standard name for uri is "cs-uri-stem"
Note: The RE string is repeated multiple times becasue Athena does not have reasonable way
to handle manifest constants (as of Oct-2023) 
*/

CREATE OR REPLACE VIEW "v_bioc_web_downloads" AS 
WITH
  T AS (
   SELECT
     "date"
   , request_ip "c-ip"
   , "status" "sc-status"
   , replace(regexp_extract("uri", '^/+packages/+[^/]*/+(bioc|workflows|data/+experiment|data/+annotation)/+(?:bin|src)/+(?:[^/]*/+)*([^_]*)_.*\.(?:tar|gz|zip|tgz)$', 1), 'data/', '') category
   , regexp_extract("uri", '^/+packages/+[^/]*/+(bioc|workflows|data/+experiment|data/+annotation)/+(?:bin|src)/+(?:[^/]*/+)*([^_]*)_.*\.(?:tar|gz|zip|tgz)$', 2) package
   , LPAD(CAST(year("date") AS VARCHAR), 4, '0') "year"
   , LPAD(CAST(month("date") AS VARCHAR), 2, '0') "month"
   , LPAD(CAST(day("date") AS VARCHAR), 2, '0') "day"
   FROM
     "cloudfront_logs"
   WHERE (("status" IN (200, 301, 302, 307, 308)) AND regexp_like("uri", '^/+packages/+[^/]*/+(bioc|workflows|data/+experiment|data/+annotation)/+(?:bin|src)/+(?:[^/]*/+)*([^_]*)_.*\.(?:tar|gz|zip|tgz)$'))
) 
SELECT *
FROM T
WHERE package <> ''
    AND length("c-ip") <= 40
    AND length(category) <= 16
    AND length("package") <= 64

