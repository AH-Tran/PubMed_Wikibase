# load the necessary libraries
from logging import log
from RaiseWikibase.raiser import create_bot
from RaiseWikibase.settings import Settings
from wikidataintegrator.wdi_config import config as wdi_config
from wikidataintegrator import wdi_core, wdi_login
import pandas as pd
import pprint

def upload_data(login_instance, config, meshtermlist):
    """
    Creates Mesh terms from the given mesh term list
    Args:
        login_instance : login instance of the wikibase
        config : login credentials
        meshtermlist (csv): csv containing all relevant MeSH term lists
    """
    mydata = pd.read_csv(meshtermlist)
    for index, row in mydata.iterrows():
        ## Prepare the statements to be added
        try:
            item_statements = [] # all statements for one item
            item_statements.append(wdi_core.WDString(mydata.loc[index].at['MeSH Unique ID'], prop_nr="P26")) #MeSH Unique ID 
            item_statements.append(wdi_core.WDString(mydata.loc[index].at['MeSH Heading'], prop_nr="P27")) #MeSH Heading 
            #item_statements.append(wdi_core.WDString(mydata.loc[index].at['ScopeNote'], prop_nr="P28")) #Scope Note
            item_statements.append(wdi_core.WDUrl(mydata.loc[index].at['MeSHBrowserLink'], prop_nr="P29")) #MeSH URL
            #item_statements.append(wdi_core.WDString(mydata.loc[index].at['TreeNumbers'], prop_nr="P30")) #Tree Number
        except:
            pass

        ## instantiate the Wikibase page, add statements, labels and descriptions
        try:
            wbPage = wdi_core.WDItemEngine(data=item_statements, mediawiki_api_url=config.wikibase_url + "/w/api.php")
            wbPage.set_label(mydata.loc[index].at['MeSH Heading'], lang="en")
            #wbPage.set_label("Kennzeichen", lang="de")
            wbPage.set_description("MeSH Entity extracted from NLM", lang="en")
        except:
            print('Continuing')
            continue
        #wbPage.set_description("Beschreibung", lang="de")


        ## sanity check (debug)
        pprint.pprint(wbPage.get_wd_json_representation())

        ## write data to wikibase
        try:
            wbPage.write(login_instance)
        except:
            print('Continuing')
            continue

def main(meshtermlist):
    ## Create Bot and save credentials in .config.json
    # WIP: Implement check if bot already exists:
    create_bot()
    config = Settings()

    ## Connect to Wikibase Instance and login with credentials
    wdi_config['MEDIAWIKI_API_URL'] = config.mediawiki_api_url
    wdi_config['SPARQL_ENDPOINT_URL'] = config.sparql_endpoint_url
    wdi_config['WIKIBASE_URL'] = config.wikibase_url
    #The config dictionary can be used in WikibaseIntegrator for creating a login instance:
    login_instance = wdi_login.WDLogin(user=config.username, pwd=config.password)

    # login to wikibase
    #login_instance = wdi_login.WDLogin(user=config.username, pwd=config.password, mediawiki_api_url=config.mediawiki_api_url)
    
    upload_data(login_instance, config, meshtermlist)

    print('>>Finished Inserting MeSH Entities<<') 

if __name__ == "__main__":
    ## Create Bot and save credentials in .config.json
    # WIP: Implement check if bot already exists:
    create_bot()
    config = Settings()

    ## Connect to Wikibase Instance and login with credentials
    wdi_config['MEDIAWIKI_API_URL'] = config.mediawiki_api_url
    wdi_config['SPARQL_ENDPOINT_URL'] = config.sparql_endpoint_url
    wdi_config['WIKIBASE_URL'] = config.wikibase_url
    #The config dictionary can be used in WikibaseIntegrator for creating a login instance:
    login_instance = wdi_login.WDLogin(user=config.username, pwd=config.password)

    # login to wikibase
    #login_instance = wdi_login.WDLogin(user=config.username, pwd=config.password, mediawiki_api_url=config.mediawiki_api_url)
    upload_data(login_instance, config)


