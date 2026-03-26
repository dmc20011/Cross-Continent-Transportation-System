CREATE TABLE shipments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created DATETIME,
    origin VARCHAR(255),
    destination VARCHAR(255),
    total_weight_kg DOUBLE,
    total_volume_m3 DOUBLE,
    order_ids JSON,
    priority ENUM('Standard', 'Express'),
    preferred_transport_mode ENUM('Air', 'Truck', 'Rail', 'Sea'),
    status ENUM('Created', 'Processing', 'Shipped', 'Delivered', 'Cancelled')
);