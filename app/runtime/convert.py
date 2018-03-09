import nbformat
import nbconvert
from bs4 import BeautifulSoup

def ipynb_export_html(nb):
    exporter = nbconvert.HTMLExporter()
    export, resources = exporter.from_notebook_node(nb)
    # Strip things from export
    soup = BeautifulSoup(export, 'html5lib')
    soup.find('meta').decompose() # remove meta
    soup.find('title').decompose() # remove title
    soup.find('script').decompose() # remove first 2 scripts (require.js and jquery)
    soup.find('script').decompose()
    # soup.find('style').decompose() # remove first style (bootstrap)
    soup.find('link').decompose() # remove link to custom stylesheet
    nb_container = soup.select('#notebook-container')[0]
    nb_container['class'] = ''
    nb_container['id'] = ''
    return str(soup)

def ipynb_export_nb(nb):
    exporter = nbconvert.NotebookExporter()
    export, resources = exporter.from_notebook_node(nb)
    return export

def ipynb_import(ipynb):
    return nbformat.reads(ipynb, as_version=4)

def ipynb_import_from_file(file):
    return ipynb_import(open(file, 'r').read())
