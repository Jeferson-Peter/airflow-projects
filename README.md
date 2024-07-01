# Airflow Projects

Welcome to the Airflow Projects repository. This repository contains various projects and workflows created using Apache Airflow. It serves as a learning and experimentation platform for implementing and managing ETL processes with Airflow.

## Table of Contents

- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Using Docker](#using-docker)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

This repository provides several example projects to help you understand how to use Apache Airflow for different data processing tasks. Follow the instructions below to set up your environment and run the projects.

## Prerequisites

- Python 3.7+
- Apache Airflow 2.0+
- Docker

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/python-dev-10/airflow-projects.git
   cd airflow-projects
   ```

2. **Set up a virtual environment:**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use \`venv\\Scripts\\activate\`
   ```

3. **Install the required dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

## Using Docker

Alternatively, you can use Docker to set up and run Airflow. Follow these steps:

1. **Build and run the Docker containers:**

   ```sh
   docker-compose --up d
   ```

2. **Access the Airflow web interface:**

   Open your web browser and navigate to `http://localhost:8080`.

## Usage

1. **Set up your Airflow configuration:**

   Edit the `airflow.cfg` file to configure your Airflow instance according to your needs.

2. **Add your DAGs:**

   Place your DAG files in the `airflow/dags` directory. Airflow will automatically detect and load them.

3. **Run your DAGs:**

   Trigger your DAGs from the Airflow web interface or using the Airflow CLI.

## Project Structure

```
airflow-projects/
├── .venv/
├── airflow/
│   ├── config/
│   ├── dags/
│   │   ├── financial_data.py
│   │   └── forecast_etl.py
│   ├── data/
│   ├── logs/
│   └── plugins/
│       └── email_template.py
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
├── .gitignore
└── README.md
```

- `.venv/`: Virtual environment directory.
- `airflow/`: Main directory for Airflow configurations and components.
  - `config/`: Configuration files for Airflow.
  - `dags/`: Contains all the DAG files.
  - `data/`: Directory for data files.
  - `logs/`: Directory for log files.
  - `plugins/`: Custom plugins for Airflow.
- `docker-compose.yaml`: Docker Compose configuration for running Airflow in containers.
- `Dockerfile`: Dockerfile for building Airflow container.
- `requirements.txt`: List of Python dependencies.


<details>
  <summary><b>DAG: forecast_etl</b></summary>
   <h4>Taks</h4>
   <ul>
      <li><b>Create Table</b>: Creates a table in PostgreSQL if it doesn't exist.</li>
      <li><b>Transform Data</b>: Transforms the extracted data to a format suitable for insertion into the database.</li>
      <li><b>Generate SQL</b>: Generates the SQL insert statement for the transformed data.</li>
      <li><b>Insert Data</b>: Inserts the transformed data into the PostgreSQL table.</li>
   </ul>
   
   <h4>Variables</h4>
   <ul>
      <li><b>open_weather_api</b>: Your OpenWeatherMap API key stored as an Airflow Variable.</li>
      <li><b>city_name</b>: The city for which to fetch the weather data, stored as an Airflow Variable.</li>
   </ul>

   <h4>Airflow Connections</h4>
   <ul>
      <li><b>airflow_postgres_conn</b>: Connection ID for connecting to the PostgreSQL database. This should be configured          in Airflow with the appropriate connection details.</li>
   </ul>

   <h4>Prerequisites</h4>
   <p>To successfully run this DAG, ensure the following prerequisites are met:</p>
   <ul>
      <li>Apache Airflow is installed and configured.</li>
      <li>PostgreSQL database is set up and accessible from Airflow.</li>
      <li>Airflow variables `open_weather_api` and `open_weather_city` are configured.</li>
   </ul>
</details>


