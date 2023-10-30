/*
view bioc_web_downloads
package and categories are inferred from the cs-uri-stem
Select only package downloads, which must have a valid category and end with a package tarball
The package tarball must be in the form 
    :<package_name>_<version>.tar.<compression>,
    where compression is gz, zip, or tgz
The category is extracted from the start of the cs-uri-stem, and must be in the form:
    /packages/<version>/<category>/...
Valid categories are: bioc, workflows, data/experiment, data/annotation

Note: Wherever a '//' appears in the uri-stem, it is treated as a single '/'
Note: The RE string is repeated multiple times becasue Athena does not have reasonable way
to handle manifest constants (as of Oct-2023) 

*/
CREATE OR REPLACE VIEW "bioc_web_downloads" AS
SELECT "date",
    "c-ip",
    "sc-status",
    replace(regexp_extract(
        "cs-uri-stem",
        '^/+packages/+[^/]*/+(bioc|workflows|data/+experiment|data/+annotation)/+(?:bin|src)/+(?:[^/]*/+)*([^_]*)_.*\.(?:tar|gz|zip|tgz)$',
        1
    ), 'data/', '') category,
    regexp_extract(
        "cs-uri-stem",
        '^/+packages/+[^/]*/+(bioc|workflows|data/+experiment|data/+annotation)/+(?:bin|src)/+(?:[^/]*/+)*([^_]*)_.*\.(?:tar|gz|zip|tgz)$',
        2
    ) package
FROM "bioc_web_logs"
WHERE (
        (
            "sc-status" BETWEEN 200 AND 399
        )
        AND regexp_like(
            "cs-uri-stem",
        '^/+packages/+[^/]*/+(bioc|workflows|data/+experiment|data/+annotation)/+(?:bin|src)/+(?:[^/]*/+)*([^_]*)_.*\.(?:tar|gz|zip|tgz)$'
        )
    )
