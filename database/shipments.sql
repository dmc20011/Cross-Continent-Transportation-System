CREATE TABLE routes (
    RouteID INT AUTO_INCREMENT PRIMARY KEY,
    Route JSON,
    DistKM INT
);

CREATE TABLE shipments (
    ShipmentID INT AUTO_INCREMENT PRIMARY KEY,
    Origin VARCHAR(255),
    Destination VARCHAR(255),
    TotalWeightKG DOUBLE,
    TotalVolumnM3 DOUBLE,
    OrderIDs JSON,
    Priority ENUM('Standard', 'Express'),
    PreferredTransportMode ENUM('None', 'Sea', 'Rail', 'Truck', 'Air'),
    OrderStatus ENUM('Created', 'Processing', 'Shipped', 'Delivered', 'Cancelled'),
    RouteID INT,
    FOREIGN KEY (RouteID) REFERENCES routes(RouteID)
);

-- INSERT INTO shipments (Origin, Destination, TotalWeightKG, TotalVolumnM3, OrderIDs, Priority, PreferredTransportMode, OrderStatus, RouteID) VALUES
-- ('Berlin', 'Shanghai', 36.3, 1.1, '{}', 'Express', 'Truck', 'Created', NULL);
