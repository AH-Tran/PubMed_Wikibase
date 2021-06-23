```
Automated creation and filling of a new wikibase instance with PubMed metadata and MeSH terms.
```
* Automated inserts into a fresh Wikibase instance
* Scripts for automated property and item creation given a csv

## Table of contents
- [How to use](#how-to-use)
  * [Installation](#installation)
  * [Customizing Wikibase](#customizing-wikibase)
  * [Creating Properties](#creating-properties)
  * [Creating Items](creating-items)
  * [Updating Item Connection](#updating-item-connection)
  * [Useful Docker Commands](#useful-docker-commands)
  * [Creating Backups](#creating-backups)
- [Acknowledgments](#acknowledgments)
- [Further Research ](#further-research)

## How to use

### Installation
```
- Install & Enable WSL2
- Install Docker
- For Windows: Install Ubuntu Terminal & Windows Terminal from Windows Store & relevant libraries
    - https://codefellows.github.io/setup-guide/
- Create Directory
- git clone https://github.com/UB-Mannheim/RaiseWikibase
cd RaiseWikibase/
sudo apt install default-libmysqlclient-dev
pip3 install -e .
- env.tmpl > rename to '.env' and insert usernames/password
    - passwords must be at least 10 characters long!
    - [WB_DB_USER], [WB_DB_NAME], [WB_ADMIN_USER] must be capitalized or ideally full cap in order to avoid db connection errors
pip3 install -r requirements.txt
- docker-compose up -d
```
### Customizing Wikibase
```
## Making Changes
- LocalSettings.php.template
## Extensions
- Download Extension in ./RaiseWikibase/extensions
- Add Volume to docker-ompose.yml
    - ./extensions/TemplateStyles:/var/www/html/extensions/TemplateStyles
- Add Volume to LocalSettings.php.template
    -wfLoadExtension( 'TemplateStyles' );
    ${DOLLAR}wgTidyConfig = [
        'driver' => 'RaggettInternalPHP',
        'tidyConfigFile' => "${DOLLAR}IP/includes/tidy/tidy.conf",
    ];
```

### Creating Properties
create_properties.py
```
#Create MeSH relevant properties
pmesh1 = property_wd('P672') #MeSH tree code
pmesh2 = property_wd('P6694') #MeSH concept ID
pmesh3 = property_wd('P9341') #MeSH qualifier ID 
pmesh4 = property_wd('P486') #MeSH descriptor ID
#pmesh5 = property_wd('') #MeSH Headings
batch('wikibase-property', [pmesh1, pmesh2, pmesh3, pmesh4])
```
### Creating Items
create_items_wd.py
```
def upload_data(login_instance, config):
    # load excel table to load into Wikibase
    mydata = pd.read_csv("pubmed_data.csv")
    for index, row in mydata.iterrows():
        ## Prepare the statements to be added
        item_statements = [] # all statements for one item
        item_statements.append(wdi_core.WDString(mydata.loc[index].at['PubmedArticle_MedlineCitation_Article_ArticleTitle'], prop_nr="P11")) #title 
        item_statements.append(wdi_core.WDString(mydata.loc[index].at['PubmedArticle_MedlineCitation_Article_AuthorList_Author_LastName'], prop_nr="P12")) #author

        ## instantiate the Wikibase page, add statements, labels and descriptions
        wbPage = wdi_core.WDItemEngine(data=item_statements, mediawiki_api_url=config.wikibase_url + "/w/api.php")
        wbPage.set_label(mydata.loc[index].at['PubmedArticle_MedlineCitation_Article_ArticleTitle'], lang="en")
        wbPage.set_description("Article retrieved from PubMed", lang="en")

        ## sanity check (debug)
        pprint.pprint(wbPage.get_wd_json_representation())

        ## write data to wikibase
        wbPage.write(login_instance)
```
### Updating Item Connection
update_statements.py
### Useful Docker Commands
```
### Stop Wikibase Docker
docker-compose down
### Remove uploaded Data & run fresh Wikibase Instance
sudo rm -rf mediawiki-*  query-service-data/ quickstatements-data/
docker-compose up -d
### Reload a single service (example: wikibase) to adopt new changes in settings
docker-compose up --no-deps -d wikibase
```

### Creating Backups
```
- Take snapshots of: docker-compose file, mounted files
### Volume backup
- docker run -v wikibase-registry_mediawiki-mysql-data:/volume -v /root/volumeBackups:/backup --rm loomchild/volume-backup backup mediawiki-mysql-data_20190129
- docker run -v wikibase-registry_mediawiki-images-data:/volume -v /root/volumeBackups:/backup --rm loomchild/volume-backup backup mediawiki-images-data_20190129
- docker run -v wikibase-registry_query-service-data:/volume -v /root/volumeBackups:/backup --rm loomchild/volume-backup backup query-service-data_20190129
```
## Current Script Usage:
1. General Wikibase Setup [o]
2. create_properties.py [o]
3. data_retrieval.py [x]
    - desired output: pubmed_data.xml or pubmed_data.csv 
                    - mesh_data.csv
4. create_mesh_items.py [x]
5. create_items_wd.py [o]


## Acknowledgements

## Further Research
- Dynamically Adapt Property Creation with CSV 
- Support for different formats than CSV
- Extract MeSH Entities from Wikidata
- Enter Wikibase into Wikibase Registry
- Authenticate Author Entity with either Scholia or 
- Document new encountered Limits
- IR/NLP metrics on Abstracts
- MeSH Tree Hierarchy as Knowledge Graph Structure
