# module app

# system
import os
import io
from datetime import datetime, timedelta

# web
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.utils import secure_filename

# db
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
        return redirect('admin_item_add')
    else:
        return render_template('admin.html', login=app.login, data={
            'footer': preload_data['footer'],
            'about': preload_data['about'],
        })


@app.route('/admin_item_add', methods=('GET', 'POST'))
def admin_item_add():
    if not app.login:
       return redirect('admin')

    # process request
    if request.method == 'POST':
        if request.form.get('button_item') == 'add':
            return redirect('admin_item_add_one')

    return render_template('admin_item_add.html', login=app.login, data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
    })        


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


if __name__ == "__main__":
    try:
        startup()
        app.run(debug=True)
    except Exception as e:
        print(str(e))
    finally:
        shutdown()

