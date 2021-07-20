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
    df1 = pd.DataFrame([data0])
    df2 = pd.DataFrame([data1])

    for key in data0:
        if key in data1:
            data0[key].update(data1[key])
    
    with open('result_union.json', 'w') as output_file:
        json.dump(df1, output_file)
    #MergeJson = pd.concat([df1, df2])
    #MergeJson.to_json("result_union.json")  

def merge_JsonFiles(filename):
    result = list()
    for f1 in filename:
        with open(f1, 'r') as infile:
            result.extend(json.load(infile))

    with open('result_union.json', 'w') as output_file:
        json.dump(result, output_file)

if __name__ == '__main__':
    jsoninsert()

    #files=['result0.json','result1.json']
    #merge_JsonFiles(files)


