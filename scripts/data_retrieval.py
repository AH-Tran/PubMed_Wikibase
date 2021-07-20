## Library Import
import requests
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, XML
import json
import re
import os
import xmltodict
import ast
import pandas as pd
from wikibaseintegrator import wbi_core, wbi_login
import spacy
import scispacy
from scispacy.linking import EntityLinker

data_path = os.path.abspath('../data/')
#file_path = os.path.

#function to get a list of all jsondicts
def IDacq(queryterm: str):
    baseurl = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?api_key=64a858580cdbab48732231789433c6dfa108&'
    retmax = 10
    database = "db=pubmed"
    query = ''
    advquery= queryterm.split()
    for i in advquery:
        query+=i
        query+="+"
    query = "term=" + query[:-1]
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
    """
    while len(IDLIST)%100000==0:
        retstart = len(IDLIST)
        print("Ziehen der nächsten " + str(retstart) + " IDs)
        idrequest = requests.get(url+"&retstart=" + str(retstart))
        print("Download fertig!")
        idxml = ET.fromstring(idrequest.text)
        ids = idxml.findall("IdList/Id")
        for i in ids:
            IDLIST.append(str(i.text))
    """
    print("Endgültige Länge der IDliste: ")
    print(str(len(IDLIST)))
    print("Unique-Term Counts: ")
    print(len(set(IDLIST)))
    return IDLIST

def dataaquisition(queryterm):
    """
    generates a list of all dictionaries with the metadata information
    Args:
        queryterm (str): simple queryterm we search for
    Returns:
        list of dict: list of dictionaries we can iterate after with the other function to upload them to the wikibase
    """
    nlp = spacy.load("en_core_sci_sm")
    nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "mesh"})
    IDLIST = IDacq(queryterm)
    dicts = []
    for ID in IDLIST:
        print("Download des Artikels: " + str(ID))
        mdrequest = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?api_key=64a858580cdbab48732231789433c6dfa108&db=pubmed&id=" + ID + "&retmode=xml")
        print("Download fertig!")
        mdxml = ET.fromstring(mdrequest.text)
        if len([a.tag for a in mdxml.iter()])>1:
            f = mdxml.findall("*//MeshHeading/DescriptorName")
            if len(f) == 0:
                print("Keine MeshTerms vorhanden")
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
                if parent is None:
                    if mdxml.find('.//PubmedArticle') is None:
                        parent = SubElement(SubElement(mdxml,'PubmedArticle'),'MedlineCitation')
                    else:
                        parent = SubElement(mdxml.find('.//PubmedArticle'),'MedlineCitation')
                else:
                    print(parent)
                children = SubElement(parent,'MeshHeadingList')
                for i in entity:
                    for mesh_ent in i._.kb_ents:
                        meshinfo = linker.kb.cui_to_entity[mesh_ent[0]]
                        Descriptor = meshinfo[0]
                        name = meshinfo[1]
                        child = XML('<MeshHeading><DescriptorName UI="'+Descriptor+'" MajorTopicYN="N">'+name+'</DescriptorName></MeshHeading>')
                        children.extend(child)
                        print("Name: ",name,type(name))
                print("ID " + ID + " besitzt jetzt MeshTerms: ",len([elem.tag for elem in parent.iter(tag="DescriptorName")]))
            elif len(f) != 0:
                print("ID " + str(ID) + " besitzt schon " + str(len(f)) + " MeshTerms")
            #List of all xml-Terms to drop INCLUDING THE ONES USED FOR MESHTERMGENERATION
            xmlparents = ['.//DateCompleted/..','.//OtherAbstract/..','.//ArticleIdList/..','.//CitationSubset/..','.//Identifier/..','.//CoiStatement/..']
            for tags in xmlparents:
                for parent in list(mdxml.iterfind(tags)):
                    for child in list(parent.iterfind(re.findall(pattern=r'\w+',string=tags)[0])):
                        parent.remove(child)
            #print(ET.tostring(mdxml))
            jsondict = json.dumps(xmltodict.parse(ET.tostring(mdxml)),indent=4,sort_keys=True,ensure_ascii=False)
            #If you want to write into a file, uncomment next two lines
            #with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),ID +'.json'),'w') as file:
            #    file.write(jsondict)
            #if you want to use a string for ongoing preprocessing or different tasks, uncomment next line, which turns the jsondict in stringformat into jsondict in dict format
            try:
                jsondict = ast.literal_eval(jsondict)
            except ValueError:
                continue
            dicts.append(jsondict)
    return dicts

def MeSHTermDF(queryterm):
    nlp = spacy.load("en_core_sci_sm")
    nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "mesh"})
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
    return df

def main():
    result = dataaquisition('infectious diseases')
    return result

if __name__ == '__main__':
    result = dataaquisition('infectious diseases') # type list containing dicts as items
    #for i in result:
    #print("Type:")
    #print(result[1])
        #with open(os.path.join(os.path.dirname(__file__), data_path), 'w') a file:
    #for i in result:
    #    with open(data_path,i +'.json', 'w') as fp:
    #        json.dump(result[i], fp, indent=4)

    with open('result0.json', 'w') as fp:
            json.dump(result[0], fp, indent=4)
    with open('result1.json', 'w') as fp:
            json.dump(result[1], fp, indent=4)
    #print(len(result))
    #print(result)
    #with open('pubmed_data.json','w') as file:
    #             file.write(result)