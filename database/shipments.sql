CREATE TABLE shipments (
    ShipmentID INT AUTO_INCREMENT PRIMARY KEY,
    Created DATETIME,
    Origin VARCHAR(255),
    Destination VARCHAR(255),
    TotalWeightKG DOUBLE,
    TotalVolumnM3 DOUBLE,
    OrderIDs JSON,
    Priority ENUM('Standard', 'Express'),
    PreferredTransportMode ENUM('Sea', 'Rail', 'Truck', 'Air'),
    OrderStatus ENUM('Created', 'Processing', 'Shipped', 'Delivered', 'Cancelled'),
    RouteID: INT FOREIGN KEY REFERENCES routes(RouteID)
);

CREATE TABLE routes (
    RouteID INT AUTO_INCREMENT PRIMARY KEY,
    Route JSON,
    DistKM INT
);

INSERT INTO shipments (Created, Origin, Destination, TotalWeightKG, TotalVolumnM3, OrderIDs, Priority, PreferredTransportMode, OrderStatus, RouteID) VALUES
('2026-02-15 09:30:00', 'Berlin', 'Shanghai', 25.5, 0.8, '{}', 'Standard', 'None', 'Created', NULL),
('2026-02-19 09:30:00', 'Berlin', 'Shanghai', 18.7, 0.3, '{}', 'Standard', 'Air', 'Created', NULL);
('2026-02-22 09:30:00', 'Berlin', 'Shanghai', 22.3, 0.7, '{}', 'Express', 'None', 'Created', NULL);
('2026-02-28 09:30:00', 'Berlin', 'Shanghai', 36.3, 1.1, '{}', 'Express', 'Truck', 'Created', NULL);
