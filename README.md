# Weekend Data Engineering Project: Security Log ELT Pipeline

This project simulates a simplified security log data pipeline designed for local execution on your machine. It demonstrates core data engineering concepts by ingesting raw security logs, processing them through an ETL (Extract, Transform, Load) stage into a transactional database (OLTP), and then performing an ELT (Extract, Load, Transform) process to an analytical data warehouse (OLAP).

## 1. Project Summary & Learning Outcomes

**Purpose:**
* **Practical Application:** Gain hands-on experience building a end-to-end data pipeline.
* **Core Concepts:** Understand and implement ETL and ELT methodologies.
* **Database Architectures:** Differentiate and apply OLTP (Online Transactional Processing) and OLAP (Online Analytical Processing) database concepts.
* **Modern Python Tooling:** Utilize FastAPI for API development, `uv` for dependency management, and `ruff` for code linting.
* **Containerization:** Learn basic Docker for deploying services.
* **Data Modeling:** Implement a basic star schema for analytical queries.

**What You Will Learn:**
* How to design and implement simple data ingestion APIs.
* How to manage Python project dependencies efficiently with `uv`.
* Best practices for code quality using `ruff`.
* The difference between transactional (OLTP) and analytical (OLAP) database usage.
* Techniques for transforming raw data into a structured dimensional model.
* Basic containerization with Docker.
* Setting up a local development environment for data engineering projects.

## 2. Architecture Overview

The pipeline consists of several interconnected components, orchestrated using Docker Compose for a local development environment.

**Conceptual Data Flow:**

The project simulates a security log data pipeline. It involves ingesting raw security logs, performing an ETL process to a transactional database (OLTP), and then an ELT process to an analytical data warehouse (OLAP).

* **Ingestion (ETL - Extract, Transform, Load)**: Raw security logs are generated and sent to a `Log Ingestor` (a FastAPI application). This ingestor then loads the raw logs directly into a `PostgreSQL` database (acting as the OLTP).

* **ELT (Extract, Load, Transform)**:

  * **Extract & Load**: A `Data Transformer` script extracts raw data from the `PostgreSQL` OLTP database. It then loads this raw data into `DuckDB` (acting as the OLAP).

  * **Transform**: The transformation into a dimensional model (star schema) occurs within `DuckDB`. This involves processing the raw data, cleaning it, and enriching it.

* **Analysis**: A `Security Analyzer` script connects to the `DuckDB` OLAP database to perform analytical queries and generate insigßhts.

```
+-----------------+     +-----------------+     +-----------------+
| Security Logs   | --> | Log Ingestor    | --> | PostgreSQL      |
| (Raw Data)      |     | (FastAPI App)   |     | (OLTP)          |
+-----------------+     +-----------------+     +-----------------+
                                    |
                                    | ETL (E & L)
                                    v
+-----------------+     +-----------------+     +-----------------+
| Data Extractor  | --> | Data Transformer| --> | DuckDB          |
| (Python Script) |     | (Python Script) |     | (OLAP)          |
+-----------------+     +-----------------+     +-----------------+
        ^                                 |
        | ELT (E & L)                     | ELT (T)
        |                                 v
        +---------------------------------+
        |
        v
+-----------------+
| Security Analyzer|
| (Python Script) |
+-----------------+
```

## 3. Project Components

These are the main components for this project:
```
<project root>/
├── data/
│   ├── logs_oltp.db      # SQLite database for OLTP (raw ingested logs) 
│   └── logs_olap.duckdb  # DuckDB database for OLAP (transformed dimensional data) 
├── src/
│   ├── log_generator.py  # Simulates log creation and sending 
│   ├── log_ingestor.py   # FastAPI for E & L (to OLTP staging) 
│   ├── data_transformer.py # ELT logic: T & L (to OLAP dimensional model) 
│   ├── security_analyzer.py # Analysis script from OLAP
│   └── utils.py          # Helper functions (database connections, schema creation)
├── Dockerfile            # For containerizing the log_ingestor
├── requirements.txt      # Python dependencies
├── .ruff.toml            # Ruff linter configuration
└── README.md             # Project description (this document)
```

## 4. Local Setup

### Prerequisites

