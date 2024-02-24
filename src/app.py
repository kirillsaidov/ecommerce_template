# module app

from flask import Flask, render_template, request, url_for, flash, redirect
import data
import aux

app = Flask(__name__)
app.config['SECRET_KEY'] = '0123456789'
preload_data = {
    'about': open('static/info/about.txt', 'r').read().split('\n'),
    'footer': open('static/info/footer.txt', 'r').read(),
}


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
    return render_template('about.html', data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
    })

@app.route('/payment')
def payment():
    return render_template('about.html', data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
    })

@app.route('/delivery')
def delivery():
    return render_template('about.html', data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
    })

@app.route('/collaboration')
def collaboration():
    return render_template('about.html', data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
    })

@app.route('/contacts')
def contacts():
    return render_template('about.html', data={
        'footer': preload_data['footer'],
        'about': preload_data['about'],
    })


# @app.route('/<int:stud_id>')
# def stud(stud_id):
#     stud = aux.get_stud(stud_id)
#     return render_template('stud.html', stud=stud)


# @app.route('/create', methods=('GET', 'POST'))
# def create():
#     if request.method == 'POST':
#         name = request.form['name']
#         age = request.form['age']
#         spec = request.form['spec']
#         year = request.form['year']

#         if not name:
#             flash('Title is required!')
#             if not age:
#                 flash('Title is required!')
#                 if not spec:
#                     flash('Title is required!')
#                     if not year:
#                         flash('Title is required!')
#         else:
#             data.studs.append({
#                 'name': name,
#                 'year': year,
#                 'age' : age,
#                 'spec': spec,
#             })
#             return redirect(url_for('index'))

#     return render_template('create.html')


if __name__ == "__main__":
    app.run(debug=True)

