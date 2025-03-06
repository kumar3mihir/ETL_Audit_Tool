# /backend/db_connectors: Contains routes for handling database connections and schema retrieval.

from config import Config
import mysql.connector
import pymongo
import pyodbc
import logging

logger = logging.getLogger(__name__)

class DatabaseConnector:
    def __init__(self, db_type):
        self.db_type = db_type
        self.connection = None
        
    def connect(self, connection_params):
        try:
            encrypted_params = Config.CIPHER_SUITE.decrypt(connection_params.encode()).decode()
            params = eval(encrypted_params)
            
            if self.db_type == 'mongodb':
                self.connection = pymongo.MongoClient(
                    host=params.get('host'),
                    port=int(params.get('port', 27017)),
                    username=params.get('username'),
                    password=params.get('password'),
                    authSource=params.get('authSource', 'admin')
                )
                return True, "Connection successful"
                
            elif self.db_type == 'mysql':
                self.connection = mysql.connector.connect(
                    host=params.get('host'),
                    port=params.get('port', 3306),
                    user=params.get('username'),
                    password=params.get('password'),
                    database=params.get('database')
                )
                return True, "Connection successful"
                
            elif self.db_type == 'sqlserver':
                self.connection = pyodbc.connect(
                    driver='{ODBC Driver 17 for SQL Server}',
                    server=params.get('host'),
                    port=params.get('port', 1433),
                    uid=params.get('username'),
                    pwd=params.get('password'),
                    database=params.get('database')
                )
                return True, "Connection successful"
                
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            return False, str(e)
            
    def get_schema(self):
        try:
            if self.db_type == 'mongodb':
                return self._get_mongo_schema()
            elif self.db_type in ['mysql', 'sqlserver']:
                return self._get_sql_schema()
        except Exception as e:
            logger.error(f"Schema extraction error: {str(e)}")
            return None

    def _get_mongo_schema(self):
        schema = {}
        for db_name in self.connection.list_database_names():
            db = self.connection[db_name]
            schema[db_name] = {
                'collections': {},
                'indexes': {}
            }
            for coll_name in db.list_collection_names():
                schema[db_name]['collections'][coll_name] = {
                    'document_count': db[coll_name].estimated_document_count(),
                    'sample_document': db[coll_name].find_one()
                }
        return schema

    def _get_sql_schema(self):
        schema = {'tables': {}}
        cursor = self.connection.cursor()
        
        # Get tables
        cursor.execute("""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
        """)
        
        for table_name, table_type in cursor.fetchall():
            schema['tables'][table_name] = {
                'type': table_type,
                'columns': {},
                'constraints': []
            }
            
            # Get columns
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
            """)
            for col in cursor.fetchall():
                schema['tables'][table_name]['columns'][col[0]] = {
                    'type': col[1],
                    'nullable': col[2] == 'YES',
                    'default': col[3]
                }
                
            # Get constraints
            cursor.execute(f"""
                SELECT constraint_name, constraint_type 
                FROM information_schema.table_constraints 
                WHERE table_name = '{table_name}'
            """)
            for constr in cursor.fetchall():
                schema['tables'][table_name]['constraints'].append({
                    'name': constr[0],
                    'type': constr[1]
                })
                
        return schema
