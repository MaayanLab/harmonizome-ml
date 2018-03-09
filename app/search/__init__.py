import pymysql
import json
from util import data_dir
from packet import Suggest

def perform_search(field, query=''):
    if field == 'target_class':
        attr_list = json.load(open(data_dir + '/attribute_list.json', 'r'))
        return Suggest([
            attr
            for i, attr in enumerate(attr_list)
            if i < 1000 and query in attr
        ])
    else:
        raise Exception("Field not found")
