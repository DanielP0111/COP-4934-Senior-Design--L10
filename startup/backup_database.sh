#!/bin/bash
# Creates a backup of the database every 10 minutes and hands control back to the default entrypoint
while true; do
    mysqldump -uroot -p$MYSQL_ROOT_PASSWORD billdb | gzip > /mysql-backups/billdb_$(date +%Y%m%d_%H%M%S).sql.gz
    sleep 600
done &
exec docker-entrypoint.sh mysqld