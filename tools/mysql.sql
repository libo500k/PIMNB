drop database if exists PIMNB;
create database PIMNB;
use PIMNB;

create table RegMano
(
ip varchar(39) not null,
nfvoid varchar(100) not null,
heartbeat int unsigned,
period int unsigned,
identityuri varchar(100) not null,
user varchar(100) not null,
passwd varchar(100) not null,
primary key(ip)
);

