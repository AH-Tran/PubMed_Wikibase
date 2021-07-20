# Importing the required libraries
import xml.etree.ElementTree as Xet
import pandas as pd
# importing the module
import json

def test():
    mydata = pd.read_csv("pubmed_data.csv")
    print(mydata.loc[0].at['PubmedArticle_MedlineCitation_Owner'])
    #print(mydata.at[0,'PubmedArticle_MedlineCitation_Owner'])
    for index, row in mydata.iterrows():
        print(mydata.loc[index].at['PubmedArticle_MedlineCitation_Article_ArticleTitle'])
        #print(index)
    #    print(row)
        print("*** END ITERATION ***")
    #print(mydata.iloc[0]['PubmedArticle_MedlineCitation_Article_ArticleTitle'])

def jsoninsert():
    # Opening JSON file
    with open('result0.json') as json_file:
        data0 = json.load(json_file)
    with open('result1.json') as json_file:
        data1 = json.load(json_file)
        # Print the type of data variable
        print("Type:", type(data0))
        print(data0)
    data0.update(data1)
    with open('result_union.json', 'w') as fp:
            json.dump(data0, fp, indent=4)

if __name__ == '__main__':
    jsoninsert()