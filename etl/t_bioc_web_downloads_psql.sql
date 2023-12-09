
-- For postgresql. databasse webstats
CREATE TABLE "bioc_web_downloads"(
  "date" date, 
  "c-ip" varchar(40), 
  "sc-status" INTEGER, 
  "category" varchar(16), 
  "package" varchar(64))
