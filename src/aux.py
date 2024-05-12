# module aux

# db
from bson.objectid import ObjectId
from pymongo.database import Database
from elasticsearch import Elasticsearch


def aux_db_add_category(db: Database, category: str):
    col = db['info']
    entry = col.find_one({'categories': {'$exists': 1}})
    if entry:
        col.update_one(entry, {
            '$set': {'categories': list(set(entry['categories'] + [category]))}
        })
    else:
        col.insert_one({
            'categories': [category],
        })


def aux_db_add_group(db: Database, group: str):
    col = db['info']
    entry = col.find_one({'groups': {'$exists': 1}})
    if entry:
        col.update_one(entry, {
            '$set': {'groups': list(set(entry['groups'] + [group]))}
        })
    else:
        col.insert_one({
            'groups': [group],
        })


def aux_db_add_brand(db: Database, brand: str):
    col = db['info']
    entry = col.find_one({'brands': {'$exists': 1}})
    if entry:
        col.update_one(entry, {
            '$set': {'brands': list(set(entry['brands'] + [brand]))}
        })
    else:
        col.insert_one({
            'brands': [brand],
        })


def aux_db_rem_category(db: Database, category: str):
    col = db['info']
    entry = col.find_one({'categories': {'$exists': 1}})
    if entry:
        col.update_one(entry, {
            '$set': {'categories': list(set(entry['categories']) - set([category]))}
        })


def aux_db_rem_group(db: Database, group: str):
    col = db['info']
    entry = col.find_one({'groups': {'$exists': 1}})
    if entry:
        col.update_one(entry, {
            '$set': {'groups': list(set(entry['groups']) - set([group]))}
        })


def aux_db_rem_brand(db: Database, brand: str):
    col = db['info']
    entry = col.find_one({'brands': {'$exists': 1}})
    if entry:
        col.update_one(entry, {
            '$set': {'brands': list(set(entry['brands']) - set([brand]))}
        })


def aux_db_get_categories(db: Database) -> list:
    col = db['info']
    entry = col.find_one({'categories': {'$exists': 1}})
    if entry: 
        lst: list = entry['categories']
        lst.sort()
        return lst
    else: 
        return list() 


def aux_db_get_groups(db: Database) -> list:
    col = db['info']
    entry = col.find_one({'groups': {'$exists': 1}})
    if entry:
        lst: list = entry['groups']
        lst.sort()
        return lst
    else: 
        return list()


def aux_db_get_brands(db: Database) -> list:
    col = db['info']
    entry = col.find_one({'brands': {'$exists': 1}})
    if entry:
        lst: list = entry['brands']
        lst.sort()
        return lst
    else: 
        return list()


def aux_db_add_item(db: Database, item: dict):
    # add categories
    aux_db_add_category(db, item['category'])

    # add groups
    aux_db_add_group(db, item['group'])

    # add brands
    aux_db_add_brand(db, item['brand'])

    # add item
    col = db['items']
    entry = col.find_one({'title': item['title']})
    if entry:
        col.update_one(entry, {
            '$set': item,
        })
    else:
        col.insert_one(item)


def aux_db_rem_item(db: Database, id: ObjectId):
    col = db['items']
    entry = col.find_one({'_id': id})
    if entry:
        col.delete_one({'_id': id})


def aux_db_get_items(db: Database) -> list:
    col = db['items']
    items = list(col.find({}))

    # convert object id to string
    for item in items: 
        item['id'] = str(item['_id'])
        del item['_id']

    return items


def aux_db_find_item(db: Database, id: ObjectId) -> dict:
    col = db['items']
    item = col.find_one({'_id': id})
    if item: item['id'] = str(item['_id']) 
    return item


def aux_chunks(lst, step):
    """Yield successive n-sized chunks from lst.

    Note:
        use `list(aux_chunks(list, step))` to convert to list 
    """
    for i in range(0, len(lst), step):
        yield lst[i:i + step]


def aux_es_create_index(es: Elasticsearch, index: str, mappings: dict) -> bool:
    """Create index if does not exist

    Args:
        es (Elasticsearch): es engine
        index (str): index string
        mappings (dict): mappings

    Returns:
        bool: True upon success, False if already exists
    """
    if not es.indices.exists(index=index): 
        es.indices.create(index=index, mappings=mappings)
        return True
    return False


def aux_es_add_docs(es: Elasticsearch, index: str, documents: list):
    """Add documents to engine

    Args:
        es (Elasticsearch): es engine
        index (str): index string
        documents (list): documents
    """
    for idx, doc in enumerate(documents):
        es.index(index=index, id=idx, body=doc)


def aux_es_search(es: Elasticsearch, index: str, search: str, get_docs: bool = True) -> list:
    """Search

    Args:
        es (Elasticsearch): es engine
        index (str): index string
        search (str): search string
        get_docs (bool, optional): get original documents instead of search response document. Defaults to True.

    Returns:
        list: list of documents

    Note:
        mappings: {
            "properties": {
                "title": {"type": "text", "analyzer": "standard"},
                "content": {"type": "text", "analyzer": "standard"},
                "price": {"type": "integer"},
            }
        }
    """
    resp = es.search(index=index, body={
        'query': {
            'match': {
                'content': search
            }
        }
    })

    # find all hits
    hits = []
    for hit in resp['hits']['hits']:
        hits.append(hit['_source'] if get_docs else hit)

    return hits


def aux_es_update_index_from_db(es: Elasticsearch, index: str, db: Database):
    items = aux_db_get_items(db)
    aux_es_add_docs(es, index, items)



