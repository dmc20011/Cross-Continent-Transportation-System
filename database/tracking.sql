CREATE TABLE Tracking(
    username VARCHAR(255),
    orderNumber VARCHAR(255),
    parentNumber VARCHAR(255),
    orderDate DATE,
    lastUpdate DATE,
    startLocation VARCHAR(255),
    currentLocation VARCHAR(255),
    targetLocaiton VARCHAR(255),
    distKM INT,
    transportMethod ENUM('Sea', 'Rail', 'Truck', 'Air'),
    deliveryEstimateEarly Date,
    deliveryEstimateLate Date,
    orderStatus ENUM('Created', 'Processing', 'Shipped', 'Delivered', 'Cancelled')
    PRIMARY KEY (username, orderNumber)
    FOREIGN KEY (username) REFERENCES User(username)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

Create TABLE User(
    username VARCHAR(255)
);

INSERT INTO Tracking (username, orderNumber, parentNumber, orderDate, lastUpdate, startLocation, currentLocation, targetLocaiton,
distKM, transportMethod, deliveryEstimateEarly, deliveryEstimateLate, orderStatus) VALUES
INSERT INTO Tracking VALUES
('Alice','A100','P10','2026-03-01','2026-03-01','Canada','Canada','United States',800,2,4),
('Alice','A101','P10','2026-03-02','2026-03-02','China','China','Japan',2100,0,8),
('Alice','A102','P11','2026-03-03','2026-03-03','China','China','United States',11000,3,2),

('Bob','B200','P20','2026-03-01','2026-03-01','Germany','Germany','France',900,1,3),
('Bob','B201','P21','2026-03-04','2026-03-04','United States','United States','Canada',700,2,2),

('Charlie','C300','P30','2026-03-02','2026-03-02','Japan','China','Australia',7800,3,3),

('Dale','D400','P40','2026-03-03','2026-03-03','Brazil','Mexico','United States',7500,0,12);