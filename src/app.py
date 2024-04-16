# module app

# system
import os
import io
from datetime import datetime, timedelta

# web
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.utils import secure_filename

# db
from bson.objectid import ObjectId
from pymongo import MongoClient

# data processing
import numpy as np
import pandas as pd

# custom
import data
import aux

app = Flask(__name__)
app.config['ADMIN_USERNAME'] = 'admin'
app.config['ADMIN_PASSWORD'] = 'admin'
app.config['ADMIN_SESSION_TIME'] = timedelta(hours=3)
app.config['ADMIN_SESSION_LAST'] = datetime.now()
app.config['SECRET_KEY'] = '0123456789'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.login = True
preload_data = {
    'about': open('static/info/about.txt', 'r').read().split('\n'),
    'footer': open('static/info/footer.txt', 'r').read(),
}


def startup():
    app.mongo_client = MongoClient('mongodb://localhost:27017/')
    app.db = app.mongo_client['config']


def shutdown():
    if app.mongo_client:
        app.mongo_client.close()


@app.route('/')
def index():
    return render_template('index.html', data={
        'footer': preload_data['footer'],
    })


@app.route('/about')
def about():
    return render_template('about.html', data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
    })


@app.route('/brands')
def brands():
    return render_template('brands.html', data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
    })


@app.route('/payment')
def payment():
    return render_template('payment.html', data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
    })


@app.route('/delivery')
def delivery():
    return render_template('delivery.html', data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
    })


@app.route('/collaboration')
def collaboration():
    return render_template('collaboration.html', data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
    })


@app.route('/contacts')
def contacts():
    return render_template('contacts.html', data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
    })


@app.route('/admin', methods=('GET', 'POST'))
def admin():
    # authorize
    if request.method == 'POST':
        if app.config['ADMIN_USERNAME'] == request.form['username'] and app.config['ADMIN_PASSWORD'] == request.form['password']:
            app.login = True
            app.config['ADMIN_SESSION_LAST'] = datetime.now()
    elif datetime.now() - app.config['ADMIN_SESSION_LAST'] > app.config['ADMIN_SESSION_TIME']:
        app.login = False

    # check if login and redirect if neccessary
    if app.login:
        return redirect(url_for('admin_item_view', page_num=0))
    else:
        return render_template('admin.html', login=app.login, data={
            'footer': preload_data['footer'],
            'about': preload_data['about'],
        })


@app.route('/admin_item_view/<int:page_num>', methods=('GET', 'POST'))
def admin_item_view(page_num: int):
    if not app.login:
       return redirect('admin')
    
    # init
    sort_by_default = {
        'select_category': 'Сортировка по категории',
        'select_group': 'Сортировка по группе',
        'select_brand': 'Сортировка по бренду',
        'select_price': 'Сортировка по цене',
    }
    sort_by = dict(sort_by_default)
    
    # process request
    if request.method == 'POST':
        for key in sort_by.keys():
            if len(request.form[key]):
                sort_by[key] = request.form[key]

    # init pages info
    page_info = {
        'items_per_page': 6,
        'items_per_row': 3,
    }

    # get all items
    items = aux.aux_db_get_items(app.db)

    # sort items 
    for key in sort_by.keys():
        if sort_by[key] != sort_by_default[key]:
            if key == 'select_price':
                items = sorted(items, key=lambda x: x['price'], reverse=sort_by[key] != 'С начала дешевле')
            else:
                items = list(filter(
                    lambda x: x[key.split('_')[-1]] == sort_by[key], items
                ))

    # split into pages
    items_split_page = list(aux.aux_chunks(items, page_info['items_per_page']))

    # split page content into rows
    items_split_row = list()
    for items_page in items_split_page:
        items_split_row.append(list(aux.aux_chunks(items_page, page_info['items_per_row'])))

    # update data
    page_num = page_num if page_num < len(items_split_row) else len(items_split_row)-1 
    page_info.update({
        'page_num': page_num,
        'page_num_max': len(items_split_page),
        'items': items_split_row[page_num],
    })

    return render_template('admin_item_view.html', login=app.login, data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
        'select_category': aux.aux_db_get_categories(app.db),
        'select_group': aux.aux_db_get_groups(app.db),
        'select_brand': aux.aux_db_get_brands(app.db),
        'sort_by': sort_by,
    }, page_info=page_info)        


