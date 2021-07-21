import json
import pandas as pd

def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct

def jsoninsert():
    # Opening JSON file
    with open('result0.json') as json_file:
        data0 = json.load(json_file)
    with open('result1.json') as json_file:
        data1 = json.load(json_file)

    #safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article')
    title = safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'ArticleTitle')
    date = safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'ArticleDate', 'Day') + '.' + \
                safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'ArticleDate', 'Month') + '.' + \
                safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'ArticleDate', 'Year')
    author_list = safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'AuthorList', 'Author')
    for a in author_list:
       safeget(a, 'LastName')+ ',' + safeget(a, 'ForeName')
    language = safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'Language')
    publication_type = safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'PublicationTypeList', 'PublicationType', '#text') #try except
    journal_title = safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'Journal', 'Title')#
    journal_issn = safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'Journal', 'ISSN', '#text')#
    journal_date = safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'Journal', 'JournalIssue', 'PubDate', 'Day') + '.' + \
                safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'Journal', 'JournalIssue', 'PubDate', 'Month') + '.' + \
                safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'Article', 'Journal', 'JournalIssue', 'PubDate', 'Year')#
    NLM_ID = safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'MedlineJournalInfo', 'NlmUniqueID')#
    PMID = safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'PMID', '#text')

    mesh_list = safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'MeshHeadingList', 'DescriptorName')
    for m in mesh_list:
        safeget(m, '@UI')
    
    print(author_list)

def csv_search():
    df = pd.read_csv('meshtermlist.csv')
    
    with open('result0.json') as json_file:
        data0 = json.load(json_file)

    #r =df.loc[df['MeSH Unique ID'] == 'D005208']
    #r2 = int(r.index.values)
    #print(r2)
    
    #r= df[df['MeSH Unique ID'] == 'D016267'].index[0]
    #print(r+1)
    #search for D016267 (external fixators)   

    mesh_list = safeget(data0, 'PubmedArticleSet','PubmedArticle', 'MedlineCitation', 'MeshHeadingList', 'DescriptorName')
    for m in mesh_list:
        if ( df[df['MeSH Unique ID'] == safeget(m, '@UI')].index[0]):
            r= df[df['MeSH Unique ID'] == safeget(m, '@UI')].index[0] + 1
            print('Q' + str(r))
        else:
            continue
    

if __name__ == '__main__':
    jsoninsert()
    #csv_search()

