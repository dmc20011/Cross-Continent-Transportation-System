CREATE TABLE orders (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Created DATETIME,
    Username VARCHAR(255),
    Origin VARCHAR(255),
    Destination VARCHAR(255),
    WeightKG DOUBLE,
    VolumeM3 DOUBLE,
    Priority ENUM('Standard', 'Express'),
    PreferredTransportMode ENUM('None', 'Sea', 'Rail', 'Truck', 'Air'),
    Status ENUM('Created', 'Processing', 'Shipped', 'Delivered', 'Cancelled')
);

INSERT INTO orders (created, customer_info, origin, destination, weight_kg, volume_m3, priority, preferred_transport_mode, status) VALUES
('2023-05-15 09:30:00', 'JohnSmith', 'Toronto', 'Shanghai', 25.5, 0.8, 'Express', 'Sea', 'Created'),
('2023-05-16 14:45:00', 'SarahJohnson', 'Cairo', 'Shanghai', 15.2, 0.5, 'Standard', 'Truck', 'Processing'),
('2023-05-17 11:20:00', 'MichaelBrown', 'Berlin', 'Houston', 30.0, 1.2, 'Express', 'Rail', 'Shipped'),
('2023-05-18 16:10:00', 'EmilyDavis', 'Cairo', 'Sydney', 8.7, 0.3, 'Standard', 'Truck', 'Delivered'),
('2023-05-19 08:55:00', 'Robert Wilson', 'Mumbai', 'Rio de Janeiro', 22.3, 0.7, 'Standard', 'Air', 'Created');
