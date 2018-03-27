import pymysql
import json
from util import data_dir
from packet import Suggest

def perform_search(field, query=''):
    if field == 'target_class':
        attr_list = json.load(open(data_dir + '/attribute_list.json', 'r'))
        return Suggest([
            attr
            for i, attr in enumerate([
                attr
                for attr in attr_list
                if query in attr
            ])
            if i < 1000
        ])
    else:
        raise Exception("Field not found")
