apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-initdb-config
data:
  init.sql: |
    CREATE DATABASE IF NOT EXISTS mydb;
    USE mydb;
    CREATE TABLE messages (id INT AUTO_INCREMENT PRIMARY KEY, message TEXT);
