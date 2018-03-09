import os

app_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.dirname(os.path.realpath(__file__)) + '/../data'
PREFIX = os.environ.get('PREFIX', '')
MYSQL_HOST = os.environ.get('MYSQL_HOST', '')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', '')
MYSQL_USER = os.environ.get('MYSQL_USER', '')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')

globalContext = {
    'PREFIX': PREFIX
}
