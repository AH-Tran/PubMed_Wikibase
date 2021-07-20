## Library Import
import requests
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, XML
import json
import re
import os
import xmltodict
import ast
from wikibaseintegrator import wbi_core, wbi_login
import spacy
import scispacy
from scispacy.linking import EntityLinker
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

#function to get a list of all jsondicts
def IDacq(queryterm: str):
    """creates a List of all the Article-IDs based on the Queryterm

    Args:
        queryterm (str): String to search in Pubmed

    Returns:
        list: list of all IDs as a String
    """
    #Constants
    baseurl = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?api_key=64a858580cdbab48732231789433c6dfa108&'
    retmax = 1000
    database = "db=pubmed"
    #process the query to not have spaces but "+"
    query = ''
    advquery= queryterm.split()
    for i in advquery:
        query+=i
        query+="+"
    query = "term=" + query[:-1]
    #create the url to get the Article IDs
    url = baseurl + database + "&" + query + "&" + "retmax=" + str(retmax)

    #request IDs for searchterms and apply XML syntax
    print("Downloaden von " + str(retmax) + " Artikel-IDs!")
    idrequest = requests.get(url)
    print("Download fertig!")
    idxml = ET.fromstring(idrequest.text)

    #use IDs in XML from first query to get Metadata in XML
    IDLIST = []
    ids = idxml.findall("IdList/Id")
    for i in ids:
        IDLIST.append(str(i.text))
    #To get all the Article IDs, we check, if we the total number of IDs and if so, get the next Article IDs
    while len(IDLIST)%100000==0:
        retstart = len(IDLIST)
        print("Ziehen der nächsten " + str(retmax) + " IDs")
        idrequest = requests.get(url+"&retstart=" + str(retstart))
        print("Download fertig!")
        idxml = ET.fromstring(idrequest.text)
        ids = idxml.findall("IdList/Id")
        for i in ids:
            IDLIST.append(str(i.text))
    print("Endgültige Länge der IDliste: ")
    print(str(len(IDLIST)))
    print("Unique-Term Counts: ")
    #make the IDs Unique
    print(len(set(IDLIST)))
    return IDLIST

def dataaquisition(queryterm):
    """
    generates a list of all dictionaries with the metadata information and a list of all MeshTerms used.
    Args:
        queryterm (str): simple queryterm we search for
    Returns:
        list of dict: list of dictionaries we can iterate after with the other function to upload them to the wikibase
    """
    #Load the spacy module to create the meshterms
    nlp = spacy.load("en_core_sci_sm")
    nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "mesh"})
    #Get the list of all IDs
    IDLIST = IDacq(queryterm)
    dicts = []
    dflist = []
    timelist = []
    #Iterate over the IDLIST
    for ID in IDLIST:
        start = time.time()
        #Get the Article of the ID
        mdrequest = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?api_key=64a858580cdbab48732231789433c6dfa108&db=pubmed&id=" + ID + "&retmode=xml")
        mdxml = ET.fromstring(mdrequest.text)
        #check if the Article is empty
        if len([a.tag for a in mdxml.iter()])>1:
            #check for Mesh-Terms
            f = mdxml.findall("*//MeshHeading/DescriptorName")
            #if there are Mesh-Terms, get additional information
            if len(f) != 0:
                for i in f:
                    doc = nlp(i.text)
                    entity = doc.ents
                    for i in entity:
                        for mesh_ent in i._.kb_ents:
                            meshinfo = linker.kb.cui_to_entity[mesh_ent[0]]
                            Descriptor = meshinfo[0]
                            name = meshinfo[1]
                            c = [meshinfo[i] for i in [0,1,4]]
                            dflist.append(c)
            #if there are no Mesh-Terms, create the Meshterms
            elif len(f) == 0:
                #get the Keywords and the Title to create Meshterms
                abstracts = ['.//Keyword','.//ArticleTitle']
                abstract = ""
                for tag in abstracts:
                    for child in mdxml.findall(tag):
                            abstract+=str(child.text)
                            abstract+=" "
                doc = nlp(abstract)
                linker = nlp.get_pipe("scispacy_linker")
                entity = doc.ents
                parent = mdxml.find('.//MedlineCitation')
                #check where to put the Mesh-Terms
                if parent is None:
                    if mdxml.find('.//PubmedArticle') is None:
                        parent = SubElement(SubElement(mdxml,'PubmedArticle'),'MedlineCitation')
                    else:
                        parent = SubElement(mdxml.find('.//PubmedArticle'),'MedlineCitation')
                children = SubElement(parent,'MeshHeadingList')
                for i in entity:
                    for mesh_ent in i._.kb_ents:
                        meshinfo = linker.kb.cui_to_entity[mesh_ent[0]]
                        Descriptor = meshinfo[0]
                        name = meshinfo[1]
                        #create XML with the Mesh-Terms
                        child = XML('<MeshHeading><DescriptorName UI="'+Descriptor+'" MajorTopicYN="N">'+name+'</DescriptorName></MeshHeading>')
                        children.extend(child)
                        #append the information to the list to create the meshtermlist later
                        c = [meshinfo[i] for i in [0,1,4]]
                        dflist.append(c)
            #List of all xml-Terms to drop INCLUDING THE ONES USED FOR MESHTERMGENERATION
            xmlparents = ['.//DateCompleted/..','.//OtherAbstract/..','.//ArticleIdList/..','.//CitationSubset/..','.//AffiliationInfo/..','.//Identifier/..','.//CoiStatement/..','.//Abstract/..','.//Keyword/..']
            for tags in xmlparents:
                for parent in list(mdxml.iterfind(tags)):
                    for child in list(parent.iterfind(re.findall(pattern=r'\w+',string=tags)[0])):
                        parent.remove(child)
            jsondict = json.dumps(xmltodict.parse(ET.tostring(mdxml)),indent=4,sort_keys=True,ensure_ascii=False)
            #If you want to write the json into files, uncomment next two lines
            #with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),ID +'.json'),'w') as file:
            #    file.write(jsondict)
            #if you want to use a string for ongoing preprocessing or different tasks, uncomment next line, which turns the jsondict in stringformat into jsondict in dict format
            try:
                jsondict = ast.literal_eval(jsondict)
            except ValueError:
                continue
            dicts.append(jsondict)
            end = time.time()
            timelist.append(end-start)
            if IDLIST.index(ID)%10==0:
                print("Download des Artikels:",str(IDLIST.index(ID)+1)+"/"+str(len(IDLIST)),"Est. time left:",time.strftime('%M:%S',time.gmtime(int(sum(timelist)/len(timelist)*(len(IDLIST)-IDLIST.index(ID))))),"Min")
        
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
    options.add_argument('log-level=3')
    timelist = []
    urllist = df['MeSHBrowserLink'].tolist()
    for i in urllist:
        n = i
        start = time.time()
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(i)
        time.sleep(3)
        element = driver.find_elements_by_xpath('//a[contains(@id,"treeNumber_")]')
        elementlist = []
        for i in element:
            elementlist.append(i.text)
        TNlist.append(elementlist)
        end = time.time()
        timelist.append(end-start)
        print("MeSHTerm:",str(urllist.index(n)+1)+"/"+str(len(urllist)),"Est. time left:",time.strftime('%H:%M:%S',time.gmtime(int(sum(timelist)/len(timelist)*(len(urllist)-urllist.index(n))))),"Hours")
    df['TreeNumbers'] = TNlist
    df.to_csv('meshtermlist.csv')
    return dicts

def main(queryterm):
    result = dataaquisition(queryterm)
    return result

if __name__ == '__main__':
    main('infectious diseases')