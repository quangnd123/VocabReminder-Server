## Getting Started

There are two ways to run this project: using Docker Compose (recommended) or manually.

### Method 1: Docker Compose (Not recommended! Image consists of 20GB)

This method simplifies the setup by using Docker to manage the necessary services.

**Prerequisites:**

* Docker

**Running the Project:**

1.  Clone this repository to your local machine.
2.  Open a terminal in the project's root directory (the directory containing the `docker-compose.yml` file).
3.  Run the following command:

    ```bash
    docker compose up -d
    ```

    * The `-d` flag runs the services in detached mode (in the background).

### Method 2: Manual Setup (Recommended)

This method involves setting up the environment and running the services manually.

**Prerequisites:**

* uv: https://docs.astral.sh/uv/getting-started/installation/
* Docker
* Postgreql DB

**Setup and Running the Project:**

1.  Clone this repository to your local machine.
2.  Open a terminal in the project's root directory.

3.  **Step 1: Synchronize virtual environment (if using uv):**
    ```bash
    uv python install 3.12 && \
    uv sync
    ```
    
4.  **Step 2: Download SpaCy models:**
    ```bash
    uv run --with spacy python -m spacy download en_core_web_sm && \
    uv run --with spacy python -m spacy download xx_sent_ud_sm
    ```

5.  **Step 3: Run Qdrant:**

    Open a new terminal window or tab in the project's root directory.  Run Qdrant using Docker:

    ```bash
    docker run -p 6333:6333 -p 6334:6334 -v "$(pwd)/qdrant_db/qdrant_storage:/qdrant/storage:z" qdrant/qdrant
    ```
    * This command runs a Qdrant container, mapping ports 6333 and 6334 and mounting a local volume for data persistence.  The data will be stored in the `qdrant_storage` directory within your project directory.
    * Leave this terminal window running. Qdrant must be running for the server to function.

6.  **Step 4: Run the server:**

    Return to the original terminal window and run the server:

    ```bash
    uv run ./server/server.py
    ```
