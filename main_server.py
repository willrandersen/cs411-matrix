from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from random import randint
import hashlib
app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://hccxcbaxkgmbjg:3fd3e1d41f6d20981c7ae46c61d256393dfdf67720c3f825066b2760e89856be@ec2-52-86-73-86.compute-1.amazonaws.com:5432/d7jcothqvc546b"
app.config["MONGO_URI"] = "mongodb://heroku_bm1s8r3b:ggka37atqhdqaqlv3j7658434p@ds249428.mlab.com:49428/heroku_bm1s8r3b"
db = SQLAlchemy(app)
mongo = PyMongo(app, retryWrites=False)


@app.route('/dash', methods=['GET'])
def load_main(called=False):
    print(called)
    user_id = user_id_or_False(request.cookies.get('login_cookie'))
    if user_id == False and not called:
        print("redirecting")
        return redir_to_login()
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

def getRandomLetters(length=60):
    output_string = ''
    sample = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    for index in range(0, length):
        index = randint(0, len(sample) - 1)
        output_string += sample[index]
    return output_string

def redir_to_login():
    html_page = open("HTML_Pages/redir_main.html")
    return html_page.read()

def user_id_or_False(cookie):
    cookie_match = mongo.db.Sessions.find({'cookie' : cookie})
    for each_match in cookie_match:
        print("Found user")
        return each_match['loginID']
    print("Not Found user")
    return False

@app.route('/dash', methods=['POST'])
def log_user_then_load():
    hash_object = hashlib.sha256(str(request.form['password']).encode('utf-8'))
    given_login_id = request.form['loginID']
    id_match = mongo.db.Users.find_one({'loginID': given_login_id})
    if id_match is None or id_match['Pass_hash'] != hash_object.hexdigest():
        print("login failed")
        return login()
    print("valid user & password")
    random_cookie = getRandomLetters(150)
    mongo.db.Sessions.delete_many({'loginID' : request.form['loginID']})
    mongo.db.Sessions.insert({'loginID' : request.form['loginID'], 'cookie' : random_cookie})

    resp = make_response(load_main(True))
    resp.set_cookie('login_cookie', random_cookie)
    return resp

@app.route('/clear', methods=['GET'])
def clear_mongo():
    mongo.db.Users.delete_many({})
    mongo.db.Invitations.delete_many({})
    mongo.db.Sessions.delete_many({})
    return 'done'

@app.route('/dash', methods=['PUT'])
def add_user_then_load():
    hash_object = hashlib.sha256(str(request.form['password']).encode('utf-8'))
    if mongo.db.Users.find_one({'loginID' : request.form['loginID']}) != None:
        return register()
    mongo.db.Users.insert({'first_name' : request.form['first_name'], 'last_name' : request.form['last_name'],
                           'loginID' : request.form['loginID'],
                           'AccountName' : request.form['AccountName'],
                           'Age' : request.form['Age'],
                           'Email' : request.form['Email'],
                           'Pass_hash' : hash_object.hexdigest(),
                           'Friends' : [], 'Subscribed' : []})
    random_cookie = getRandomLetters(150)
    mongo.db.Sessions.insert({'loginID' : request.form['loginID'], 'cookie' : random_cookie})

    resp = make_response(load_main(True))
    resp.set_cookie('login_cookie', random_cookie)
    return resp


@app.route('/update', methods=['DELETE'])
def deleteFromDatabase():
    user_id = user_id_or_False(request.cookies.get('login_cookie'))
    if user_id == False:
        return redir_to_login()
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
    user_id = user_id_or_False(request.cookies.get('login_cookie'))
    if user_id == False:
        return redir_to_login()
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
    user_id = user_id_or_False(request.cookies.get('login_cookie'))
    if user_id == False:
        return redir_to_login()
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
    user_id = user_id_or_False(request.cookies.get('login_cookie'))
    if user_id == False:
        return redir_to_login()
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

