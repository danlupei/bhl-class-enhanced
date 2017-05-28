# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import logging
import socket

from flask import Flask, request, render_template, redirect, send_from_directory, url_for
from google.cloud import datastore

from cenh import *
from functools import reduce

app = Flask(__name__)


def is_ipv6(addr):
    """Checks if a given address is an IPv6 address."""
    try:
        socket.inet_pton(socket.AF_INET6, addr)
        return True
    except socket.error:
        return False

@app.route('/')
def index():
    
    url_for('static', filename='layout/styles/layout.css')
    url_for('static', filename='layout/scripts/jquery.placeholder.min.js')
    url_for('static', filename='layout/scripts/jquery.min.js')
    url_for('static', filename='layout/scripts/script.js')
    url_for('static', filename='layout/scripts/jquery.backtotop.js')
    url_for('static', filename='layout/scripts/jquery.mobilemenu.js')
    url_for('static', filename='images/demo/backgrounds/background.jpg')
    
    ds = datastore.Client()

    class_query = ds.query(kind='class')
    class_results = ['Course name: {}. Title: {}. Concepts: {}'.format(x['course'], x.get('title', 'XYZ'),
        '\n'.join(['{}. {}'.format(i+1, c) for i, c in enumerate(x['concepts'])])) for x in class_query.fetch()]
    
    output = class_results

    #return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    return render_template('index.html', classes=output)


@app.route('/add-chinese')
def add_chinese():
    ds = datastore.Client()
    
    add_class_with_file(ds, 'Tsinghua Chinese', 'Intro to Chinese', 'tsinghua-chinese.txt')
    
    return redirect('/')
    

@app.route('/add-sample')
def add_sample():
    ds = datastore.Client()
    
    add_class_with_file(ds, 'sample', 'sample', 'Tsinghua Chinese', 'tsinghua-chinese.txt')
    
    return redirect('/')
    

@app.route('/add-class', methods=['POST', 'GET'])
def add_class():
    ds = datastore.Client()
    if request.method == 'POST':
        title = request.form.get('title', 'wat')
        #course_id = request.form['course_id']
        content = request.files['content_file']
        content.save(content.filename)
        filename = content.filename
        class_id = filename.split('.')[0]
    
        add_class_with_file(ds, class_id, 'abc', title, filename) #TODO:make this work with courses
        return redirect('/')
    return render_template('newclass.html')
    
    
@app.route('/add-course', methods=['POST', 'GET'])
def add_course():
    ds = datastore.Client()
    course = datastore.Entity(key=ds.key('course'))
    course.update({
    	'course_id': 'abc',
    	'title': 'Abecadło'
    })
    
    ds.put(course)
    
    return redirect('/')


@app.route('/save-review/<course_id>/<class_id>', methods=['POST'])
def save_review(course_id, class_id):
    ds = datastore.Client()
    review = datastore.Entity(key=ds.key('review'))
    print(['checkbox' + str(id) for id in range(len(get_class(ds, class_id)['concepts']))])
    checked = [request.form.get(bname, 'unchecked') for bname in ['checkbox' + str(id) for id in range(len(get_class(ds, class_id)['concepts']))]]
    print(checked)
    #checked = [False, True, False, True, False]
    def asdf(b):
    	if b == False:
    	    return 0
    	return 1
    review.update({
    	'course_id': course_id,
    	'class_id': class_id,
    	'problems': list(map(lambda b: 1 if b == 'on' else 0, checked)),
    	'rating': request.form['rating'],
    	'comments': request.form.get('comments', '')
    })
    print(review['problems'])
    
    ds.put(review)
    return redirect('/')
    
@app.route('/add-teacher', methods=['POST'])
def add_teacher():
    return redirect('/')
    
    
@app.route('/show-course/<course_id>')
def show_course(course_id):
    ds = datastore.Client()
    course_query = ds.query(kind='course')
    course_query.add_filter('course_id', '=', course_id)


@app.route('/show-courses')
def show_courses():
    ds = datastore.Client()
    course_query = ds.query(kind='course')
    
    return render_template('courses.html', obj=['Identyfikator kursu: {course_id}. Tytuł kursu: {title}'.format(**e) for e in course_query.fetch()])
    
    
@app.route('/show-class/<course>/<class_id>', methods=['POST', 'GET'])
def show_class(course, class_id):
    ds = datastore.Client()
    class_query = ds.query(kind='class')
    class_query.add_filter('class_id', '=', class_id)
    class_to_show = [entity for entity in class_query.fetch()][0]
    
    return render_template('review.html', concepts=enumerate(class_to_show['concepts']))


@app.route('/show-stats/<course_id>/<class_id>')
def show_stats(course_id, class_id):
    ds = datastore.Client()
    reviews = get_reviews(ds, class_id)
    class_ = get_class(ds, class_id)
    
    sum_of_problems = reduce(lambda acc, l: [a+l_i for a, l_i in zip(acc, l)], [rev['problems'] for rev in reviews])
    concepts = class_['concepts']
    
    avg = sum([int(rev['rating']) for rev in reviews]) / float(len(reviews))
    cmms = [rev['comments'] for rev in reviews if rev['comments']]
    dict_of_problems = {conc: sum_of_problems[lp] for lp, conc in enumerate(concepts)}
    return render_template('stats.html', obj=dict_of_problems, count=len(reviews), rating=avg, comments=cmms)
    

@app.route('/clear-db')
def clear_db():
    ds = datastore.Client()
    delete_all(ds)
    
    return redirect('/')


#@app.route('/layout/scripts/<path:path>')
#def send_js(path):
#    return send_from_directory('scripts', path)


#@app.route('/layout/styles/<path:path>')
#def send_css(path):
#    return send_from_directory('styles', path)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)

