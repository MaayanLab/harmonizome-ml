import pymysql
import json
from .util import data_dir
from .packet import Suggest

def perform_search(field, query=''):
    if field == 'target_class':
        attr_list = json.load(open(data_dir + '/class_list.json', 'r'))
        return Suggest([
            attr
            for i, attr in enumerate([
                attr
                for attr in attr_list
                if query.lower() in attr.lower()
            ])
            if i < 1000
        ])
    elif field == 'target_gene':
        attr_list = json.load(open(data_dir + '/gene_list.json', 'r'))
        return Suggest([
            attr
            for i, attr in enumerate([
                attr
                for attr in attr_list
                if query.lower() in attr.lower()
            ])
            if i < 1000
        ])
    else:
        raise Exception("Field not found")
