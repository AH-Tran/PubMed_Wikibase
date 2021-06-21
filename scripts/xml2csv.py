import xml.etree.ElementTree as ETree
import pandas as pd
import xml_to_df as xml_to_df

def manual_convert():
    # give the path where you saved the xml file
    # inside the quotes
    xmldata = 'pubmed_data.xml'
    prstree = ETree.parse(xmldata)
    root = prstree.getroot()
    
    # print(root)
    store_items = []
    all_items = []
    
    for elem in root.iter('PubmedArticle'):

        title = elem.find('ArticleTitle').text
        abstract = elem.find('AbstractText').text
        author = elem.find('Author').text
        pubmed_id = elem.find('PMID').text
        pubdate = elem.find('PubDate').text
        mesh_heading = elem.find('MeshHeading').text
        mesh_descriptor_id = elem.attrib.get('slNo')

        store_items = [title, abstract, author, pubmed_id, pubdate, mesh_heading, mesh_descriptor_id]
        all_items.append(store_items)
    
    xmlToDf = pd.DataFrame(all_items, columns=[
    'SL No', 'ITEM_NUMBER', 'PRICE', 'QUANTITY', 'DISCOUNT'])
    
    print(xmlToDf.to_string(index=False))

if __name__ == "__main__":
    df = xml_to_df.convert_xml_to_df("pubmed_data.xml")
    df.to_csv('pubmed_data.csv')
    #print(df.head())
    print("done")