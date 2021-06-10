from RaiseWikibase.raiser import create_bot
from RaiseWikibase.settings import Settings
from wikibaseintegrator import wbi_login
from wikibaseintegrator.wbi_config import config as wbi_config
import os
def load_xml(directory):
    for path, subdir, file in os.walk(directory):
        extensions = tuple([".xml"])
        files = [f for f in file if f.endswith(extensions)]
    return files

def create_item(raw_data, login_instance):
    for entrez_id, ensembl in raw_data.items():
    # add some references
    references = [
        [
            wbi_core.ItemID(value='Q20641742', prop_nr='P248', is_reference=True),
            wbi_core.Time(time='+2020-02-08T00:00:00Z', prop_nr='P813', is_reference=True),
            wbi_core.ExternalID(value='1017', prop_nr='P351', is_reference=True)
        ]
    ]

    # data type object
    entrez_gene_id = wbi_core.String(value=entrez_id, prop_nr='P351', references=references)
    ensembl_transcript_id = wbi_core.String(value=ensembl, prop_nr='P704', references=references)

    # data goes into a list, because many data objects can be provided to
    data = [entrez_gene_id, ensembl_transcript_id]

    # Search for and then edit/create new item
    wd_item = wbi_core.ItemEngine(data=data)
    wd_item.write(login_instance)
    return none

def create_properties(properties, login_instance):
    for p in properties
        batch('wikibasep-property', p)

def assign_properties(items, properties):
    return none

def query_data(item, login_instance):
    from wikibaseintegrator import wbi_core
    query = {
    'action': 'query',
    'prop': 'revisions',
    'titles': item,
    'rvlimit': 10
    }
    print(wbi_core.FunctionsEngine.mediawiki_api_call_helper(query, allow_anonymous=True))

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

if __name__ == '__main__':
    main()