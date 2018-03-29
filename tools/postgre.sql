drop database if exists pimnb;
create database pimnb;
\c pimnb;

create table regmano
(
nfvoid varchar(36) not null PRIMARY KEY,
heartbeat int,
period int,
identityuri varchar(255) not null,
luser varchar(16) not null,
lpasswd varchar(16) not null
);

create table persistence
(
nfvoid varchar(36) not null,
failtime bigint not null PRIMARY KEY,
failip varchar(36) not null,
failbody BYTEA,
failmethod varchar(6) not null,
failuri varchar(255) not null
);
