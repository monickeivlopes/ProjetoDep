create database db_projetoHotel;
use db_projetoHotel;

create table hospede(
id int not null primary key auto_increment,
nome varchar(50),
cpf varchar(50) ,
telefone varchar(20),
email varchar(50)
);

create table quarto(
id int not null primary key auto_increment,
numero int,
tipo varchar(50),
preco float,
capacidade int, 
descricao text
);

create table reserva(
id int not null primary key auto_increment,
hos_id int,
quarto_id int not null,
checkin date,
checkout date,
total float,
FOREIGN KEY (hos_id) REFERENCES hospede(id),
FOREIGN KEY (quarto_id) REFERENCES quarto(id)
);

create table reserva_quarto (
	id int not null primary key auto_increment,
    res_id int not null,
    qua_id int not null,
    dataRes date not null,
    status varchar(20) not null,
    foreign key (res_id) references reserva(id),
    foreign key (qua_id) references quarto(id)
);
