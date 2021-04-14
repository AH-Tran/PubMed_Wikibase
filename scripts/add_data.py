from RaiseWikibase.raiser import create_bot
from RaiseWikibase.settings import Settings
#RaiseWikibase can create a bot account for a local Wikibase instance, save the login and password to a configuration file and read them back to a config dictionary:
create_bot()
config = Settings()

#The config dictionary can be used in WikibaseIntegrator for creating a login instance:
from wikibaseintegrator import wbi_login
login_instance = wbi_login.Login(user=config.username, pwd=config.password)

#You can also create the JSON representations of entities in WikidataIntegrator or WikibaseIntegrator and then fill them into a Wikibase instance using RaiseWikibase. In WikibaseIntegrator you can create a wbi_core.ItemEngine object and use the get_json_representation function:
from wikibaseintegrator import wbi_core
item = wbi_core.ItemEngine(item_id='Q1003030')
ijson = item.get_json_representation()

#The JSON representation of an entity can be uploaded into a Wikibase instance using the batch function in RaiseWikibase:
from RaiseWikibase.raiser import batch
batch('wikibase-item', [ijson])

#docker exec raisewikibase_wikibase_1 bash "-c" "php maintenance/update.php --quick --force"