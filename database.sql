DROP TABLE IF EXISTS bookings;
CREATE TABLE `bookings` (
  `idBooking` int NOT NULL AUTO_INCREMENT,
  `deptDate` datetime NOT NULL,
  `arrivDate` datetime NOT NULL,
  `idRoutes` int NOT NULL,
  `noOfSeats` int NOT NULL DEFAULT '1',
  `totFare` int NOT NULL,
  `classes` varchar(10) NOT NULL,
  PRIMARY KEY (`idBooking`),
  KEY `idRoutes` (`idRoutes`),
  CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`idRoutes`) REFERENCES `routes` (`idRoutes`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS routes;
CREATE TABLE `routes` (
  `idRoutes` int NOT NULL,
  `deptCity` varchar(45) NOT NULL,
  `deptTime` varchar(5) NOT NULL,
  `arrivCity` varchar(45) NOT NULL,
  `arrivTime` varchar(45) NOT NULL,
  `stFare` double NOT NULL,
  `classes` varchar(10) NOT NULL,
  PRIMARY KEY (`idRoutes`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS users;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(64) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(128) DEFAULT NULL,
  `usertype` varchar(8) DEFAULT 'standard',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;




