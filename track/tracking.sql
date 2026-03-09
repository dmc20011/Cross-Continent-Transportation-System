CREATE TABLE Tracking(
    username VARCHAR(255),
    orderNumber VARCHAR(255),
    parentNumber VARCHAR(255),
    orderDate DATE,
    currentLocation VARCHAR(255),
    targetLocaiton VARCHAR(255),
    distKM INT,
    transportMethod INT CHECK (transportMethod BETWEEN 0 AND 3),
    estimateDays INT,
    PRIMARY KEY (username, orderNumber)
);

INSERT INTO Tracking (username, orderNumber, parentNumber, distKM, transportMethod, estimateDays) VALUES
INSERT INTO Tracking VALUES
('Alice','A100','P10','2026-03-01','Canada','United States',800,2,4),
('Alice','A101','P10','2026-03-02','China','Japan',2100,0,8),
('Alice','A102','P11','2026-03-03','China','United States',11000,3,2),

('Bob','B200','P20','2026-03-01','Germany','France',900,1,3),
('Bob','B201','P21','2026-03-04','United States','Canada',700,2,2),

('Charlie','C300','P30','2026-03-02','Japan','Australia',7800,3,3),

('Dale','D400','P40','2026-03-03','Brazil','United States',7500,0,12);