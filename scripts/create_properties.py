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
    print('><Creating properties<<')
    # Create first three properties in a local Wikibase
    p1 = property_wid() #wikibaseID
    p2 = property_wd('P1630') #formatter URL
    p3 = property_wd('P1921') #formatter URI for RDF resource
    batch('wikibase-property', [p1, p2, p3])

    # Create PubMed relevant properties
    p4 = property_wd('P932') #PBMCID
    p5 = property_wd('P698') #pubmed id
    p6 = property_wd('P496') #orcid
    p7 = property_wd('P2322') #article id
    p8 = property_wd('P356') #DOI
    p9 = property_wd('P5875') #Researchgate publication id
    p10 = property_wd('P8978') #DBLP publication
    p11 = property_wd('P1476') #title
    p12 = property_wd('P50') #author
    p13 = property_wd('P2093') #author name string
    p14 = property_wd('P577') #publication date
    p15 = property_wd('P921') #main subject
    p16 = property_wd('P31') #instance of
    p17 = property_wd('P4510') #describes a project that uses
    p18 = property_wd('P407') #language of work or name
    p19 = property_wd('P1104') #number of pages
    p20 = property_wd('P1433') #published in
    p21 = property_wd('P478') #volumes
    p22 = property_wd('P2860') #cites work
    p23 = property_wd('P3176') #uses property
    p24 = property_wd('P859') #sponsor
    p25 = property_wd('P275') #copyright license
    batch('wikibase-property', [p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25])

    #Create MeSH relevant properties
    p26 = property_wd('P486') #MeSH descriptor ID/ Unique ID
    p27 = create_property('MeSH Heading', ['Heading'], 'Label of the MeSH descriptor ID', 'string')
    p28 = create_property('ScopeNote', ['Note'], 'Note describing further the Label of a MeSH Heading', 'string')
    p29 = create_property('MeshBrowserLink', ['Mesh URL', 'MeSH Browser'], 'MeSH Browser URL of a specific Mesh Heading', 'url')
    p30 = create_property('MeSH Treecode', ['Tree', 'MeSH Tree'], 'MeSH Tree Code of a specific Mesh Heading', 'string')

    #pmesh5 = property_wd('') #MeSH Headings
    batch('wikibase-property', [p26, p27, p28, p29, p30])

    #Create new Pubmed relevant properties not existent in Wikidata
    p31 = create_property('keywords', ['keyword'], 'main keywords describing a publication', 'string')
    p32 = create_property('affiliations', ['affiliation', 'institute', 'organization'], 'organizations and affiliations associated with a given publication', 'string')
    p33 = create_property('abstract', ['abstracts', 'short summary'], 'The abstract of a given publication, summarizing the publications findings', 'string')
    p34 = create_property('publication type', ['publication medium'], 'The type/medium of the given publication i.e. journals, reports, etc.', 'string')
    #Create additional properties
    p35 = create_property('journal title', ['magazine title'], 'Title of the corresponding journal', 'string')
    p36 = property_wd('P236') #ISSN
    p37 = create_property('journal publication date', ['journal date'], 'Publication Date of the corresponding journal', 'string')
    p38 = property_wd('P1055') #NLM ID
    batch('wikibase-property', [p31, p32, p33, p34, p35, p36, p37, p38])

    # Fill all texts
    fill_texts()
    print('>>Finisched Creating properties<<')

if __name__ == "__main__":

    time0 = time.time()

    first_property_setup()

    # to make the KG production-ready, execute building_indexing() as well
    # or run in shell 'docker-compose down' and 'docker-compose up -d' again
    # building_indexing() 

    print('Total time in seconds: ', time.time() - time0)
