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

1. Build the containers:
   ```bash
   docker compose build
   ```

2. Start the application:
   ```bash
   docker compose up
   ```
   
3. To stop the containers:
   ```bash
   docker compose stop
   ```
   
4. To start them again:
   ```bash
   docker compose start
   ```
5. To view logs:
   ```bash
   docker compose logs
   ```

6. To remove containers, networks, and related resources:
   ```bash
   docker compose down
   ```

7. After starting the containers, open http://localhost:3000 in your browser. The page should load like this: <br>

<img width="570" height="210" alt="image" src="https://github.com/user-attachments/assets/d70a1744-6914-47bd-a3e8-b920995b1f19" />
