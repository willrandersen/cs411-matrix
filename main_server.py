from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from flask_heroku import Heroku

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://hccxcbaxkgmbjg:3fd3e1d41f6d20981c7ae46c61d256393dfdf67720c3f825066b2760e89856be@ec2-52-86-73-86.compute-1.amazonaws.com:5432/d7jcothqvc546b"
app.config["MONGO_URI"] = "mongodb://heroku_bm1s8r3b:ggka37atqhdqaqlv3j7658434p@ds249428.mlab.com:49428/heroku_bm1s8r3b"
db = SQLAlchemy(app)

@app.route('/dash', methods=['GET'])
def load_main():
    file_in = open('HTML_Pages/main_dash.html')
    html_template = file_in.read()
    file_in.close()

    file_in = open("SQL_commands/dashboard.sql")
    sql_query = file_in.read()
    file_in.close()

    try:
        res = db.engine.execute(sql_query)
    except:
        return "Failed"

    resultset = []
    for row in res:
        resultset.append(dict(row))
    return html_template.format(resultset[0]["firstname"], resultset[0]["lastname"], resultset[0]["id"], resultset[1]["firstname"], resultset[1]["lastname"], resultset[1]["id"], resultset[2]["firstname"], resultset[2]["lastname"], resultset[2]["id"])

@app.route('/update', methods=['DELETE'])
def deleteFromDatabase():
    template = open("SQL_commands/delete.sql")
    query = template.read().format(request.form["id"])
    template.close()
    try:
        res = db.engine.execute(query)
    except:
        return "Failed", 400
    return "Success"

@app.route('/update', methods=['POST'])
def changeToDatabase():
    template = open("SQL_commands/update.sql")
    query = template.read().format(request.form["firstname"], request.form["lastname"], request.form["gender"],
                                   request.form["age"], request.form["height"], request.form["weight"], request.form["id"])
    template.close()
    try:
        res = db.engine.execute(query)
    except:
        return "Failed", 400
    return "Success"

@app.route('/update', methods=['PUT'])
def addToDatabase():
    template = open("SQL_commands/insert.sql")
    query = template.read().format(request.form["firstname"], request.form["lastname"], request.form["gender"],
                                   request.form["age"], request.form["height"], request.form["weight"])
    template.close()
    try:
        res = db.engine.execute(query)
    except:
        return "Failed", 400
    return "Success"

@app.route('/READ', methods=['GET'])
def databaseDump():
    res = db.engine.execute("SELECT * FROM celebrities;")
    resultset = []
    for row in res:
        resultset.append(dict(row))
    return str(resultset)

@app.route('/display')
def showAll():
    return viewPage("")


def buildTableBody(l):
    output = ""
    for each_row in l:
        output += "<tr onclick='setEdit(" + str(each_row["id"]) + ")'>"
        output += "<td>" + each_row["firstname"] + "</td>"
        output += "<td>" + each_row["lastname"] + "</td>"
        output += "<td>" + str(each_row["height"]) + "</td>"
        output += "<td>" + str(each_row["weight"]) + "</td>"
        output += "<td>" + each_row["gender"] + "</td>"
        output += "<td>" + str(each_row["age"]) + "</td>"
        output += "<td>" + str(each_row["id"]) + "</td>"
        output += "</tr>\n"
    return output




@app.route('/display/<search>')
def viewPage(search):
    template = open("SQL_commands/search.sql")
    query = template.read().format(search, search, search)
    try:
        res = db.engine.execute(query)
    except:
        return "Failed"
    resultset = []
    for row in res:
        resultset.append(dict(row))

    file_in = open('HTML_Pages/add_and_list.html')
    html_template = file_in.read()
    file_in.close()

    table_f = buildTableBody(resultset)
    return html_template.format(table_f)

@app.route('/display/<gender>/<age_gte>/<age_lte>/<height_gte>/<height_lte>/<weight_gte>/<weight_lte>')
def viewPage_detailed(gender,age_gte,age_lte,height_gte,height_lte,weight_gte,weight_lte):
    template = open("SQL_commands/query.sql")
    query = template.read().format(gender,age_gte,age_lte,height_gte,height_lte,weight_gte,weight_lte)
    try:
        res = db.engine.execute(query)
    except:
        return "Failed"
    resultset = []
    for row in res:
        resultset.append(dict(row))

    file_in = open('HTML_Pages/add_and_list.html')
    html_template = file_in.read()
    file_in.close()

    table_f = buildTableBody(resultset)
    return html_template.format(table_f)




@app.route('/edit/<id>')
def editPage(id):
    template = open("SQL_commands/load_from_id.sql")
    query = template.read().format(id)
    try:
        res = db.engine.execute(query)
    except:
        return "Failed"
    resultset = []
    for row in res:
        resultset.append(dict(row))
    curr_celeb = resultset[0]

    file_in = open('HTML_Pages/modify_user.html')
    html_template = file_in.read()
    file_in.close()

    if curr_celeb["gender"] == 'Male':
        a = ["selected='selected'", "",""]
    elif curr_celeb["gender"] == 'Female':
        a = ["", "selected='selected'", ""]
    else:
        a = ["", "", "selected='selected'"]

    full_name = curr_celeb["firstname"] + " " + curr_celeb["lastname"]
    return html_template.format(full_name, full_name, curr_celeb["firstname"], curr_celeb["lastname"], a[0], a[1], a[2],curr_celeb["age"], curr_celeb["height"], curr_celeb["weight"], curr_celeb["id"])

@app.route('/')
def login():
    file_in = open('HTML_Pages/login.html')
    html_template = file_in.read()
    file_in.close()
    return html_template
@app.route('/register')
def register():
    file_in = open('HTML_Pages/register.html')
    html_template = file_in.read()
    file_in.close()
    return html_template 

@app.route('/search', methods=['GET'])
def searchcelebrity():
    file_in = open('HTML_Pages/enter_celebrity_group.html')
    html_template = file_in.read()
    file_in.close()    
    return html_template
@app.route('/profile', methods=['GET'])
def myprofile():
    file_in = open('HTML_Pages/myprofile.html')
    html_template = file_in.read()
    file_in.close()    
    return html_template
@app.route('/community', methods=['GET'])
def community():
    file_in = open('HTML_Pages/community.html')
    html_template = file_in.read()
    file_in.close()    
    return html_template
if __name__ == '__main__':
    app.run(debug=True)