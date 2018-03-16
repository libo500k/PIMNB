drop database if exists pimnb ;
create database pimnb;
use pimnb;

create table regmano
(
nfvoid varchar(36) not null,
heartbeat int unsigned,
period int unsigned,
identityuri varchar(255) not null,
luser varchar(16) not null,
lpasswd varchar(16) not null,
primary key(nfvoid)
);

