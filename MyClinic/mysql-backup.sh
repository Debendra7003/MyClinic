#!/bin/bash
TIMESTAMP=$(date +"%F")
BACKUP_DIR="path/to/backup/directory"
MYSQL_CONTAINER="myclinic-db-1"
DB_NAME="myclinic"
DB_USER="clinicuser"
DB_PASS="clinicpass"

mkdir -p $BACKUP_DIR
docker exec $MYSQL_CONTAINER /usr/bin/mysqldump -u $DB_USER --password=$DB_PASS $DB_NAME > $BACKUP_DIR/$DB_NAME-$TIMESTAMP.sql
