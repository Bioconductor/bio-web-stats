CREATE TABLE access_log (
    ips TEXT NOT NULL,
    day_month_year TEXT NOT NULL,
    month_year TEXT NOT NULL,
    time TEXT NOT NULL,
    utc_offset TEXT NOT NULL,
    method TEXT NOT NULL,
    url TEXT NOT NULL,
    protocol TEXT NOT NULL,
    statuscode TEXT NOT NULL,
    bytes INTEGER NULL,
    referer TEXT NULL,
    user_agent TEXT NULL,
    biocrepo_relurl TEXT NULL,
    biocrepo TEXT NULL,
    biocversion TEXT NULL,
    package TEXT NULL,
    pkgversion TEXT NULL,
    pkgtype TEXT NULL
);
CREATE INDEX ipsI ON access_log (ips);
CREATE INDEX month_yearI ON access_log (month_year);
CREATE INDEX packageI ON access_log (package);


select day_month_year as "date", ips as "c-ip", statuscode as "sc-status", "url" as "cs-uri-stem" from access_log
