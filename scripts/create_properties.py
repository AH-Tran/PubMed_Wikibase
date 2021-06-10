from RaiseWikibase.dbconnection import DBConnection
from RaiseWikibase.datamodel import label, alias, description, snak, claim, entity, namespaces, datatypes
from RaiseWikibase.utils import get_wikidata_properties
from RaiseWikibase.raiser import page, batch, building_indexing
from pathlib import Path
import requests
import time
import numpy as np
import csv


def restrict(d, languages=['en', 'de']):
    """Restrict a dictionary with the labels or aliases to the specified 
    languages only"""
    # lang = ['en', 'de', 'zh', 'hi', 'es', 'fr', 'ar', 'bn', 'ru', 'pt', 'id']
    return dict((k, v) for (k, v) in d.items() if k in languages)


def property_wid(prop=''):
    """Create a simplified JSON represetation (only the label, aliases, 
    description and one claim) of the first local property 'Wikidata ID'"""
    p = entity(labels=label(value='Wikidata ID'),
               aliases=alias(value=["WID", 'WikidataID']),
               descriptions=description(value="ID of an entity in Wikidata"),
               claims=claim(prop='P2',
                            mainsnak=snak(datatype='string',
                                          value='http://www.wikidata.org/entity/$1',
                                          prop='P2',
                                          snaktype='value')),
               etype='property',
               datatype='external-id')
    p['claims'].update(claim(prop='P3',
                             mainsnak=snak(datatype='string',
                                           value='http://www.wikidata.org/entity/$1',
                                           prop='P3',
                                           snaktype='value')))
    return p


def property_wd(prop=''):
    """For the given PID of a property in Wikidata returns its 
    simplified JSON represetation (only the label, aliases, description 
    and one claim)"""
    if prop:
        r = requests.get('https://www.wikidata.org/entity/' + prop + '.json').json()
        po = r.get('entities').get(prop)
        p = entity(labels=restrict(po.get('labels')),
                   aliases=restrict(po.get('aliases')),
                   descriptions=restrict(po.get('descriptions')),
                   claims=claim(prop='P1',
                                mainsnak=snak(datatype='external-id',
                                              value=prop,
                                              prop='P1',
                                              snaktype='value')),
                   etype='property',
                   datatype='string')
    else:
        p = None
    return p


def property_wd_all():
    """ Send a SPARQL-request to Wikidata, get all properties with labels,
    aliases, descriptions and datatypes, and return a list of JSON 
    representations of the properties"""
    props = get_wikidata_properties(language='en')
    props = props.replace(np.nan, '').replace("http://www.wikidata.org/entity/", "", regex=True)
    props = props.groupby(['propertyWikidata', 'propertyType',
                           'propertyLabel', 'propertyDescription']
                          ).agg(propertyAlias=('propertyAlias', lambda x: list(x)),
                                fURL=('fURL', lambda x: list(x)),
                                cURI=('cURI', lambda x: list(x)),
                                ).reset_index()
    props = props[props.propertyWikidata != ("P1630" or "P1921")]
    props = props.sort_values(by=['propertyWikidata'],
                              key=lambda col: col.str.replace('P', '', regex=True).astype(float))
    plist = []
    for ind, row in props.iterrows():
        url, dtype, title, desc, alia, furl, curi = row
        p = entity(labels=label(value=title),
                   aliases=alias(value=alia),
                   descriptions=description(value=desc),
                   claims=claim(prop='P1',
                                mainsnak=snak(datatype='external-id',
                                              value=url,
                                              prop='P1',
                                              snaktype='value')),
                   etype='property',
                   datatype=datatypes[dtype])
        for f in furl:
            if f != '':
                p['claims'].update(claim(prop='P2',
                                         mainsnak=snak(datatype='string',
                                                       value=f,
                                                       prop='P2',
                                                       snaktype='value')))
        for c in curi:
            if c != '':
                p['claims'].update(claim(prop='P3',
                                         mainsnak=snak(datatype='string',
                                                       value=c,
                                                       prop='P3',
                                                       snaktype='value')))
        plist.append(p)
    return plist

def create_property(p_label,p_alias, p_description, p_datatype):
    """Creates a property with the given variables"""
    p = entity(labels={**label('en', p_label)},
                aliases=alias('en', p_alias),
                descriptions=description('en', p_description),
                etype='property',
                datatype=p_datatype)
    return p

