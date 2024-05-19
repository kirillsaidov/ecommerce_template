# module aux

# db
from bson.objectid import ObjectId
from pymongo.database import Database

# semantic search
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# translate to english (semantic search works best with english)
from deep_translator import GoogleTranslator


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
        # delete item
        col.delete_one({'_id': id})

        # get updated categories, groups, brands
        items = aux_db_get_items(db)
        update_data = [
            list(set(map(lambda x: x['category'], items))),
            list(set(map(lambda x: x['group'], items))),
            list(set(map(lambda x: x['brand'], items))),
        ]
        
        # find entries
        col = db['info']
        entries = [
            col.find_one({'categories': {'$exists': 1}}),
            col.find_one({'groups': {'$exists': 1}}),
            col.find_one({'brands': {'$exists': 1}}),
        ]

        # update
        for data, entry, name in zip(update_data, entries, ['categories', 'groups', 'brands']):
            col.update_one(entry, {
                '$set': {name: data}
            })
        
        
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


def aux_semantic_search(model: SentenceTransformer, query: str, items: list[dict]) -> list[dict]:
    """Performs semantic search and returns relevant items.

    Args:
        model (SentenceTransformer): initialized model
        query (str): query string
        items (list[dict]): data items

    Returns:
        list[dict]: relevant items
    
    Note:
        if len(query) == 0, returns the initial items
    """
    # check empty query
    if not len(query): 
        return items
    else: 
        query = GoogleTranslator(source='auto', target='en').translate(query)
    
    # convert list of dict to appropriate format
    for item in items: 
        item['combined'] = '\n'.join([item['title'], item['description']])
    
    # create df
    df = pd.DataFrame.from_dict(items)

    # get passages for search
    passages = df['title'].values.tolist()

    # search
    query_embedding = model.encode(query, convert_to_tensor=True)
    passage_embedding = model.encode(passages, convert_to_tensor=True)
    simscore = util.pytorch_cos_sim(query_embedding, passage_embedding)[0].cpu().tolist()
    
    # update df
    df['simscore'] = simscore
    df.sort_values(by='simscore', ascending=False, inplace=True)
    items = df.to_dict('records')

    return items



