from RaiseWikibase.raiser import batch
from RaiseWikibase.datamodel import claim, snak
import requests

def get_wd_entity(wid=''):
    """Returns JSON representation of a Wikidata entity for the given WID"""
    # Remove the following keys to avoid a problem with a new Wikibase instance
    remove_keys = ['lastrevid', 'pageid', 'modified', 'title', 'ns']
    try:
        r = requests.get('https://www.wikidata.org/entity/' + wid + '.json')
        entity = r.json().get('entities').get(wid)
        for key in remove_keys:
            entity.pop(key)
        entity['claims'] = claim(prop='P1',
                                 mainsnak=snak(datatype='external-id',
                                               value=wid,
                                               prop='P1',
                                               snaktype='value'),
                                 qualifiers=[],
                                 references=[])
    except Exception:
        entity = None
    return entity

wids = ['Q5', 'Q43229', 'Q17334923'] # human, organization, location
items = [get_wd_entity(wid) for wid in wids]
batch('wikibase-item', items)