# load the necessary libraries
from logging import log
from RaiseWikibase.raiser import create_bot
from RaiseWikibase.settings import Settings
from wikidataintegrator.wdi_config import config as wdi_config
from wikidataintegrator import wdi_core, wdi_login
import pandas as pd
import pprint

def upload_data(login_instance, config, metadata):
    # load excel table to load into Wikibase
    mydata = pd.read_csv("pubmed_data.csv")
    for index, row in mydata.iterrows():
        ## Prepare the statements to be added
        item_statements = [] # all statements for one item
        item_statements.append(wdi_core.WDString(mydata.loc[index].at['PubmedArticle_MedlineCitation_Article_ArticleTitle'], prop_nr="P11")) #title 
        #item_statements.append(wdi_core.WDString(mydata.loc[index].at['PubmedArticle_MedlineCitation_Article_Abstract_AbstractText'], prop_nr="P32")) #abstract 
        item_statements.append(wdi_core.WDString(mydata.loc[index].at['PubmedArticle_MedlineCitation_Article_AuthorList_Author_LastName'], prop_nr="P12")) #author
        #item_statements.append(wdi_core.WDString(mydata.loc[index].at['PubmedArticle_MedlineCitation_PMID'], prop_nr="P5"))  #Pubmed ID
        #item_statements.append(wdi_core.WDString(mydata.loc[index].at['PubmedArticle_PubmedData_History_PubMedPubDate_Year'], prop_nr="P14")) #publication date
        ##item_statements.append(wdi_core.WDString("mesh descriptor id", prop_nr="P29")) #MeSH Descriptor ID
        ##item_statements.append(wdi_core.WDItem("Q1234", prop_nr="P2"))
        ##item_statements.append(wdi_core.WDURL("<http://someURL>", prop_nr="P3"))

        ## instantiate the Wikibase page, add statements, labels and descriptions
        wbPage = wdi_core.WDItemEngine(data=item_statements, mediawiki_api_url=config.wikibase_url + "/w/api.php")
        wbPage.set_label(mydata.loc[index].at['PubmedArticle_MedlineCitation_Article_ArticleTitle'], lang="en")
        #wbPage.set_label("Kennzeichen", lang="de")
        wbPage.set_description("Article retrieved from PubMed", lang="en")
        #wbPage.set_description("Beschreibung", lang="de")

        ## sanity check (debug)
        pprint.pprint(wbPage.get_wd_json_representation())

        ## write data to wikibase
        wbPage.write(login_instance)

#def link_entitity():
 
def main(metadata):
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
    upload_data(login_instance, config, metadata)   

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


