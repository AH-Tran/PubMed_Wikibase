from RaiseWikibase.raiser import create_bot
from RaiseWikibase.settings import Settings
from RaiseWikibase.datamodel import label, alias, description, snak, claim, entity, namespaces, datatypes
from RaiseWikibase.raiser import page, batch, building_indexing
import requests
#from wikibaseintegrator import wbi_login
#from wikibaseintegrator.wbi_config import config as wbi_config
from wikidataintegrator import wdi_core, wdi_login, wdi_helpers
import os

def create_properties(properties, login_instance):
    #for p in properties:
    #    batch('wikibasep-property', p)
    return 1

def create_item(raw_data, login_instance):
    #for entrez_id, ensembl in raw_data.items():
    return 1

def main():
    ## Load XML-Data
    #data_path = '../data'
    #load_xml(data_path)
    
    ## Create Bot and save credentials in .config.json
    create_bot()
    config = Settings()

    ## Connect to Wikibase Instance and login with credentials
    wbi_config['MEDIAWIKI_API_URL'] = config.mediawiki_api_url
    wbi_config['SPARQL_ENDPOINT_URL'] = config.sparql_endpoint_url
    wbi_config['WIKIBASE_URL'] = config.wikibase_url
    #The config dictionary can be used in WikibaseIntegrator for creating a login instance:
    login_instance = wbi_login.Login(user=config.username, pwd=config.password)

    raw_data = {
    '50943': 'ENST00000376197',
    '1029': 'ENST00000498124'
    }

    create_item(raw_data, login_instance)

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

def restrict(d, languages=['en', 'de']):
    """Restrict a dictionary with the labels or aliases to the specified 
    languages only"""
    # lang = ['en', 'de', 'zh', 'hi', 'es', 'fr', 'ar', 'bn', 'ru', 'pt', 'id']
    return dict((k, v) for (k, v) in d.items() if k in languages)

if __name__ == '__main__':
    #main()
    #p1 = property_wid()
    p2 = property_wd('P1630')
    p3 = property_wd('P1921')
    batch('wikibase-property', [p2, p3])
    print('test')