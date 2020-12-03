#!/bin/bash
sudo apt update && sudo apt install postgresql postgresql-contrib -y
sudo -u postgres sh -c "psql -c \"CREATE USER cloud WITH PASSWORD 'cloud';\" && createdb -O cloud tasks"
sudo sed -i "/#listen_addresses/ a\listen_addresses = '*'" /etc/postgresql/10/main/postgresql.conf
sudo sed -i "a\host all all 0.0.0.0/0 md5" /etc/postgresql/10/main/pg_hba.conf
sudo systemctl restart postgresql