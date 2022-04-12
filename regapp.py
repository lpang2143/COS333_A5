#-----------------------------------------------------------------------
# regapp.py
# Author: Hervé Ishimwe & Louis Pang
#-----------------------------------------------------------------------

from flask import Flask, request, make_response, redirect
from flask import render_template, url_for
from search import overview_search
from details import detail

#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='.')

#-----------------------------------------------------------------------

@app.route('/', methods=['GET'])
@app.route('/homepage', methods=['GET'])
def homepage():
    tuple = request.cookies.get('prev_tuple')
    if tuple == None:
        dept = request.args.get('dept')
        num = request.args.get('num')
        area = request.args.get('area')
        title = request.args.get('title')
        tuple = (dept, num, area, title)

    classes = overview_search(tuple)

    html = render_template('homepage.html',
        class_list = classes)
    response = make_response(html)
    response.set_cookie('prev_tuple', tuple)
    return response

#-----------------------------------------------------------------------

@app.route('/class_details', methods=['GET'])
def class_details():

    classid = request.args.get('classid')

    details_list = detail(classid)

    html = render_template('searchform.html',
        details = details_list)
    response = make_response(html)
    return response