from RaiseWikibase.datamodel import label, alias, description, snak, claim, entity
labels = {**label('en', 'organization'), **label('de', 'Organisation')}
aliases = alias('en', ['organisation', 'org']) | alias('de', ['Org', 'Orga'])
descriptions = description('en', 'social entity (not necessarily commercial)')
descriptions.update(description('de', 'soziale Struktur mit einem gemeinsamen Ziel'))