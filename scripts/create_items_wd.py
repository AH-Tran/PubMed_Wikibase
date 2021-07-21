# load the necessary libraries
from logging import log
from RaiseWikibase.raiser import create_bot
from RaiseWikibase.settings import Settings
from wikidataintegrator.wdi_config import config as wdi_config
from wikidataintegrator import wdi_core, wdi_login
import pandas as pd
import pprint
import json

def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct

def upload_data(login_instance, config, metadata):
    author_list = []
    mesh_list = []
    df = pd.read_csv('meshtermlist.csv')

    for index in metadata:
        
        # Get relevant Values from retrieved Metadata
        try:
            PMID = safeget(index, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'PMID', '#text')
            title = safeget(index, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'ArticleTitle')
            pdate = safeget(index, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'ArticleDate', 'Day') + '.' + \
                    safeget(index, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'ArticleDate', 'Month') + '.' + \
                    safeget(index, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'ArticleDate', 'Year')
            author_list = safeget(index, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'AuthorList', 'Author')
            language = safeget(index, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'Language')
            #publication_type = safeget(index, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'PublicationTypeList', 'PublicationType', '#text')
            NLM_ID = safeget(index, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'MedlineJournalInfo', 'NlmUniqueID')
            journal_title = safeget(index, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'Journal', 'Title')
            journal_issn = safeget(index, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'Journal', 'ISSN', '#text')
            journal_date = safeget(index, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'Journal', 'JournalIssue', 'PubDate', 'Day') + '.' + \
                        safeget(index, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'Journal', 'JournalIssue', 'PubDate', 'Month') + '.' + \
                        safeget(index, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'Journal', 'JournalIssue', 'PubDate', 'Year')
            mesh_list = safeget(index, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'MeshHeadingList', 'DescriptorName')
        except TypeError:
            print('Malformed Metadata Value detected, skipping Value and continuing Insert')
            pass

        ## Prepare the statements to be added
        item_statements = [] # all statements for one item
        try:
            item_statements.append(wdi_core.WDString(PMID, prop_nr="P5")) #PMID
        except:
            pass
        try:
            item_statements.append(wdi_core.WDString(NLM_ID, prop_nr="P38")) #NLM ID
        except:
            pass
        try:
            item_statements.append(wdi_core.WDString(title, prop_nr="P11")) #title 
        except:
            pass
        try:
            item_statements.append(wdi_core.WDString(pdate, prop_nr="P14")) #publication date 
        except:
            pass
        for a in author_list:
            try:
                item_statements.append(wdi_core.WDString(str(safeget(a, 'LastName')+ ',' + safeget(a, 'ForeName')), prop_nr="P13")) #author name string
            except:
                pass
        try:
            item_statements.append(wdi_core.WDString(language, prop_nr="P18")) #language
        except:
            pass
        try:
            item_statements.append(wdi_core.WDString(journal_title, prop_nr="P35")) #journal title
        except:
            pass
        try:
            item_statements.append(wdi_core.WDString(journal_issn, prop_nr="P36")) #journal issn
        except:
            pass
        try:
            item_statements.append(wdi_core.WDString(journal_date, prop_nr="P37")) #journal date
        except:
            pass
        try:
            for m in mesh_list:
                if ( df[df['MeSH Unique ID'] == safeget(m, '@UI')].index[0]):
                    r= df[df['MeSH Unique ID'] == safeget(m, '@UI')].index[0] + 1
                    entity_link = 'http://localhost:8181/wiki/Item:'+ 'Q' + str(r)
                    item_statements.append(wdi_core.WDItem(entity_link, prop_nr="P39"))
        except:
            pass
        ##item_statements.append(wdi_core.WDString("mesh descriptor id", prop_nr="P29")) #MeSH Descriptor ID
        ##item_statements.append(wdi_core.WDItem("Q1234", prop_nr="P2"))
        ##item_statements.append(wdi_core.WDURL("<http://someURL>", prop_nr="P3"))

        ## instantiate the Wikibase page, add statements, labels and descriptions
        try:
            wbPage = wdi_core.WDItemEngine(data=item_statements, mediawiki_api_url=config.wikibase_url + "/w/api.php")
            wbPage.set_label(title, lang="en")
            #wbPage.set_label("Kennzeichen", lang="de")
            wbPage.set_description("Article retrieved from PubMed", lang="en")
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

    print('>>Finished Inserting PubMed Articles<<') 

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


