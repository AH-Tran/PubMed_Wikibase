import spacy
import scispacy
from scispacy.linking import EntityLinker
nlp = spacy.load("en_core_sci_sm")
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def IDacq(queryterm: str):
    nlp = spacy.load("en_core_sci_sm")
    nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "mesh"})
    baseurl = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?api_key=64a858580cdbab48732231789433c6dfa108&'
    retmax = 100000
    database = "db=pubmed"
    query = ''
    advquery= queryterm.split()
    for i in advquery:
        query+=i
        query+="+"
    query = "term=" + query[:-1]
    url = baseurl + database + "&" + query + "&" + "retmax=" + str(retmax)

    #request IDs for searchterms and apply XML syntax
    idrequest = requests.get(url)
    idxml = ET.fromstring(idrequest.text)

    #use IDs in XML from first query to get Metadata in XML
    IDLIST = []
    ids = idxml.findall("IdList/Id")
    for i in ids:
        IDLIST.append(str(i.text))
    while len(IDLIST)%100000==0:
        retstart = len(IDLIST)
        print(len(IDLIST))
        idrequest = requests.get(url+"&retstart=" + str(retstart))
        idxml = ET.fromstring(idrequest.text)
        ids = idxml.findall("IdList/Id")
        print(len(ids))
        for i in ids:
            IDLIST.append(str(i.text))
    print("Endgültige Länge der IDliste: ")
    print(str(len(IDLIST)))
    print("Unique-Term Counts: ")
    print(len(set(IDLIST)))
    return IDLIST
def MeSHTermDF(queryterm):
    IDLIST = IDacq(queryterm=queryterm)
    for ID in IDLIST:
        print("Getting Article: " + ID)
        mdrequest = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=" + ID + "&retmode=xml")
        print(ID + " done")
        mdxml = ET.fromstring(mdrequest.text)
        f = mdxml.findall("*//MeshHeading/DescriptorName")
        dflist =[]
        if len(f) == 0:
            print("Keine Meshterms vorhanden")
            abstracts = ['.//AbstractText','.//Keyword','.//ArticleTitle']
            abstract = ""
            for tag in abstracts:
                for child in mdxml.findall(tag):
                        abstract+=str(child.text)
                        abstract+=" "
            doc = nlp(abstract)
            linker = nlp.get_pipe("scispacy_linker")
            entity = doc.ents
            for i in entity:
                for mesh_ent in i._.kb_ents:
                    meshinfo = linker.kb.cui_to_entity[mesh_ent[0]]
                    meshinfo = list(meshinfo)
                    del meshinfo[2:4]
                    dflist.append(meshinfo)
        elif len(f) > 0:
            print(ID, "MeshTerms vorhanden!")
    df = pd.DataFrame(dflist,columns=['MeSH Unique ID','MeSH Heading','ScopeNote'])
    df = df.drop_duplicates(subset=['MeSH Unique ID'])
    df['MeSHBrowserLink'] = 'https://meshb.nlm.nih.gov/record/ui?ui=' + df['MeSH Unique ID']
    TNlist = []
    options = Options()
    options.headless = True
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--incognito')
    options.add_argument('--disable-plugins-discovery')
    for i in df['MeSHBrowserLink']:
        driver = webdriver.Chrome('C:/webdriver/chromedriver.exe', chrome_options=options)
        print("Opening Website: "+ i)
        driver.get(i)
        element = driver.find_elements_by_xpath('//a[contains(@id,"treeNumber")]')
        elementlist = []
        for i in element:
            elementlist.append(i.text)
        print(elementlist)
        TNlist.append(elementlist)
    df['TreeNumbers'] = TNlist
    return df

if __name__ == '__main__':
    df = MeSHTermDF(queryterm="infectious diseases")
    #one can save the dataframe in csv or xlsx or whatever
    name = 'MeSHTermList.csv'
    df.to_csv(name)