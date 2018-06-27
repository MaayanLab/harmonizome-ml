import pymysql
from sqlalchemy import create_engine
import pandas as pd
import json
from harmonizome import Harmonizome, df_column_uniquify, save_df

con = pymysql.connect(
    host='amp.pharm.mssm.edu',
    user='harmonizome',
    password='sysbio',
    database='harmonizome',
)

cur = con.cursor()
cur.execute('''
select
    concat(
        resource.name,
        "\t",
        dataset.name_without_resource
    ),
    dataset.name
from
    dataset,
    resource
where
    dataset.resource_fk=resource.id;
''')
entries = dict(list(cur))
entries

cur = con.cursor()
cur.execute('''
select
    *
from
    dataset;
''')
datasets = list(cur)
con.close()

label = [desc[0] for desc in cur.description]
[dict(zip(label, dataset)) for dataset in datasets]

omics_datasets = list(map(entries.get, '''Cancer Cell Line Encyclopedia	Cell Line Gene Expression Profiles
Encyclopedia of DNA Elements	Transcription Factor Targets
Allen Brain Atlas	Adult Human Brain Tissue Gene Expression Profiles
ChIP-X Enrichment Analysis	Transcription Factor Targets
BioGPS	Cell Line Gene Expression Profiles
Genotype Tissue Expression	Tissue Gene Expression Profiles
'''.splitlines()))
omics_datasets

attribute_datasets = list(map(entries.get, '''DISEASES	Text-mining Gene-Disease Assocation Evidence Scores
Human Phenotype Ontology	Gene-Disease Associations
Mammalian Phenotype Ontology	Gene-Phenotype Associations
Gene Ontology	Biological Process Annotations
'''.splitlines()))



print('Loading all datasets...')
D = {}
dataset_lookup = {}
for dataset in omics_datasets + attribute_datasets:
    for df in Harmonizome.download_df([dataset], ['gene_attribute_matrix.txt.gz']):
        D[dataset] = df
        # save_df(df, '../'+dataset_short.replace(' ','')+'.feather')


print('Enumerating attributes')
all_columns = []
for dataset in attribute_datasets:
    all_columns += ['%s (%s from %s)' % (col[0], col[1], dataset)
                    for col in map(json.loads, D[dataset].columns)]
all_columns[:10]+all_columns[-10:]
len(all_columns)
json.dump(all_columns, open('attribute_list.json', 'w'))




con = pymysql.connect(
    host='amp.pharm.mssm.edu',
    user='harmonizome',
    password='sysbio',
    database='harmonizome',
)

cur = con.cursor()
cur.execute('''
select
    concat(
        resource.name,
        "\t",
        dataset.name_without_resource
    ),
    concat(
        dataset.name,
        " (",
        dataset_group.name,
        ")"
    )
from
    dataset,
    resource,
    dataset_group
where
    dataset.resource_fk = resource.id
and dataset.dataset_group_fk = dataset_group.id;
''')
entries = dict(list(cur))
entries


omics_datasets = list(map(entries.get, '''Cancer Cell Line Encyclopedia	Cell Line Gene Expression Profiles
Encyclopedia of DNA Elements	Transcription Factor Targets
Allen Brain Atlas	Adult Human Brain Tissue Gene Expression Profiles
ChIP-X Enrichment Analysis	Transcription Factor Targets
BioGPS	Cell Line Gene Expression Profiles
Genotype Tissue Expression	Tissue Gene Expression Profiles
'''.splitlines()))
## omics
omics_datasets

attribute_datasets = list(map(entries.get, '''DISEASES	Text-mining Gene-Disease Assocation Evidence Scores
Human Phenotype Ontology	Gene-Disease Associations
Mammalian Phenotype Ontology	Gene-Phenotype Associations
Gene Ontology	Biological Process Annotations
'''.splitlines()))
attribute_datasets
## Annotations or associations

all_omics_datasets = {k:v for k,v in entries.items() if 'omics' in v}
print('\n'.join(all_omics_datasets.keys()))
all_attribute_datasets = {k:v for k,v in entries.items() if 'annotation' in v or 'association' in v}
all_attribute_datasets
print('\n'.join(all_attribute_datasets.keys()))

len(all_omics_datasets)+len(all_attribute_datasets)
len(entries)
print(
    '\n'.join([
        '%s (%s)' % (entry[0], entry[1])
        for entry in entries.items()
        if all_omics_datasets.get(entry[0]) is None and all_attribute_datasets.get(entry[0]) is None
    ]))

con.close()
