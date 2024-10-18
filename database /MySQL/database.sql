create database HolidayIN;
use HolidayIN;

create table bookings (
B_Id integer (3) auto_increment  not null,
Primary key(b_id),
PassengerNo varchar (2) not null,
departuredate date  not null,
returndate date  not null, 
bookeddate date  not null,
destination varchar (15) not null
);

create table CAccount (
A_id integer (4) not null auto_increment,
Primary key(a_id),
book_id varchar (3),
Cname varchar (20) not null,
Cemail varchar (20) not null,
CPassword varchar (8) not null
-- foreign key(Book_id). WHY ISNT IT WORKING?
	-- references bookings(B_id)
    -- on delete set null 
    -- on update cascade 
);

create table HPackage (
p_id integer (5) not null auto_increment, 
primary key (p_id),
acc_id varchar (4) not null, 
p_deal1 varchar (10), 
p_deal2 varchar (10),
p_deal3 varchar (10),

foreign key (acc_id)
	references CAccount (a_id)
    on delete set null
    on update cascade 
-- CAN YOU HAVE MORE THAN ONE FOREIGN KEY PER TABLE?
);

create table VIP (
v_id int (3) auto_increment, -- WHAT DOES AUTO-INCREMENT DO?
primary key (v_id),
bo_id varchar(3),
vbusiness varchar (3),
veconomy varchar (3),
foreign key (bo_id)
	references bookings (b_id)
    on delete set null
    on update cascade
);

create table Payment (
p_id integer (4) auto_increment,
primary key (p_id),
b_id varchar (4),
pdate date not null,
Poption varchar (10) not null,
pAmount integer (5) not null,
foreign key (b_id)
	references bookings (b_id)
    on delete set null
    on update cascade 
);

create table invoice (
i_id integer (5) auto_increment,
primary key (i_id),
bk_id varchar (4),
CAdress varchar (100),
PConfimation varchar (30),
foreign key (bk_id)
	references bookings (b_id)
    on delete set null
    on update cascade 
);

insert into bookings values -- when the column on the table is auto_increment, 
-- do we have to put a value down?
(102, 2, '12-12-22', '13-01-23', '10-11-22', 'bristol'),
(103, 5,'15-09-23', '16-02-23', '12-05-22', 'Manchester'),
(104, 4, '15-10-23', '20-11-23', '10-04-22', 'Dundee'),
(105, 3, '10-05-23', '25-05-23', '01-04-23', 'Manchester');

insert into CAccount values -- when there's a foreign key, do we have to reenter that value?
(1002, 102, 'Lola Smith', 'Lola@gmail.com', 'senha123'),
(1003, 104, 'Milo Jones', 'm.jones@yahoo.com', 'Brillian'),
(1004, 105, 'Will Brown', 'willbrown@icloud.com', 'Brown21');

insert into HPackage values 
(

insert into VIP values 
(

insert into payment values 

insert into invoice values 








