CREATE TABLE IF NOT EXISTS emails(
id SERIAL PRIMARY KEY,
email VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS phones(
id SERIAL PRIMARY KEY,
phone VARCHAR(255) NOT NULL
);
INSERT INTO emails(email) VALUES ('test@mail.ru');
INSERT INTO phones(phone) VALUES ('89999999999');
create user replicator with replication encrypted password 'Qq12345';
select pg_create_physical_replication_slot('replication_slot');
GRANT pg_read_all_data TO replicator;
GRANT pg_write_all_data TO replicator;
