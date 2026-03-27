CREATE TABLE IF NOT EXISTS User (
    username VARCHAR(255) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Tracking (
    username VARCHAR(255),
    orderNumber VARCHAR(255),
    parentNumber VARCHAR(255),
    orderDate DATE,
    lastUpdate DATE,
    startLocation VARCHAR(255),
    currentLocation VARCHAR(255),
    targetLocation VARCHAR(255),
    distKM INT,
    transportMethod ENUM('Sea', 'Rail', 'Truck', 'Air'),
    deliveryEstimateEarly DATE,
    deliveryEstimateLate DATE,
    orderStatus ENUM('Created', 'Processing', 'Shipped', 'Delivered', 'Cancelled'),
    
    PRIMARY KEY (username, orderNumber),
    FOREIGN KEY (username) REFERENCES User(username)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

INSERT INTO User (username) VALUES
('alpha'),
('beta'),
('gamma');

INSERT INTO Tracking (
    username, orderNumber, parentNumber, orderDate, lastUpdate,
    startLocation, currentLocation, targetLocation, distKM,
    transportMethod, deliveryEstimateEarly, deliveryEstimateLate, orderStatus
) VALUES
('alpha', 'ORD001', 'AB1', '2026-03-01', '2026-03-02', 'Toronto', 'Ottawa', 'Montreal', 450, 'Truck', '2026-03-05', '2026-03-07', 'Shipped'),
('beta', 'ORD002', 'AB2', '2026-03-03', '2026-03-04', 'Vancouver', 'Calgary', 'Winnipeg', 1200, 'Rail', '2026-03-08', '2026-03-10', 'Processing'),
('gamma', 'ORD003', 'AB3', '2026-03-05', '2026-03-06', 'Halifax', 'Toronto', 'Chicago', 1800, 'Air', '2026-03-07', '2026-03-08', 'Delivered');