import os
import time
import create_properties 
import data_retrieval
import create_mesh_items
import create_items_wd


if __name__ == "__main__":
    """
    Executes all important scripts for the creation, dataacquisition and ingestion of the wikibase instance
    Args:
        retmax (int): The number of documents to extract from PubMed
        queryterm (str): simple queryterm we search for
    Returns:
        list of dict: list of dictionaries we can iterate after with the other function to upload them to the wikibase
    """
    retmaximum = 500
    queryterm ='infectious diseases'
    time0 = time.time()

    # Execute scripts
    create_properties.first_property_setup()
    metadata = data_retrieval.main(retmaximum, queryterm)
    create_mesh_items.main('meshtermlist.csv')
    create_items_wd.main(metadata)

    print('Total time in seconds: ', time.time() - time0)