@app.route('/display/<gender>/<age_gte>/<age_lte>/<height_gte>/<height_lte>/<weight_gte>/<weight_lte>/<af>')
def viewPage_detailed(gender,age_gte,age_lte,height_gte,height_lte,weight_gte,weight_lte, af):
    user_id = user_id_or_False(request.cookies.get('login_cookie'))
    if user_id == False:
        return redir_to_login()
    if(af == "Default"):
        template = open("SQL_commands/query.sql")
        query = template.read().format(gender,age_gte,age_lte,height_gte,height_lte,weight_gte,weight_lte)
    else:
        template = open("SQL_commands/query_join.sql")
        query = template.read().format(gender,age_gte,age_lte,height_gte,height_lte,weight_gte,weight_lte, af)
        print(query)
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
    user_id = user_id_or_False(request.cookies.get('login_cookie'))
    if user_id == False:
        return redir_to_login()
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
    comm_message = "Join Community"
    if id in mongo.db.Users.find_one({"loginID" : user_id})['Subscribed']:
        comm_message = "Leave Community"
    return html_template.format(full_name, full_name, curr_celeb["firstname"], curr_celeb["lastname"], a[0], a[1], a[2],curr_celeb["age"], curr_celeb["height"], curr_celeb["weight"], curr_celeb["id"], comm_message)


def render_friends(user):
    friend_list = user['Friends']
    friend_data = mongo.db.Users.find({"loginID" : {"$in" : friend_list}})

    output = ""
    for each_friend in friend_data:
        output += "<tr>"
        output += "<td>" + each_friend['AccountName'] + "</td>"
        output += "<td>" + each_friend['first_name'] + "</td>"
        output += "<td>" + each_friend['last_name'] + "</td>"
        output += "<td>" + each_friend['Age'] + "</td>"
        output += "<td>" + each_friend['loginID'] + "</td>"
        output += "<td>" + "<button onclick='delete_friend(\"" + each_friend['loginID'] + "\")' class='btn-danger'>Remove</button>" + "</td>"
        output += "</tr>\n"
    return output

def format_comm_req(follow_list):
    template = open('SQL_commands/load_multiple_ids').read()
    string_in = ""
    for each_entry in follow_list:
        string_in += "id = " + each_entry + " OR "
    return db.engine.execute(template.format(string_in)[:-4])

def common_str(common_list, info_dict):
    out = ""
    for each_common in common_list:
        out += info_dict[int(each_common)][0] + ' ' + info_dict[int(each_common)][1] + ', '
    if len(out) > 0:
        return out[:-2]
    return out

def render_community(user):
    follow_list = user['Subscribed']
    if len(follow_list) == 0:
        return ""
    aggregate_list = [{
       "$match" : {
           "loginID": {"$ne": user['loginID']}
       }
    }, {
        "$unwind" : "$Subscribed"
    }, {
        "$match": {
            "Subscribed" : {"$in" : follow_list}
        }
    }, {
        "$group" : {
            "_id" : {
                "loginID" : "$loginID",
                "AccountName": "$AccountName",
                "Email": "$Email",
                "Age": "$Age",
            },
            "common_subscribed" : { "$push" :
                "$Subscribed"
            },
            "common_count" : {"$sum" : 1}
        }
    }, {
        "$sort" : {"common_count" : -1}
    }]
    follow_data = mongo.db.Users.aggregate(aggregate_list)
    id_data = {}
    res = format_comm_req(follow_list)
    for each_line in res:
        id_data[each_line[2]] = each_line
    print(id_data)
    output = ""
    for each_comm in follow_data:
        output += "<tr>"
        output += "<td>" + each_comm["_id"]['AccountName'] + "</td>"
        output += "<td>" + each_comm["_id"]['Email'] + "</td>"
        output += "<td>" + each_comm["_id"]['Age'] + "</td>"
        output += "<td>" + common_str(each_comm["common_subscribed"], id_data) + "</td>"
        output += "<td>" + "<button onclick='invitation_send(\"" + each_comm["_id"]['loginID'] + "\")' class='btn btn-primary'>Invite</button>" + "</td>"
        output += "</tr>\n"
    return output


def render_requests(user):
    req_list = mongo.db.Invitations.find({'sent_to' : user['loginID']})
    output = ""
    for each_req in req_list:
        output += "<tr>"
        output += "<td>" + each_req['sent_from'] + "</td>"
        output += "<td><button type='button' onclick='invitation_response(\"" + each_req['sent_from'] + "\" ,true)' class='btn btn-success'>Accept</button></td>"
        output += "<td><button type='button' onclick='invitation_response(\"" + each_req['sent_from'] + "\" ,false)' class='btn btn-danger'>Decline</button></td>"
        output += "</tr>\n"
    return output

@app.route('/')
def login():
    file_in = open('HTML_Pages/login.html')
    html_template = file_in.read()
    file_in.close()
    return html_template

