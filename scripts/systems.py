import os
import time
#import create_properties 
#import data_retrieval
import create_mesh_items
#import create_items_wd


if __name__ == "__main__":
    """
    Executes all important scripts for the creation, dataacquisition and ingestion of the wikibase instance
    Args:
        None
    Returns:
        None
    """
    time0 = time.time()

    #execute scripts
    #create_properties.first_property_setup() # works
    #metadata = data_retrieval.main()
    create_mesh_items.main('meshtermlist.csv') # works
    #create_items_wd.main(metadata)

    print('Total time in seconds: ', time.time() - time0)