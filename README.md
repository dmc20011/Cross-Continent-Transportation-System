# Cross Continent Transportation System

## How to run Docker containers

1. Build the containers:
   ```bash
   docker compose build
   ```

2. Start the application:
   ```bash
   docker compose up
   ```

    open http://localhost:3000 in your browser. The page should load like this: <br>

   <img width="570" height="210" alt="image" src="https://github.com/user-attachments/assets/d70a1744-6914-47bd-a3e8-b920995b1f19" />
   
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