@app.route('/friendship', methods=['PUT'])
def send_request():
    user_id = user_id_or_False(request.cookies.get('login_cookie'))
    if user_id == False:
        return redir_to_login()
    possible_friend = request.form['new_friend']
    id_match = mongo.db.Users.find_one({'loginID': possible_friend})
    if id_match is None:
        return "False", 400
    if user_id in id_match["Friends"]:
        return "False", 304
    mongo.db.Invitations.insert({"sent_from" : user_id, "sent_to" : possible_friend})
    return "True", 200

@app.route('/friendship', methods=['POST'])
def add_friend():
    user_id = user_id_or_False(request.cookies.get('login_cookie'))
    if user_id == False:
        return redir_to_login()
    possible_friend = request.form['new_friend']
    should_add = request.form['add']
    mongo.db.Invitations.delete_many({"sent_to" : user_id, "sent_from" : possible_friend})
    if should_add == "false":
        return ""
    mongo.db.Users.update_one({"loginID" : user_id}, {'$push': {'Friends': possible_friend}})
    mongo.db.Users.update_one({"loginID" : possible_friend}, {'$push': {'Friends': user_id}})
    return ""


@app.route('/deletefriend', methods=['DELETE'])
def delete_friendship():
    user_id = user_id_or_False(request.cookies.get('login_cookie'))
    if user_id == False:
        return redir_to_login()
    remove_friend = request.form['new_friend']
    mongo.db.Users.update_one({"loginID": user_id}, {'$pull': {'Friends': remove_friend}})
    mongo.db.Users.update_one({"loginID": remove_friend}, {'$pull': {'Friends': user_id}})
    return "Done"

@app.route('/register')
def register():
    file_in = open('HTML_Pages/register.html')
    html_template = file_in.read()
    file_in.close()
    return html_template 


@app.route('/search', methods=['GET'])
def searchcelebrity():
    user_id = user_id_or_False(request.cookies.get('login_cookie'))
    if user_id == False:
        return redir_to_login()
    file_in = open('HTML_Pages/enter_celebrity_group.html')
    html_template = file_in.read()
    file_in.close()    
    return html_template


@app.route('/profile', methods=['GET'])
def myprofile():
    user_id = user_id_or_False(request.cookies.get('login_cookie'))
    if user_id == False:
        return redir_to_login()
    file_in = open('HTML_Pages/myprofile.html')
    user_data = mongo.db.Users.find_one({"loginID" : user_id})
    html_template = file_in.read().format(user_data['first_name'], user_data['first_name'], user_data['last_name'], user_data['AccountName'], 'communities', render_friends(user_data), render_requests(user_data))
    file_in.close()    
    return html_template


@app.route('/community', methods=['GET'])
def community():
    user_id = user_id_or_False(request.cookies.get('login_cookie'))
    if user_id == False:
        return redir_to_login()
    file_in = open('HTML_Pages/community.html')
    user_data = mongo.db.Users.find_one({"loginID": user_id})
    html_template = file_in.read().format(user_data['first_name'] + '\'s', render_community(user_data))
    file_in.close()    
    return html_template

@app.route('/logout', methods=['POST'])
def logout():
    user_id = user_id_or_False(request.cookies.get('login_cookie'))
    if user_id == False:
        return redir_to_login()
    mongo.db.Sessions.delete_many({'loginID' : user_id})
    resp = make_response(redir_to_login())
    resp.set_cookie('login_cookie', "")
    return resp


@app.route('/community', methods=['POST'])
def joincommunity():
    user_id = user_id_or_False(request.cookies.get('login_cookie'))
    if user_id == False:
        return redir_to_login()
    user_data = mongo.db.Users.find_one({"loginID": user_id})
    if not request.form['id'] in user_data['Subscribed']:
        if len(user_data['Subscribed']) < 5:
            template = open("SQL_commands/joincommunity.sql")
            query = template.read().format(request.form['id'])
            template.close()
            try:
                res = db.engine.execute(query)
                mongo.db.Users.update_one({"loginID": user_id}, {'$push': {'Subscribed': request.form['id']}})
            except:
                return "Failed", 400
    else:
        template = open("SQL_commands/update_community_fansnum.sql")
        query = template.read().format(request.form['id'])
        template.close()
        try:
            res = db.engine.execute(query)
            mongo.db.Users.update_one({"loginID": user_id}, {'$pull': {'Subscribed': request.form['id']}})
        except:
            return "Failed", 400
    return "Success"

if __name__ == '__main__':
    app.run(debug=True)