CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created DATETIME,
    origin VARCHAR(255),
    destination VARCHAR(255),
    dist_km INT,
    weight_kg DOUBLE,
    volume_m3 DOUBLE,
    customer_info JSON,
    priority ENUM('Standard', 'Express'),
    preferred_transport_mode ENUM('Sea', 'Rail', 'Truck', 'Air'),
    status ENUM('Created', 'Processing', 'Shipped', 'Delivered', 'Cancelled')
);

INSERT INTO orders (created, customer_info, origin, destination, weight_kg, volume_m3, priority, preferred_transport_mode, status) VALUES
('2023-05-15 09:30:00', '{"name": "John Smith", "email": "john@example.com"}', 'New York', 'Los Angeles', 25.5, 0.8, 'Express', 'Sea', 'Created'),
('2023-05-16 14:45:00', '{"name": "Sarah Johnson", "email": "sarah@example.com"}', 'Chicago', 'Miami', 15.2, 0.5, 'Standard', 'Truck', 'Processing'),
('2023-05-17 11:20:00', '{"name": "Michael Brown", "email": "michael@example.com"}', 'Seattle', 'Denver', 30.0, 1.2, 'Express', 'Rail', 'Shipped'),
('2023-05-18 16:10:00', '{"name": "Emily Davis", "email": "emily@example.com"}', 'Boston', 'Atlanta', 8.7, 0.3, 'Standard', 'Truck', 'Delivered'),
('2023-05-19 08:55:00', '{"name": "Robert Wilson", "email": "robert@example.com"}', 'Houston', 'Phoenix', 22.3, 0.7, 'Standard', 'Air', 'Created');
