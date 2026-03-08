CREATE TABLE Tracking(
    username VARCHAR(255),
    orderNumber VARCHAR(255),
    parentNumber VARCHAR(255),
    distKM INT,
    transportMethod INT CHECK (transportMethod BETWEEN 0 AND 3),
    estimateDays INT,
    PRIMARY KEY (username, orderNumber)
);

INSERT INTO Tracking (username, orderNumber, parentNumber, distKM, transportMethod, estimateDays) VALUES
('Alpha',   'A1001', 'P9001', 120, 1, 2),
('Alpha',   'A1002', 'A1001', 350, 2, 5),
('Alpha',   'A1003', 'A1002', 90,  0, 1),

('Bravo',   'B2001', 'P9002', 500, 3, 7),
('Bravo',   'B2002', 'B2001', 150, 1, 2),

('Charlie', 'C3001', 'P9003', 60,  0, 1),

('Delta',   'D4001', 'P9004', 800, 2, 10);