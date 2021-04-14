from wikibaseintegrator import wbi_core

def main():
    my_first_wikidata_item = wbi_core.ItemEngine(item_id='Q5')

    # to check successful installation and retrieval of the data, you can print the json representation of the item
    print(my_first_wikidata_item.get_json_representation())

if __name__ == '__main__':
    main()