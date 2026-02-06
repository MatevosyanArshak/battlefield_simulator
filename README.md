# Battlefield Simulation Service

This is a backend service that simulates and monitors a battlefield scenario.

## Running the Service

### With Docker Compose (Recommended)

This is the easiest way to run the service for local development.

1.  **Build and run the container:**

    ```bash
    docker-compose up
    ```

    The service will be available at `http://localhost:8000`. Any changes you make to the code will be automatically reloaded.

### With a Bash Script

You can also use the provided `run.sh` script to build and run the service.

1.  **Build and run the Docker container:**

    ```bash
    bash run.sh
    ```

## API and Swagger

The simulation is controlled via a set of API endpoints. A Swagger UI is available for exploring and interacting with the API at:

[http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)

### API Endpoints

#### 1. Add Countries

Add two or more countries to the battlefield before starting the simulation.

*   **URL:** `/api/countries`
*   **Method:** `POST`
*   **Body:**

    ```json
    {
        "name": "string",
        "soldiers": "integer (1-10)",
        "tanks": "integer (0-3)"
    }
    ```

#### 2. Start the Simulation

*   **URL:** `/api/start`
*   **Method:** `POST`
*   **Description:** Starts the simulation. Requires at least two countries on the battlefield.

#### 3. Query Battle State

*   **URL:** `/api/state`
*   **Method:** `GET`
*   **Description:** Returns the current state of the battle, including active countries and their remaining units.

#### 4. Stop the Simulation

*   **URL:** `/api/stop`
*   **Method:** `POST`
*   **Description:** Pauses the simulation, freezing the battlefield in its current state.

#### 5. Restart the Simulation

*   **URL:** `/api/restart`
*   **Method:** `POST`
*   **Description:** Stops the simulation and clears the battlefield of all countries and units.

## Console Output

When the simulation is running, a grid representing the battlefield will be printed to the console every second.

*   `s` represents a soldier
*   `t` represents a tank
*   The number following the letter is the unique ID of the country.

A legend is provided below the grid to map country names to their IDs.

## Design Notes

*   **In-Memory State:** The battlefield state is stored in memory and will be reset if the server is restarted.
*   **Concurrency:** The simulation runs in a background thread, and a lock is used to ensure thread-safe access to the game state.
*   **API:** The service is built with Django and Django Rest Framework, with a Swagger UI for API documentation and interaction.
*   **Containerization:** The application is containerized with Docker for easy and consistent deployment.
