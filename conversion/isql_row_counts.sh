# report row counts for all sqlite3 databases
for file in /mnt/data/home/biocadmin/download_dbs/download_db_*.sqlite; do
   echo $(basename "$file")  $(sqlite3 "$file" "select count(*) from access_log")
 done
 