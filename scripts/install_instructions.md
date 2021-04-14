## Basic Install
- Install & Enable WSL2
- Install Docker
- For Windows: Install Ubuntu Terminal & Windows Terminal
- Create Directory
- git clone https://github.com/UB-Mannheim/RaiseWikibase
cd RaiseWikibase/
pip3 install -e .
- env.tmpl > rename to '.env' and insert usernames/password
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
docker run -v wikibase-registry_mediawiki-mysql-data:/volume -v /root/volumeBackups:/backup --rm loomchild/volume-backup backup mediawiki-mysql-data_20190129
docker run -v wikibase-registry_mediawiki-images-data:/volume -v /root/volumeBackups:/backup --rm loomchild/volume-backup backup mediawiki-images-data_20190129
docker run -v wikibase-registry_query-service-data:/volume -v /root/volumeBackups:/backup --rm loomchild/volume-backup backup query-service-data_20190129
