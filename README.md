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

| id | created | origin | destination | weight_kg | volume_m3 | customer_info | priority | preferred_transport_mode | status
|-|-|-|-|-|-|-|-|-|-|
| INT AUTO_INCREMENT PRIMARY KEY | DATETIME | VARCHAR(255) | VARCHAR(255) | DOUBLE | DOUBLE | JSON | VARCHAR(50) | VARCHAR(50) | VARCHAR(50)

```sql
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created DATETIME,
    origin VARCHAR(255),
    destination VARCHAR(255),
    weight_kg DOUBLE,
    volume_m3 DOUBLE,
    customer_info JSON,
    priority VARCHAR(50),
    preferred_transport_mode VARCHAR(50),
    status VARCHAR(50)
);
```

### Shipments

| id | created | origin | destination | total_weight_kg | total_volume_m3 | order_ids | priority | preferred_transport_mode | status
|-|-|-|-|-|-|-|-|-|-|
| INT AUTO_INCREMENT PRIMARY KEY | DATETIME | VARCHAR(255) | VARCHAR(255) | DOUBLE | DOUBLE | JSON | VARCHAR(50) | VARCHAR(50) | VARCHAR(50)

```sql
CREATE TABLE shipments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created DATETIME,
    origin VARCHAR(255),
    destination VARCHAR(255),
    total_weight_kg DOUBLE,
    total_volume_m3 DOUBLE,
    order_ids JSON,
    priority VARCHAR(50),
    preferred_transport_mode VARCHAR(50),
    status VARCHAR(50)
);
```