def fill_texts():
    """Fill all texts from the texts-folder"""
    connection = DBConnection()
    cmodelpath = "../RaiseWikibase/texts/"
    cmodels = ['wikitext', 'Scribunto']
    for cmodel in cmodels:
        p = Path(cmodelpath + cmodel)
        folders = [x for x in p.iterdir() if x.is_dir()]
        for folder in folders:
            ns = namespaces[folder.name]
            files = [x for x in folder.iterdir() if x.is_file()]
            for file in files:
                pt = file.name.replace(':', '/')
                if pt.endswith('.css'):
                    cm = 'sanitized-css'
                else:
                    cm = cmodel
                text = file.read_text("utf-8")
                #print(ns, pt, cmodel)
                page(connection, cm, ns, text, pt, True)
    # Fill the Main page separately
    pt = "Main_Page"
    p = Path(cmodelpath + pt)
    text = p.read_text("utf-8")
    page(connection, 'wikitext', 0, text, pt, False)
    connection.conn.commit()
    connection.conn.close()

def first_property_setup():
    """Fill empty Wikibase with first properties and layout"""
    # Create first three properties in a local Wikibase
    p1 = property_wid()
    p2 = property_wd('P1630')
    p3 = property_wd('P1921')
    batch('wikibase-property', [p1, p2, p3])

    # Create PubMed relevant properties
    pb0 = property_wd('P932') #PBMCID
    pb1 = property_wd('P698') #pubmed id
    pb2 = property_wd('P496') #orcid
    pb3 = property_wd('P2322') #article id
    pb4 = property_wd('P356') #DOI
    pb5 = property_wd('P5875') #Researchgate publication id
    pb6 = property_wd('P8978') #DBLP publication
    pb7 = property_wd('P1476') #title
    pb8 = property_wd('P50') #author
    pb9 = property_wd('P2093') #author name string
    pb10 = property_wd('P577') #publication date
    pb11 = property_wd('P921') #main subject
    pb12 = property_wd('P31') #instance of
    pb13 = property_wd('P4510') #describes a project that uses
    pb14 = property_wd('P407') #language of work or name
    pb15 = property_wd('P1104') #number of pages
    pb16 = property_wd('P1433') #published in
    pb17 = property_wd('P478') #volumes
    pb18 = property_wd('P2860') #cites work
    pb19 = property_wd('P3176') #uses property
    pb20 = property_wd('P859') #sponsor
    pb21 = property_wd('P275') #copyright license
    batch('wikibase-property', [pb0, pb1, pb2, pb3, pb4, pb5, pb6, pb7, pb8, pb9, pb10, pb11, pb12, pb13, pb14, pb15, pb16, pb17, pb18, pb19, pb20, pb21])

    #Create MeSH relevant properties
    pmesh1 = property_wd('P672') #MeSH tree code
    pmesh2 = property_wd('P6694') #MeSH concept ID
    pmesh3 = property_wd('P9341') #MeSH qualifier ID 
    pmesh4 = property_wd('P486') #MeSH descriptor ID
    batch('wikibase-property', [pmesh1, pmesh2, pmesh3, pmesh4])

    #Create new Pubmed relevant properties not existent in Wikidata
    #keywords, affiliations, abstract, publication type
    np1 = create_property('keywords', ['keyword'], 'main keywords describing a publication', 'string')
    np2 = create_property('affiliations', ['affiliation', 'institute', 'organization'], 'organizations and affiliations associated with a given publication', 'string')
    np3 = create_property('abstract', ['abstracts', 'short summary'], 'The abstract of a given publication, summarizing the publications findings', 'string')
    np4 = create_property('publication type', ['publication medium'], 'The type/medium of the given publication i.e. journals, reports, etc.', 'string')
    batch('wikibase-property', [np1, np2, np3, np4])

    # Fill all texts
    fill_texts()

if __name__ == "__main__":

    time0 = time.time()

    first_property_setup()

    # to make the KG production-ready, execute building_indexing() as well
    # or run in shell 'docker-compose down' and 'docker-compose up -d' again
    # building_indexing() 

    print('Total time in seconds: ', time.time() - time0)
