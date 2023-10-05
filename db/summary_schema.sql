CREATE TABLE download_summary (
  "date" date,
  repo TEXT,
  package TEXT,
  IPcount BIGINT,
  downloadCount BIGINT
);

INSERT INTO download_summary values ('2021-01-01', 'bioc', 'S4Vectors', 198, 234);
SELECT * FROM download_summary;

