# Importing the required libraries
import xml.etree.ElementTree as Xet
import pandas as pd
  
cols = ["title", "abstract", "author", "pubmed id", "publication date", "mesh descriptor id"]
rows = []
  
# Parsing the XML file
xmlparse = Xet.parse('pubmed_data.xml')
#root = xmlparse.getroot()
for elem in xmlparse.iter:
    title = elem.find("ArticleTitle").text
    abstract = elem.find("AbstractText").text
    author = elem.find("Author").text
    pubmed_id = elem.find("PMID").text
    pubdate = elem.find("PubDate").text
    mesh = elem.find("MeshHeading").text
  
    rows.append({"title": title,
                 "abstract": abstract,
                 "author": author,
                 "pubmed id": pubmed_id,
                 "publication": pubdate,
                 "mesh descriptor id": mesh})
  
df = pd.DataFrame(rows, columns=cols)
  
# Writing dataframe to csv
df.to_csv('output.csv')