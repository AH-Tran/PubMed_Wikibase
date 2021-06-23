## Basic Install
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
- docker-compose up -d
### Stop Wikibase Docker
docker-compose down
### Remove uploaded Data & run fresh Wikibase Instance
sudo rm -rf mediawiki-*  query-service-data/ quickstatements-data/
docker-compose up -d

## Making Changes
- LocalSettings.php.template
### Reload a single service (example: wikibase) to adopt new changes in settings
docker-compose up --no-deps -d wikibase

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

## Backups
- Take snapshots of: docker-compose file, mounted files
### Volume backup
- docker run -v wikibase-registry_mediawiki-mysql-data:/volume -v /root/volumeBackups:/backup --rm loomchild/volume-backup backup mediawiki-mysql-data_20190129
- docker run -v wikibase-registry_mediawiki-images-data:/volume -v /root/volumeBackups:/backup --rm loomchild/volume-backup backup mediawiki-images-data_20190129
- docker run -v wikibase-registry_query-service-data:/volume -v /root/volumeBackups:/backup --rm loomchild/volume-backup backup query-service-data_20190129

## Current Script Usage:
1. General Wikibase Setup [o]
2. create_properties.py [o]
3. data_retrieval.py [x]
    - desired output: pubmed_data.xml or pubmed_data.csv 
                    - mesh_data.csv
4. create_mesh_items.py [x]
5. create_items_wd.py [o]

## Further Research
- Dynamically Adapt Property Creation with CSV 
- Extract MeSH Entities from Wikidata
- Enter Wikibase into Wikibase Registry
- Authenticate Author Entity with either Scholia or 
- Document new encountered Limits
- IR/NLP metrics on Abstracts
- MeSH Tree Hierarchy as Knowledge Graph Structure
