from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.models import Variable
from email_template import notify_email, success_email
from datetime import datetime, timedelta
import requests
import logging

DAG_DOC_MD = """
### ETL Pipeline DAG
This DAG performs the following tasks:

1. **Create Table**: Creates a table in PostgreSQL if it doesn't exist.
2. **Extract Data**: Fetches weather data from the OpenWeatherMap API.
3. **Transform Data**: Transforms the extracted data to a format suitable for insertion into the database.
4. **Generate SQL**: Generates the SQL insert statement for the transformed data.
5. **Insert Data**: Inserts the transformed data into the PostgreSQL table.

#### Variables:
- `open_weather_api`: Your OpenWeatherMap API key stored as an Airflow Variable.
- `city_name`: The city for which to fetch the weather data, stored as an Airflow Variable.

#### Author:
- Jeferson Peter
"""

default_args = {
    'owner': 'jefersonp',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 29),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def extract_data(**kwargs):
    """
    #### Extract Data
    Fetches weather data from the OpenWeatherMap API for the specified city.
    The city and API key are stored as Airflow Variables.
    """
    try:
        city = Variable.get('open_weather_city')
        api_key = Variable.get('open_weather_api')
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        logging.info("Data extracted successfully")
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        raise


def transform_data(**kwargs):
    """
    #### Transform Data
    Transforms the extracted data to a format suitable for insertion into the database.
    """
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='extract')
    if not data:
        raise ValueError("No data to transform")

    city_forecast = {
        'city_name': data.get('name'),
        'wind_speed': data.get('wind', {}).get('speed'),
        'weather': data.get('weather', [{}])[0].get('description'),
        'sunrise': datetime.fromtimestamp(data.get('sys', {}).get('sunrise')).isoformat() if data.get('sys', {}).get(
            'sunrise') else None,
        'sunset': datetime.fromtimestamp(data.get('sys', {}).get('sunset')).isoformat() if data.get('sys', {}).get(
            'sunset') else None,
        'humidity': data.get('main', {}).get('humidity'),
        'temp': data.get('main', {}).get('temp'),
        'created_at': datetime.fromtimestamp(data.get('dt')).isoformat() if data.get('dt') else None,
    }

    logging.info("Data transformed successfully")
    ti.xcom_push(key='city_forecast', value=city_forecast)
    return city_forecast


def generate_insert_sql(**kwargs):
    """
    #### Generate SQL
    Generates the SQL insert statement for the transformed data.
    """
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='transform', key='city_forecast')
    if not data:
        raise ValueError("No data to generate SQL")

    sql = f"""
    INSERT INTO weather_data (city_name, wind_speed, weather, sunrise, sunset, humidity, temp, created_at)
    VALUES ('{data['city_name']}', {data['wind_speed']}, '{data['weather']}', '{data['sunrise']}', '{data['sunset']}',
     {data['humidity']}, {data['temp']}, '{data['created_at']}');
    """

    logging.info("SQL generated successfully")
    ti.xcom_push(key='sql_query', value=sql)
    return sql


with DAG(
        'forecast_etl',
        default_args=default_args,
        description='A simple Forecast ETL Pipeline',
        schedule_interval=timedelta(days=1),
        catchup=False,
        default_view='graph',
        doc_md=DAG_DOC_MD,
        on_failure_callback=notify_email,
        on_success_callback=success_email
) as dag:
    create_forecast_table_task = PostgresOperator(
        postgres_conn_id='airflow_postgres_conn',
        task_id='create_forecast_table',
        sql="""
        CREATE TABLE IF NOT EXISTS weather_data (
            id SERIAL PRIMARY KEY,
            city_name VARCHAR(100),
            wind_speed FLOAT,
            weather VARCHAR(50),
            sunrise TIMESTAMP,
            sunset TIMESTAMP,
            humidity INT,
            temp FLOAT,
            created_at TIMESTAMP
        );
        """,
        doc_md="""
        #### Create Table
        This task creates the `weather_data` table in the PostgreSQL database if it doesn't already exist.
        The table schema includes columns for city name, wind speed, weather description, sunrise and sunset times,
        humidity, temperature, and the timestamp when the data was created.
        """
    )

    extract_task = PythonOperator(
        task_id='extract',
        python_callable=extract_data,
        provide_context=True,
        doc_md="""
        #### Extract Data
        This task fetches weather data from the OpenWeatherMap API for the specified city.
        The city and API key are stored as Airflow Variables.
        """
    )

    transform_task = PythonOperator(
        task_id='transform',
        python_callable=transform_data,
        provide_context=True,
        doc_md="""
        #### Transform Data
        This task transforms the extracted data to a format suitable for insertion into the database.
        It extracts relevant fields such as city name, wind speed, weather description, sunrise and sunset times,
        humidity, temperature, and the timestamp when the data was created.
        The transformed data is then pushed to XCom for downstream tasks to use.
        """
    )

    generate_sql_task = PythonOperator(
        task_id='generate_sql',
        python_callable=generate_insert_sql,
        provide_context=True,
        doc_md="""
        #### Generate SQL
        This task generates the SQL insert statement for the transformed data.
        It retrieves the transformed data from XCom and constructs an SQL `INSERT` statement.
        The SQL statement is then pushed to XCom for the insertion task to use.
        """
    )

    insert_forecast_data = PostgresOperator(
        postgres_conn_id='airflow_postgres_conn',
        task_id='insert_forecast_data',
        sql="{{ task_instance.xcom_pull(task_ids='generate_sql', key='sql_query') }}",
        doc_md="""
        #### Insert Data
        This task inserts the transformed data into the `weather_data` table in the PostgreSQL database.
        It retrieves the SQL `INSERT` statement generated by the previous task from XCom and executes it.
        """
    )

    create_forecast_table_task >> extract_task >> transform_task >> generate_sql_task >> insert_forecast_data
