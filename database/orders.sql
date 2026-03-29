CREATE TABLE orders (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Created DATETIME,
    CustomerInfo JSON,
    Origin VARCHAR(255),
    Destination VARCHAR(255),
    WeightKG DOUBLE,
    VolumeM3 DOUBLE,
    Priority ENUM('Standard', 'Express'),
    PreferredTransportMode ENUM('None', 'Sea', 'Rail', 'Truck', 'Air'),
    Status ENUM('Created', 'Processing', 'Shipped', 'Delivered', 'Cancelled')
);

INSERT INTO orders (ID, Created, CustomerInfo, Origin, Destination, WeightKG, VolumeM3, Priority, PreferredTransportMode, Status) VALUES
(1001, '2023-05-19 08:55:00', '{"name": "Robert Wilson", "email": "robert@example.com"}', 'Toronto', 'Cairo', 22.3, 0.7, 'Standard', 'Rail', 'Created'),
(1002, '2023-06-19 08:55:00', '{"name": "First Smith", "email": "first@example.com"}', 'Toronto', 'Cairo', 22.3, 0.7, 'Standard', 'Rail', 'Created'),
(1003, '2023-07-19 08:55:00', '{"name": "John Last", "email": "john@example.com"}', 'Toronto', 'Cairo', 22.3, 0.7, 'Standard', 'Rail', 'Created');
