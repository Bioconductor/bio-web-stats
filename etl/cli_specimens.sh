 aws glue get-table --database-name glue-sup-db --name "bw-dev_bioc_weblogs_small_test"

 aws glue update-table --cli-input-json file://change-table-location.json

 aws glue create-table --database-name glue-sup-db --table-input file://etl/glue_weblog_table_in.json

aws glue delete-table  --database-name  glue-sup-db --name bioc_web_logs
