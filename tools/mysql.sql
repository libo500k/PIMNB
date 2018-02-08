drop database if exists PIMNB;
create database PIMNB;
use PIMNB;

create table RegMano
(
nfvoid varchar(36) not null,
heartbeat int unsigned,
period int unsigned,
identityuri varchar(255) not null,
user varchar(16) not null,
passwd varchar(16) not null,
primary key(nfvoid)
);

