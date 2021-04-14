from wikibaseintegrator.wbi_config import config as wbi_config

wbi_config['MEDIAWIKI_API_URL'] = 'http://localhost:8181/api.php'
wbi_config['SPARQL_ENDPOINT_URL'] = 'http://localhost:8989/bigdata/sparql'
wbi_config['WIKIBASE_URL'] = 'http://wikibase.svc'

def main():
    my_first_wikidata_item = wbi_core.ItemEngine(item_id='Q5')

    print(my_first_wikidata_item.get_json_representation())

if __name__ == '__main__':
    main()