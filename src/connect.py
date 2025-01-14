import psycopg2
from config import config

def connect():
    connection =  None
    try:
        # config function from config file
        params = config()
        print("Connecting to the postgresql database...")
        connection= psycopg2.connect(**params)

        # create cursor
        curs = connection.cursor()
        print('PostgreSQL database version: ')
        curs.execute('SELECT version()')
        db_version = curs.fetchone()
        print(db_version)
        curs.close()
        
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            return connection