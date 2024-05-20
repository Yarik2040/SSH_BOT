echo "host replication repl_user 0.0.0.0/0 md5" >> /var/lib/postgresql/data/pg_hba.conf
pg_ctl reload