from sqlalchemy import create_engine
import os


def build_engine_url(credentials):
    template = 'mysql+pymysql://{user}:{password}@{host}:3306/{database}'
    return template.format(**credentials)

def write_dataframe_to_db(url, df, table_name):
    
    engine = create_engine(url)

    with engine.connect().execution_options(autocommit=True) as conn:
        df.to_sql(table_name, engine, if_exists='replace', index=False)    

    engine.dispose()

def load_params_from_env():
    env_variables = dict(os.environ)
    db_user = env_variables.get("DB_USER", '')
    db_pass = env_variables.get("DB_PASSWORD", '')
    db_host = env_variables.get("DB_HOST", '')
    db_database = env_variables.get("DB_NAME", '')
    return dict(user=db_user,password=db_pass, host=db_host, database=db_database)


def load_data(df, table_name):
    credentials = load_params_from_env()
    url = build_engine_url(credentials)

    write_dataframe_to_db(url, df, table_name)    
