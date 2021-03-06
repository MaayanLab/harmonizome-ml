import os
import json

app_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.dirname(os.path.realpath(__file__)) + '/../data'
PREFIX = '/' + os.environ.get('HARMONIZOME_API_PREFIX', 'Harmonizome-ML')
HARMONIZOME_PREFIX = os.environ.get('HARMONIZOME_PREFIX', 'http://amp.pharm.mssm.edu/Harmonizome')
PORT = json.loads(os.environ.get('HARMONIZOME_API_PORT', '5000'))
DEBUG = json.loads(os.environ.get('HARMONIZOME_API_DEBUG', 'true'))
MYSQL_HOST = os.environ.get('MYSQL_HOST', '')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', '')
MYSQL_USER = os.environ.get('MYSQL_USER', '')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')

globalContext = {
    'PREFIX': PREFIX,
    'HARMONIZOME_PREFIX': HARMONIZOME_PREFIX,
}