* Docker Desktop (includes Docker Engine and Docker Compose)
* Python 3.9+
* `uv` (recommended for dependency management): `pip install uv`
* `ruff` (for linting): `pip install ruff`

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd weekend-data-engineering-project
    ```

2.  **Build and run Docker containers:**
    ```bash
    docker compose up --build -d
    ```
    This will:
    * Build the Docker image for the `log_ingestor` FastAPI application.
    * Start the PostgreSQL database container.
    * Start the FastAPI application.

3.  **Initialize Databases:**
    * The `docker-compose.yml` should handle initial database setup via entrypoint scripts or volumes. Verify that the necessary tables in PostgreSQL are created.

## 5. How to Run the Pipeline

Once the Docker containers are up and running:

1.  **Ingest Sample Logs (via FastAPI):**
    You can use `curl` or a tool like Postman/Insomnia to send sample security logs to your FastAPI endpoint.
    The FastAPI app will be accessible at `http://localhost:8000`.

    Example `curl` command to send a log:
    ```bash
    curl -X POST -H "Content-Type: application/json" \
    -d '{
        "timestamp": "2024-05-25T10:30:00Z",
        "event_type": "login_attempt",
        "user_id": "user123",
        "ip_address": "192.168.1.10",
        "status": "success",
        "details": {"device": "laptop", "browser": "chrome"}
    }' http://localhost:8000/logs
    ```
    (Adjust the endpoint if your FastAPI app exposes a different path, e.g., `/ingest`).

2.  **Run the ELT Pipeline (Data Extraction and Transformation):**
    Execute the Python scripts to extract, transform, and load data into DuckDB. You'll typically run these from your host machine or within a dedicated data processing container (though for a weekend project, running locally is fine).

    ```bash
    # Assuming you are in the project root directory
    # Navigate to the data_pipeline directory
    cd data_pipeline

    # Ensure dependencies are installed for the pipeline scripts
    uv sync

    # Run the data extraction and transformation (which loads into DuckDB)
    python data_extractor.py
    python data_transformer.py
    ```

3.  **Perform Analytical Queries (using `security_analyzer.py`):**
    After the data is loaded into DuckDB, you can run the analytical script.

    ```bash
    # From within the data_pipeline directory
    python security_analyzer.py
    ```
    This script will connect to your DuckDB database (e.g., `logs_olap.duckdb`) and print analytical insights.

## 6. Project Structure

The project is organized into the following key directories and files:

* `.` (Project Root)
    * `log_ingestor/`: Contains the FastAPI application for ingesting logs.
    * `data_pipeline/`: Holds scripts for data extraction, transformation, and analysis.
    * `db/`: Stores SQL scripts for database initialization.
    * `docker-compose.yml`: Defines the Docker services for the project.
    * `.gitignore`: Git ignore file.
    * `README.md`: This documentation.
    * `logs_olap.duckdb`: The local DuckDB database file.

## 7. Next Steps & Enhancements

This project provides a solid foundation. Here are some ideas for extending it:

* **Real-time Processing with Kafka & Spark:**
    * Integrate Apache Kafka as a message broker between the `log_ingestor` and a new Spark Structured Streaming application.
    * Use Spark to consume logs from Kafka, perform real-time transformations, and stream data into a data lake (e.g., Parquet/Delta Lake).
* **Cloud Integration:**
    * Replace local PostgreSQL and DuckDB with cloud services (e.g., Amazon RDS/PostgreSQL, Amazon S3 for data lake, Snowflake/Google BigQuery/Amazon Redshift for data warehouse).
* **Deployment & Operations:**
    * **Kubernetes (Conceptual):** Define Kubernetes YAML manifests for your `log_ingestor` deployment and service for orchestration at scale. (Note: This is a significant learning curve for a weekend).
    * **CI/CD Pipeline:** Implement a basic CI/CD pipeline (e.g., using GitHub Actions) to automatically lint, test, build Docker images, and (conceptually) deploy your services.
* **Advanced Analytics:**
    * **Machine Learning Integration:** Use libraries like `scikit-learn` (or Spark ML if you incorporate Spark) within `security_analyzer.py` to build simple anomaly detection models (e.g., flagging unusual login patterns).
    * **Dashboards:** Build a simple web dashboard using Streamlit or Dash to visualize the analyzed security events from DuckDB.

## 8. Contributing

Feel free to fork this repository, make improvements, and submit pull requests.

## 9. License

This project is open-source and available under the [MIT License](LICENSE).