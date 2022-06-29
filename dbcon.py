# Connect to MYSQL Database

# import mysql.connector as myql
import mysql
from mysql import connector
from mysql.connector import Error
from mysql.connector.constants import ClientFlag


class App:
    #Local mysql(on premisis)
    def db_conn1(self):
        try:
            h_db = mysql.connector.connect(host="localhost", username="ravindra", password="Nandu@2021", database="HPS",
                                           buffered=True)
            h_cursor = h_db.cursor()
        except mysql.connector.Error as error:
            print("Query Failed {}".format(error))
        return h_db, h_cursor

    # cloud mysql
    def db_conn(self):
        try:
            config = {
                'user': 'ravindra',
                'password': 'ravindra',
                'host': '35.239.29.23',
                'client_flags': [ClientFlag.SSL],
                'ssl_ca': 'ssl/server-ca.pem',
                'ssl_cert': 'ssl/client-cert.pem',
                'ssl_key': 'ssl/client-key.pem'
            }
            h_db = mysql.connector.connect(**config)
            h_cursor = h_db.cursor()
        except mysql.connector.Error as error:
            print("Query Failed {}".format(error))
        return h_db, h_cursor


AppInst = App()
