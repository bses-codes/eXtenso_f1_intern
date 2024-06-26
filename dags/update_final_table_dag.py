from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from function_dag import *
from sqlalchemy import create_engine

def update_table():
    df_lengths = retrieve()

    # read the data
    final_df = pd.read_csv('/opt/airflow/datasets/final_table.csv')
    # engine = create_engine("mysql+pymysql://<YOUR_DB_USERNAME>:<YOUR_DB_PASSWORD>@host.docker.internal/<YOUR_DB_NAME>")
    #final_df = pd.read_sql(table_name, engine)

    layout_1, layout_2, layout_3, layout_4, layout_5 = read_data()
    layout_1_c = layout_1.copy().loc[df_lengths['lay1']:]
    layout_2_c = layout_2.copy().loc[df_lengths['lay2']:]
    layout_3_c = layout_3.copy().loc[df_lengths['lay3']:]
    layout_4_c = layout_4.copy().loc[df_lengths['lay4']:]
    layout_5_c = layout_5.copy().loc[df_lengths['lay5']:]

# store the number of row until which data is aggregated
    store(layout_1, layout_2, layout_3, layout_4, layout_5)

    dict_layout = {
        'Customer Code': layout_1_c,
        'Mobile Number': layout_2_c,
        'votersID': layout_3_c,
        'Electricity Bill ID': layout_4_c,
        'License Number': layout_5_c
    }

#append new values to final_df
    new_final_df = add_new_values(final_df, dict_layout)
    if 'index' in new_final_df.columns:
        new_final_df.drop('index', axis=1, inplace=True)
    # new_final_df.to_sql('<YOUR_TABLE_NAME>', engine, if_exists='append', index=False)
    new_final_df.to_csv('/opt/airflow/datasets/final_table.csv', index=False)


default_args = {
    'owner': 'bses',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='dag_update_table',
    default_args=default_args,
    start_date=datetime(2024, 5, 29),
    schedule_interval='@once'
) as dag:
    updated_table = PythonOperator(
        task_id='update_final_table',
        python_callable=update_table
    )

    updated_table