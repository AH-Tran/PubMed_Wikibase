import json

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
    
    #print(mesh_list)

if __name__ == '__main__':
    jsoninsert()


