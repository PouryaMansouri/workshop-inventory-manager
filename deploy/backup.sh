#!/usr/bin/env bash
set -euo pipefail

app_dir=/opt/workshop
backup_dir=/opt/workshop-backups
stamp=$(date -u +%Y%m%dT%H%M%SZ)

install -d -m 700 "$backup_dir"
cd "$app_dir"

db_tmp="$backup_dir/database-$stamp.sql.gz.tmp"
media_tmp="$backup_dir/media-$stamp.tar.gz.tmp"
trap 'rm -f "$db_tmp" "$media_tmp"' EXIT

docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip -9 > "$db_tmp"
gzip -t "$db_tmp"
mv "$db_tmp" "$backup_dir/database-$stamp.sql.gz"

tar -czf "$media_tmp" -C "$app_dir" media
tar -tzf "$media_tmp" >/dev/null
mv "$media_tmp" "$backup_dir/media-$stamp.tar.gz"

find "$backup_dir" -maxdepth 1 -type f \( -name 'database-*.sql.gz' -o -name 'media-*.tar.gz' \) -mtime +30 -delete
