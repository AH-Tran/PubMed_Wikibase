import spacy
import scispacy
from scispacy.linking import EntityLinker

nlp = spacy.load("en_core_sci_sm")
nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "mesh"})
abstract = "For the past several decades, the infectious disease profile in China has been shifting with rapid developments in social and economic aspects, environment, quality of food, water, housing, and public health infrastructure. Notably, 5 notifiable infectious diseases have been almost eradicated, and the incidence of 18 additional notifiable infectious diseases has been significantly reduced. Unexpectedly, the incidence of over 10 notifiable infectious diseases, including HIV, brucellosis, syphilis, and dengue fever, has been increasing. Nevertheless, frequent infectious disease outbreaks/events have been reported almost every year, and imported infectious diseases have increased since 2015. New pathogens and over 100 new genotypes or serotypes of known pathogens have been identified. Some infectious diseases seem to be exacerbated by various factors, including rapid urbanization, large numbers of migrant workers, changes in climate, ecology, and policies, such as returning farmland to forests. This review summarizes the current experiences and lessons from China in managing emerging and re-emerging infectious diseases, especially the effects of ecology, climate, and behavior, which should have merits in helping other countries to control and prevent infectious diseases."
doc = nlp(abstract)

# Let's look at a random entity!
linker = nlp.get_pipe("scispacy_linker")
entity = doc.ents
for i in entity:
    #print("Name: ", i)
    for mesh_ent in i._.kb_ents:
        meshinfo = linker.kb.cui_to_entity[mesh_ent[0]]
        print(meshinfo)
