## Library Import
import requests
import xml.etree.ElementTree as ET
import json
import re
import os
import xmltodict
import ast
from wikibaseintegrator import wbi_core, wbi_login

#function to get a list of all jsondicts
def dataacquision(queryterm:str, retmax:str) -> list(dict):
    """
    generates a list of all dictionaries with the metadata information
    Args:
        queryterm (str): simple queryterm we search for
        retmax (str): the amount of IDs we want to retrieve at the maximum
    Returns:
        list of dict: list of dictionaries we can iterate after with the other function to upload them to the wikibase
    """
    baseurl = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'
    dicts = []
    database = "db=pubmed"
    query = ''
    advquery= queryterm.split()
    for i in advquery:
        query+=i
        query+="+"
    query = "term=" + query[:-1]
    url = baseurl + database + "&" + query + "&" + "retmax=" + retmax

    #request IDs for searchterms and apply XML syntax
    idrequest = requests.get(url)
    idxml = ET.fromstring(idrequest.text)

    #use IDs in XML from first query to get Metadata in XML
    for tag in idxml.findall("IdList/Id"):
        ID = tag.text
        mdrequest = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=" + ID + "&retmode=xml")
        mdxml = ET.fromstring(mdrequest.text)
        f = mdxml.findall("*//MeshHeading/DescriptorName")
        #if len(f) != 0:
        #    for i in mdxml.findall("*//MeshHeading/DescriptorName"):
        #        print("ID " + ID + " besitzt die MeshTerms: " + i.text)
        #else:
        #    MESHTERMS HAVE TO BE GENERATED HERE BECAUSE ABSTRACT AND KEYWORDS ARE GOING TO BE DROPPED IN LINE 39+
        #    print("ID " + ID + " besitzt keine MeshTerms")
        #List of all xml-Terms to drop INCLUDING THE ONES USED FOR MESHTERMGENERATION
        xmlparents = ['.//DateCompleted/..','.//OtherAbstract/..','.//ArticleIdList/..','.//CitationSubset/..','.//AffiliationInfo/..','.//Identifier/..','.//CoiStatement/..','.//Abstract/..','.//Keyword/..']
        for tags in xmlparents:
            for parent in list(mdxml.iterfind(tags)):
                for child in list(parent.iterfind(re.findall(pattern=r'\w+',string=tags)[0])):
                    parent.remove(child)
        #print(ET.tostring(mdxml))
        jsondict = json.dumps(xmltodict.parse(ET.tostring(mdxml)),indent=4,sort_keys=True,ensure_ascii=False)
        #If you want to write into a file, uncomment next two lines
        #with open(os.path.join(os.path.dirname(os.path.abspath(__file__))+'/data/',ID +'.json','w') as file:
            #file.write(jsondict)
        #if you want to use a string for ongoing preprocessing or different tasks, uncomment next line, which turns the jsondict in stringformat into jsondict in dict format
        jsondict = ast.literal_eval(jsondict)
        dicts.append(jsondict)
    return dicts

def upload(raw_data: dict):
    # login object
    login_instance = wbi_login.Login(user='<bot user name>', pwd='<bot password>')
    #login_instance = wbi_login.Login(consumer_key='<your_consumer_key>', consumer_secret='<your_consumer_secret>')
    #login_instance.continue_oauth()


    # We have raw data, which should be written to Wikidata, namely two human NCBI entrez gene IDs mapped to two Ensembl Gene IDs

    for entrez_id, ensembl in raw_data.items():
        # add some references
        references = [
            [
                wbi_core.ItemID(value='Q20641742', prop_nr='P248', is_reference=True),
                wbi_core.Time(time='+2020-02-08T00:00:00Z', prop_nr='P813', is_reference=True),
                wbi_core.ExternalID(value='1017', prop_nr='P351', is_reference=True)
            ]
        ]

        # data type object
        entrez_gene_id = wbi_core.String(value=entrez_id, prop_nr='P351', references=references)
        ensembl_transcript_id = wbi_core.String(value=ensembl, prop_nr='P704', references=references)

        # data goes into a list, because many data objects can be provided to 
        data = [entrez_gene_id, ensembl_transcript_id]

        # Search for and then edit/create new item
        wd_item = wbi_core.ItemEngine(data=data)
        wd_item.write(login_instance)

if __name__ == '__main__':
    #main()
    print('test')