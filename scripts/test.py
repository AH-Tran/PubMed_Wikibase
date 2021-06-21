# Importing the required libraries
import xml.etree.ElementTree as Xet
import pandas as pd
  
mydata = pd.read_csv("pubmed_data.csv")
print(mydata.loc[0].at['PubmedArticle_MedlineCitation_Owner'])
#print(mydata.at[0,'PubmedArticle_MedlineCitation_Owner'])
for index, row in mydata.iterrows():
    print(mydata.loc[index].at['PubmedArticle_MedlineCitation_Article_ArticleTitle'])
    #print(index)
#    print(row)
    print("*** END ITERATION ***")
#print(mydata.iloc[0]['PubmedArticle_MedlineCitation_Article_ArticleTitle'])