@app.route('/admin_item_remove/<string:id>')
def admin_item_remove(id: str):
    if not app.login:
       return redirect('admin')
    
    # remove object
    aux.aux_db_rem_item(app.db, ObjectId(id))

    return redirect(url_for('admin_item_view', page_num=0)) 


@app.route('/admin_item_add_one', methods=('GET', 'POST'))
def admin_item_add_one():
    if not app.login:
       return redirect('admin')
    
    # process request
    if request.method == 'POST':
        item_info = {
            'title': request.form['title'],
            'price': request.form['price'],
            'description': request.form['description'],
            'category': request.form['select_category'],
            'group': request.form['select_group'],
            'brand': request.form['select_brand'],
            'pic1': request.form['pic1'],
            'pic2': request.form['pic2'],
            'pic3': request.form['pic3'],
        }
        aux.aux_db_add_item(app.db, item=item_info)

        # reload page form with empty fields
        return redirect('admin_item_add_one')

    return render_template('admin_item_add_one.html', login=app.login, data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
        'select_category': aux.aux_db_get_categories(app.db),
        'select_group': aux.aux_db_get_groups(app.db),
        'select_brand': aux.aux_db_get_brands(app.db),
    })


@app.route('/admin_item_add_excel', methods=('GET', 'POST'))
def admin_item_add_excel():
    if not app.login:
        return redirect('admin')

    # process request
    if request.method == 'POST':
        # save file
        file_io = io.BytesIO()
        file = request.files['file']
        file.save(file_io)

        # read to pandas
        df = pd.read_excel(file_io)
        for i in range(len(df)):
            # convert row to dict
            item = df.iloc[i].to_dict()

            # replace nan
            for key in item.keys():
                if pd.isna(item[key]): item[key] = ''

            # validate (title is unique)
            aux.aux_db_add_item(app.db, item)
            

    return render_template('admin_item_add_excel.html', login=app.login, data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
    })


@app.route('/admin_constructor', methods=('GET', 'POST'))
def admin_constructor():
    if not app.login:
       return redirect('admin') 
    
    if request.method == 'POST':
        if 'category' in request.form:
            form_category = request.form['category']
            if len(form_category):
                aux.aux_db_add_category(app.db, form_category)
        if 'group' in request.form:
            form_group = request.form['group']
            if len(form_group):
                aux.aux_db_add_group(app.db, form_group)
        if 'brand' in request.form:
            form_brand = request.form['brand']
            if len(form_brand):
                aux.aux_db_add_brand(app.db, form_brand)
        if 'select_category' in request.form:
            form_select_category = request.form['select_category']
            if len(form_select_category):
                aux.aux_db_rem_category(app.db, form_select_category)
        if 'select_group' in request.form:
            form_select_group = request.form['select_group']
            if len(form_select_group):
                aux.aux_db_rem_group(app.db, form_select_group)
        if 'select_brand' in request.form:
            form_select_brand = request.form['select_brand']
            if len(form_select_brand):
                aux.aux_db_rem_brand(app.db, form_select_brand)

    return render_template('admin_constructor.html', login=app.login, data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
        'select_category': aux.aux_db_get_categories(app.db),
        'select_group': aux.aux_db_get_groups(app.db),
        'select_brand': aux.aux_db_get_brands(app.db),
    })


@app.route('/item_view/<string:id>')
def item_view(id: str):
    return render_template('item_view.html', data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
    }, item=aux.aux_db_find_item(app.db, ObjectId(id)))


if __name__ == "__main__":
    try:
        startup()
        app.run(debug=True)
    except Exception as e:
        print(str(e))
    finally:
        shutdown()

