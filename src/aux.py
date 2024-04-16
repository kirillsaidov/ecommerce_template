# module aux

# db
from bson.objectid import ObjectId
from pymongo.database import Database

# local
import data


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
    return entry['categories'] if entry else list()


def aux_db_get_groups(db: Database) -> list:
    col = db['info']
    entry = col.find_one({'groups': {'$exists': 1}})
    return entry['groups'] if entry else list()


def aux_db_get_brands(db: Database) -> list:
    col = db['info']
    entry = col.find_one({'brands': {'$exists': 1}})
    return entry['brands'] if entry else list()


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

    return items


def aux_db_find_item(db: Database, id: ObjectId) -> dict:
    col = db['items']
    entry = col.find_one({'_id': id})
    return entry


def aux_chunks(lst, step):
    """Yield successive n-sized chunks from lst.

    Note:
        use `list(aux_chunks(list, step))` to convert to list 
    """
    for i in range(0, len(lst), step):
        yield lst[i:i + step]


