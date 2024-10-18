Use Myweb; 

DROP TABLE IF EXISTS routes; 
DROP TABLE IF EXISTS cancelation; 

CREATE TABLE routes (
  idRoutes INT NOT NULL, 
  deptCity VARCHAR(45) NOT NULL, 
  deptTime VARCHAR(5) NOT NULL, 
  arrivCity VARCHAR(45) NOT NULL, 
  arrivTime VARCHAR(45) NOT NULL, 
  stFare double NOT NULL,
  classes VARCHAR (10) NOT  NULL,
  PRIMARY KEY (idRoutes)); 
  
  DELETE from routes;
  
  INSERT INTO routes VALUES 
  (1000, 'Dundee', '10:00', 'Portsmouth', '12:00', 100.00,'Economy'),
  (1001, 'Dundee', '10:00', 'Portsmouth', '12:00', 200.00,'Business'),
  (1002, 'Portsmouth', '12:00', 'Dundee', '14:00', 100.00,'economy'),
  (1003, 'Portsmouth', '12:00', 'Dundee', '14:00', 200.00,'Business'), 
  (1004, 'Bristol', '11:30', 'Manchester', '12:30', 60.00,'economy'),
  (1005, 'Bristol', '11:30', 'Manchester', '12:30', 120.00,'Business'), 
  (1006, 'Manchester', '12:20', 'Bristol', '13:20', 60.00,'economy'),
  (1007, 'Manchester', '12:20', 'Bristol', '13:20', 120.00,'Business'),
  (1008, 'Bristol', '06:20', 'Manchester', '07:20', 60.00,'economy'),
  (1009, 'Bristol', '06:20', 'Manchester', '07:20', 1200.00,'Business'),
  (1010, 'Manchester', '18:25', 'Bristol', '19:30', 60.00,'economy'),
  (1011, 'Manchester', '18:25', 'Bristol', '19:30', 120.00,'Business'), 
  (1012, 'Bristol', '08:00', 'Newcastle', '09:15', 80.00,'economy'), 
  (1013, 'Bristol', '08:00', 'Newcastle', '09:15', 1600.00,'Business'),  
  (1014, 'Newcastle', '16:45', 'Bristol', '18:00', 80.00,'economy'),
  (1015, 'Newcastle', '16:45', 'Bristol', '18:00', 1600.00,'Business'), 
  (1016, 'Bristol', '07:40', 'Glasgow', '08:45', 90.00,'economy'), 
  (1017, 'Bristol', '07:40', 'Glasgow', '08:45', 1800.00,'Business'), 
  (1018, 'Bristol', '07:40', 'London', '08:20', 60.00,'economy'), 
  (1019, 'Bristol', '07:40', 'London', '08:20', 120.00,'Business'), 
  (1020, 'Southampton', '12:00', 'Manchester', '13:30', 70.00,'economy'), 
  (1021, 'Southampton', '12:00', 'Manchester', '13:30', 140.00,'Business'), 
  (1022, 'Manchester', '19:00', 'Southampton', '20:30', 70.00,'economy'), 
  (1023, 'Manchester', '19:00', 'Southampton', '20:30', 1400.00,'Business'),  
  (1024, 'Cardiff', '06:00', 'Edinburgh', '07:30', 80.00,'economy'), 
  (1025, 'Cardiff', '06:00', 'Edinburgh', '07:30', 160.00,'Business'), 
  (1026, 'Edinburgh', '18:30', 'Cardiff', '20:00', 80.00,'economy'), 
  (1027, 'Edinburgh', '18:30', 'Cardiff', '20:00', 160.00,'Business'), 
  (1028, 'London', '11:00', 'Manchester', '12:20', 75.00,'economy'),
  (1029, 'London', '11:00', 'Manchester', '12:20', 150.00,'Business'),
  (1030, 'Manchester', '12:20', 'Glasgow', '13:30', 75.00,'economy'),
  (1031, 'Manchester', '12:20', 'Glasgow', '13:30', 150.00,'Business'),
  (1032, 'Glasgow', '14:30', 'Newcastle', '15:45', 75.00,'economy'),
  (1033, 'Glasgow', '14:30', 'Newcastle', '15:45', 150.00,'Business'),
  (1034, 'Newcastle', '16:15', 'Manchester', '17:05', 75.00,'economy'),
  (1035, 'Newcastle', '16:15', 'Manchester', '17:05', 150.00,'Business'),
  (1036, 'Birmingham', '16:00', 'Newcastle','17:30', 75.00,'economy'),
  (1037, 'Birmingham', '16:00', 'Newcastle','17:30', 150.00,'Business'),
  (1038, 'Newcastle', '06:00', 'Birmingham', '07:30', 75.00,'economy'),
  (1039, 'Newcastle', '06:00', 'Birmingham', '07:30', 150.00,'Business'),
  (1040, 'Aberdeen', '07:00', 'Portsmouth', '09:00', 75.00,'economy'),
  (1041, 'Aberdeen', '07:00', 'Portsmouth', '09:00', 150.00,'Business');
  
  select * from routes; 
  
  CREATE TABLE bookings (
  idBooking INT NOT NULL auto_increment, 
  deptDate  datetime NOT NULL,   
  arrivDate datetime NOT NULL, 
  idRoutes INT NOT NULL,  
  noOfSeats INT NOT NULL default 1, 
  totFare INT  NOT NULL,  
  classes VARCHAR (10) NOT NULL,
 FOREIGN KEY (idRoutes) REFERENCES routes (idRoutes), 
 PRIMARY KEY (idBooking)
    ); 
    
  select * from bookings; 
  delete from bookings; 