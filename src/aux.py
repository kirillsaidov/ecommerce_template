# module aux

# db
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


