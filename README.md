# Cross Continent Transportation System

## How to run Docker containers

```bash
docker compose build # rebuild all containers
docker compose up # create and start all containers
docker compose stop # stop all containers
docker compose start # start all containers
docker compose logs # view container logs
docker compose down # stop and delete all containers
```

## How to run the app
1. in the ui folder, run `npm install` command on terminal/shell
2. run `npm run dev` command on terminal/shell

<img width="376" height="186" alt="image" src="https://github.com/user-attachments/assets/1ef807ad-55b7-49d3-a283-5362ce060189" />

3. goto http://localhost:3000 on any browser. The page should load like this: <br>

<img width="570" height="210" alt="image" src="https://github.com/user-attachments/assets/d70a1744-6914-47bd-a3e8-b920995b1f19" />

5. CTRL+C to stop running the webpage

## Database Schemas

### Orders

```sql
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
```

### Shipments

```sql
CREATE TABLE shipments (
    ShipmentID INT AUTO_INCREMENT PRIMARY KEY,
    Origin VARCHAR(255),
    Destination VARCHAR(255),
    TotalWeightKG DOUBLE,
    TotalVolumnM3 DOUBLE,
    OrderIDs JSON,
    Priority ENUM('Standard', 'Express'),
    PreferredTransportMode ENUM('Sea', 'Rail', 'Truck', 'Air'),
    OrderStatus ENUM('Created', 'Processing', 'Shipped', 'Delivered', 'Cancelled'),
    RouteID: INT
);
```

```sql
CREATE TABLE routes (
    RouteID INT AUTO_INCREMENT PRIMARY KEY,
    Route JSON,
    DistKM INT
);
```

### Tracking

```sql 
CREATE TABLE IF NOT EXISTS User (
    username VARCHAR(255) PRIMARY KEY
);
```

```sql
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
```