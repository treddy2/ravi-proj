# Resume Phrase Matcher code


# importing all required libraries
import atexit
import base64
import glob
import io
import tempfile
import webbrowser
from operator import itemgetter

import docxpy
import fitz
from apscheduler.schedulers.background import BackgroundScheduler

# from flask_apscheduler import APScheduler
# scheduler = APScheduler()
from werkzeug.utils import secure_filename

import gcpresources
from gcpresources import upload_files_gcp

sched = BackgroundScheduler()

import content
import PyPDF2
import os
from io import StringIO

# import buffer as buffer
# import docx as docx
import pandas as pd
from collections import Counter
import en_core_web_sm
import matplotlib.pyplot as plt

from dbscripts import login_sc, configskills_db, gettechnologies, _processdata, getskillareas, _techsubAreas, \
    logout, userdetails_res, filename_generator, configmncs_db, _techcomp, up_del_modal, getmncscomp, del_model

nlp = en_core_web_sm.load()
from spacy.matcher import PhraseMatcher
from flask import Flask, render_template, request, session, jsonify

app = Flask(__name__)

app.secret_key = 'random string'
TOPIC_DICT = content

# Function to read resumes from the folder one by one
# mypath = '/home/rdy/resumes'  # enter your path here where you saved the resumes
# onlyfiles = [os.path.join(mypath, f) for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
login_user_name = ""
login_user_role = ""
is_user_login = False
onlyfiles = ""
# filePath = "/home/rdy/" # Linux directory
filePath = "C:/Resumes/"  # Windows directory , mozilla,chrome,edze
# filePath = "C:/Users/ravi/Desktop/"
iefilePath = "C:/Resume/Field Service/"  # Windows internet explorer directory
APP_ROOT = filePath
rsrc_name = "Resource Name"
rsrc_rank = "Rank"
tech_weightage = "Technologies Weightage"
tier_weightage = "Tier Type Weightage"
total_weightage = "Total Weightage"
temp_dict_list1 = []
temp_dict_list = []
temp_words_list = []
mnc_words_list = []
dff_key = dict()
dff_key1 = dict()
tech_skill_org = []
tech_skill_org1 = ""
datali = []
filesCount = 0
chart_session = ""
profile_pic = os.path.join("static", "img")
# upld_files = os.path.join("static","uploadfiles")
app.config["UPLOAD_FOLDER"] = profile_pic
app.config["SECRET_KEY"] = app.secret_key
ls = []
list3 = []
staging_bucket = 'psapp_profiles2'
profiles_bucket = 'psapp_screen_profiles'
filesselected = []
# screened_profiles_r = "https://console.cloud.google.com/storage/browser/"+profiles_bucket+"/"
screened_profiles_r = "https://storage.cloud.google.com/" + profiles_bucket + "/"


def userdetails():
    usr_data = []
    firstName, lastName, eMail, phoneNumber, adDress, couNtry = userdetails_res()
    usr_data.append(firstName)
    usr_data.append(lastName)
    usr_data.append(eMail)
    usr_data.append(phoneNumber)
    usr_data.append(adDress)
    usr_data.append(couNtry)
    return usr_data


@app.route('/')
def home():
    areas_subareas = gettechnologies()
    if login_user_role == "":
        return render_template("login.html", conf="nav-link disabled")
    if login_user_role == "user":
        user_data = userdetails()
        return render_template("pf_result.html", areas_subareas=areas_subareas, filesCount=filesCount,
                               sign_user=login_user_name, conf="nav-link disabled", conf_link="nav-link",
                               login=is_user_login, dropdown_toggle="dropdown-toggle", user_data=user_data)
    if login_user_role == "admin":
        user_data = userdetails()
        return render_template("pf_result.html", areas_subareas=areas_subareas, filesCount=filesCount,
                               sign_user=login_user_name, conf="nav-link", login=is_user_login,
                               dropdown_toggle="dropdown-toggle", user_data=user_data)


@app.route('/login')
def login():
    return render_template("login.html", conf="nav-link disabled")


@app.route("/loginuser", methods=['POST', 'GET'])
def loginuser():
    global login_user_name
    global login_user_role
    global is_user_login
    return_val, session = login_sc()
    if len(session) != 0:
        login_user_name = session['user_name']
        login_user_role = session['user_role']
        is_user_login = session['login']
        if return_val == 1 and login_user_role == "user":
            user_data = userdetails()
            areas_subareas = gettechnologies()
            strg_files = gcpresources.get_storage_files(staging_bucket)
            gcpstrg_files_text = docextract(strg_files[1])
            print("Extracted files",gcpstrg_files_text)
            return render_template("pf_result.html", areas_subareas=areas_subareas, filesCount=filesCount,
                                   sign_user=login_user_name, conf="nav-link disabled", conf_link="nav-link",
                                   login=is_user_login, dropdown_toggle="dropdown-toggle", user_data=user_data,strg_files=strg_files)
        if return_val == 1 and login_user_role == "admin":
            user_data = userdetails()
            areas_subareas = gettechnologies()
            #strg_files = gcpresources.get_storage_files(staging_bucket)
            #gcpstrg_files_text = docextract(strg_files[1])
            #print("Extracted files", strg_files)
            return render_template("pf_result.html", areas_subareas=areas_subareas, filesCount=filesCount,
                                   sign_user=login_user_name, conf="nav-link", login=is_user_login,
                                   dropdown_toggle="dropdown-toggle", user_data=user_data)
            #return render_template("test5.html")
    if len(session) == 0:
        error = 'Incorrect user-name and password'
        return render_template("login.html", error=error, conf="nav-link disabled")


@app.route('/signup')
def signup():
    return render_template("signup.html", conf="nav-link disabled")


@app.route("/signupuser", methods=['POST', 'GET'])
def signupuser():
    _processdata()
    return render_template("login.html", conf="nav-link disabled")


@app.route("/skillsconfig")
def skillsconfig():
    tech_subareas = _techsubAreas()
    techcomp = _techcomp()
    if session['user_role'] == "user":
        user_data = userdetails()
        return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                               filesCount=filesCount,
                               sign_user=session['user_name'], conf="nav-link disabled", conf_link="nav-link",
                               login=session['login'], dropdown_toggle="dropdown-toggle", user_data=user_data)
    if session['user_role'] == "admin":
        user_data = userdetails()
        return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                               filesCount=filesCount,
                               sign_user=session['user_name'], conf="nav-link", login=session['login'],
                               dropdown_toggle="dropdown-toggle", user_data=user_data)
    else:
        error = 'Data is not available'
        return render_template("login.html", error=error, conf="nav-link disabled")
    # return render_template("skillsconfig.html", tech_subareas=tech_subareas,techcomp=techcomp)


@app.route("/configskills", methods=['POST', 'GET'])
def configskills():
    error = ""
    success = ""
    bool, subareas_ratings = configskills_db()  # function insert data in the mysql database
    techcomp = _techcomp()
    tech_subareas = _techsubAreas()

    if not bool and subareas_ratings == 0:
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Invalid values - Null Values not allowed !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   error=error,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", user_data=user_data)

    elif not bool and subareas_ratings == "Duplicate":
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Found duplicates !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   error=error,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", user_data=user_data)

    elif not bool and subareas_ratings == "zero":
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Null Values not allowed in Tech subareas !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   error=error,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", user_data=user_data)

    elif not bool and subareas_ratings == "rating error":
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Please Check assigned weightage !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   error=error,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", user_data=user_data)

    elif not bool and (subareas_ratings == "()" or subareas_ratings == "pipeline"):
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Syntax Error !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   error=error,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", user_data=user_data)

    elif not bool and subareas_ratings == 1:
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Weightage should not be null or zero !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(),
                                   techcomp=techcomp,
                                   error=error,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", user_data=user_data)

    elif not bool and subareas_ratings == "Repeat":
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = 'Error : Technologies and sub-areas exist'
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   error=error,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", user_data=user_data)

    else:
        if session['user_role'] == "admin":
            user_data = userdetails()
            success = "Success : Technologies and sub-areas added successfully !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas, techcomp=techcomp,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", success=success, user_data=user_data)


@app.route("/up_del_modal", methods=['POST', 'GET'])
def updel_modal():
    success = ""
    check, c = up_del_modal()
    tech_subareas = _techsubAreas()
    techcomp = _techcomp()
    if check == False and c == "syntax":
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Syntax Error !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", error=error, user_data=user_data)

    if check == True and c == "Values":
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Tier weightage is constant !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", error=error, user_data=user_data)

    if check == False and c == "Greater":
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Weightage should be 100 !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", error=error, user_data=user_data)

    if check == False and c == "Duplicate":
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Found duplicates values !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", error=error, user_data=user_data)

    if check == False and c == "zero":
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Invalid values - Null values not allowed for subareas !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", error=error, user_data=user_data)

    if check == True and c == 1 or c == "Tier":
        if session['user_role'] == "admin":
            user_data = userdetails()
            success = "Success : Data modified successfully !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", success=success, user_data=user_data)


@app.route("/configmncs", methods=['POST', 'GET'])
def configmncs():
    tiercount = 0
    error = ""
    success = ""
    bool, comp_ratings = configmncs_db()  # function insert data in the mysql database
    tech_subareas = _techsubAreas()
    techcomp = _techcomp()
    if (comp_ratings == "spell check" or comp_ratings == "syntax") and bool == False:
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Invalid Syntax (E.x (Tier-1(value)) ) !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   error=error,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", user_data=user_data)

    if comp_ratings == "Data added" and bool == True:
        if session['user_role'] == "admin":
            user_data = userdetails()
            success = "Success : Data Added successfully !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas, techcomp=techcomp,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", success=success, user_data=user_data)

    if comp_ratings == "Greater than 25" and bool == False:
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Weightage should not exceed 25 or lesser then 25 !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   error=error,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", user_data=user_data)

    if comp_ratings == "duplicate" and bool == False:
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Duplicate values not allowed !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   error=error,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", user_data=user_data)

    if comp_ratings == "Tier Value" and bool == False:
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Tier Value not Equal to Zero !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   error=error,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", user_data=user_data)

    if bool == False and comp_ratings == 0:
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Invalid Values - Null Values Not Allowed !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   error=error,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", user_data=user_data)

    if bool == False and comp_ratings == 4:
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = "Error : Invalid Type !"
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   error=error,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", user_data=user_data)

    if bool == False and comp_ratings == "Company Exit":
        if session['user_role'] == "admin":
            user_data = userdetails()
            error = 'Error : Company already Exist !'
            return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                                   error=error,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", user_data=user_data)


@app.route("/deletemncs", methods=['POST', 'GET'])
def deletemncs():
    del_model()
    tech_subareas = _techsubAreas()
    techcomp = _techcomp()
    if session['user_role'] == "user":
        user_data = userdetails()
        success = "Success : Data modified successfully !"
        return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                               sign_user=session['user_name'], conf="nav-link disabled", conf_link="nav-link",
                               login=session['login'], dropdown_toggle="dropdown-toggle", success=success,
                               user_data=user_data)

    if session['user_role'] == "admin":
        user_data = userdetails()
        success = "Success : Data modified successfully ! "
        return render_template("skillsconfig.html", tech_subareas=tech_subareas.to_dict(), techcomp=techcomp,
                               sign_user=session['user_name'], conf="nav-link", login=session['login'],
                               dropdown_toggle="dropdown-toggle", success=success, user_data=user_data)


@app.route("/signout")
def signout():
    log_out = logout()
    if log_out:
        return render_template("login.html", conf="nav-link disabled")


@app.route("/clear", methods=['GET', 'POST'])
def clear():
    temp_dict_list.clear()
    # tech_skill_org.clear()
    temp_words_list.clear()
    filesselected.clear()
    areas_subareas1 = gettechnologies()
    user_data = userdetails()
    if session['user_role'] == "user":
        return render_template("pf_result.html", areas_subareas=areas_subareas1,
                               sign_user=session['user_name'], conf="nav-link disabled",
                               conf_link="nav-link", user_data=user_data,
                               login=session['login'], dropdown_toggle="dropdown-toggle"
                               )
    if session['user_role'] == "admin":
        return render_template("pf_result.html", areas_subareas=areas_subareas1, sign_user=session['user_name'],
                               conf="nav-link", user_data=user_data,
                               login=session['login'],
                               dropdown_toggle="dropdown-toggle"
                               )


def crDf(temp_dict, tech_skill, mncs_type_l, tech_skill_org1):
    tech_null_dict = dict()
    subareas_occurence = []
    # for x in tech_skill:
    # temp_words_list.append(str(x).strip(' '))
    rmv_dupl = list(dict.fromkeys(tech_skill_org1))
    df8 = pd.DataFrame([[" " for x in range(len(rmv_dupl))]], columns=rmv_dupl)
    for xkey, y in df8.to_dict().items():
        sbars, sbrtngs = subareassplit(xkey)
        for zvalue in y.values():
            tech_null_dict[sbars] = zvalue

    dataframe5 = pd.DataFrame(temp_dict)
    dataframe6 = pd.DataFrame(dataframe5.iloc[:, 0:3])
    resr_df = pd.DataFrame(dataframe6.iloc[[0], [0]])
    resr_name = resr_df.to_dict()
    for keyword_keys in dataframe6.to_dict()['Keyword'].keys():
        for key in tech_null_dict:
            if key in dataframe6.to_dict()['Keyword'][keyword_keys].strip(' '):
                tech_null_dict[key] = int(dataframe6.to_dict()['Count'][keyword_keys].strip(' '))  # mapping
                subareas_occurence.append(int(dataframe6.to_dict()['Count'][keyword_keys].strip(' ')))
    dff_key["Keywods Count"] = tech_null_dict
    temp_dict2 = dict(resr_name, **dff_key)
    temp_dict2.update(resr_name)
    return temp_dict2, subareas_occurence


#strg_files = gcpresources.get_storage_files(staging_bucket)

@app.route('/getprofiles', methods=['GET', 'POST'])
def getprofiles():
    gcp_bucket_profiles = request.form['stgbucketname']
    strg_files = gcpresources.get_storage_files(gcp_bucket_profiles)
    return jsonify(strg_files=strg_files)

@app.route('/profile', methods=["GET",'POST'])
def profile():
    temp_dict_list.clear()
    # tech_skill_org.clear()
    temp_words_list.clear()
    filesselected.clear()
    t1 = []
    t2 = []
    t3 = []
    # user_data = userdetails()
    list_sub_tier_perctg = []
    total_weitg_avg = 0
    try:
        areas_subareas1 = gettechnologies()
        mncs_type_l1, mncs_comp_l = getmncscomp()
        mncs_type_l2, mncs_rating, dum_wtg = tier_ratings(mncs_type_l1)
        mncs_type_l = mncs_type_l2.split(',')
        if len(areas_subareas1) == 0:
            if session['user_role'] == "user":
                user_data = userdetails()
                return render_template("error.html",
                                       sign_user=session['user_name'], conf="nav-link disabled",
                                       conf_link="nav-link", user_data=user_data,
                                       login=session['login'], dropdown_toggle="dropdown-toggle"
                                       )
            if session['user_role'] == "admin":
                user_data = userdetails()
                return render_template("error.html", sign_user=session['user_name'], conf="nav-link",
                                       login=session['login'], user_data=user_data,
                                       dropdown_toggle="dropdown-toggle"
                                       )

        if len(mncs_type_l) < 3 or len(mncs_comp_l) < 3:
            if session['user_role'] == "user":
                user_data = userdetails()
                return render_template("mncs_error.html",
                                       sign_user=session['user_name'], conf="nav-link disabled",
                                       conf_link="nav-link", user_data=user_data,
                                       login=session['login'], dropdown_toggle="dropdown-toggle"
                                       )
            if session['user_role'] == "admin":
                user_data = userdetails()
                return render_template("mncs_error.html", sign_user=session['user_name'], conf="nav-link",
                                       login=session['login'], user_data=user_data,
                                       dropdown_toggle="dropdown-toggle"
                                       )

        if request.method == 'POST':
            technologies = request.form['technologies']
            tech_weight = request.form['techweight']
            tier_weight = request.form.get("tierweight")
            cloud_profiles = request.form.getlist('cloudfilesSel')
            print(cloud_profiles,len(cloud_profiles),"Got the profiles from the Cloud storage")
            tech_subareas1 = getskillareas(technologies)
            tech_skill_org1 = tech_subareas1.split(",")
            tech_subareas, sub_rating, subar_wtg_ratings = subareas_ratings(tech_subareas1)
            fileobject = list(fileobj for fileobj in request.files.getlist('fileNames'))
            # Temp directory to upload selected profiles into Server
            temp_dir_name = tempfile.TemporaryDirectory(prefix="upload_files_", dir=os.getcwd())
            upld_files = os.path.join(temp_dir_name.name)

            for fle in fileobject:
                _file = os.path.join(upld_files, fle.filename.split("/")[1])
                filesselected.append(_file)
                fle.save(_file)
            filesCount1 = len(filesselected)
            filesCount = str(filesCount1) + " - Files"
            chart_wid = 500
            chart_hth = 250
            chart_font = 30
            if filesCount1 <= 10:
                chart_wid = 1000
                chart_hth = 500
                chart_font = 45
            if filesCount1 >= 11 and filesCount1 <= 21:
                chart_wid = 1400
                chart_hth = 700
                chart_font = 35
            if filesCount1 >= 22:
                chart_wid = 2400
                chart_hth = 1400
                chart_font = 25
            final_database = pd.DataFrame()
            # Start - code to work in Internet explorer
            """if filesselected[0].__contains__("/") == False:
                onlyfiles = list(map(lambda x: iefilePath + x, filesselected))"""
            # End - code to work in Internet explorer
            print("check - 1 : No of Files to be Screen - ", len(filesselected))
            for x in range(len(filesselected)):
                f_file = filesselected[x]
                print("check - 2 : Profile  - ", f_file)
                is_file_avl = os.path.isfile(f_file)
                if not is_file_avl:
                    filesselected.clear()
                    if session['user_role'] == "user":
                        user_data = userdetails()
                        print("check - 3 : File is not avialable")
                        return render_template("error.html",
                                               sign_user=session['user_name'], conf="nav-link disabled",
                                               conf_link="nav-link", user_data=user_data,
                                               login=session['login'], dropdown_toggle="dropdown-toggle"
                                               )
                    if session['user_role'] == "admin":
                        user_data = userdetails()
                        print("check - 3 : File is not avialable")
                        return render_template("error.html", sign_user=session['user_name'], conf="nav-link",
                                               login=session['login'], user_data=user_data,
                                               dropdown_toggle="dropdown-toggle"
                                               )
                dat, tech_skill = create_profile(f_file, technologies, tech_subareas, mncs_type_l[0],
                                                 mncs_comp_l[0], mncs_type_l[1], mncs_comp_l[1],
                                                 mncs_type_l[2], mncs_comp_l[2])

                t1 = get_keyt1(mncs_type_l[0], dat.to_dict())
                t2 = get_keyt2(mncs_type_l[1], dat.to_dict())
                t3 = get_keyt3(mncs_type_l[2], dat.to_dict())
                sum_t1 = sum(t1)
                sum_t2 = sum(t2)
                sum_t3 = sum(t3)
                wtg_t1 = mncs_rating[0] * sum_t1
                wtg_t2 = mncs_rating[1] * sum_t2
                wtg_t3 = mncs_rating[2] * sum_t3
                final_database = final_database.append(dat)
                cs, new_data = plotlyChart(final_database, chart_font)
                dataframe3 = pd.DataFrame(dat.iloc[[0], [0]]).to_dict()
                dataframe4 = pd.DataFrame(dat.iloc[:, 2:4]).to_dict()
                temp_dict = dict(dataframe3, **dataframe4)
                temp_dict.update(dataframe3)
                temp_dict3, subareas_occurence1 = crDf(temp_dict, tech_skill, mncs_type_l, tech_skill_org1)
                dummy_list = []
                dummy_list1 = []
                if len(subar_wtg_ratings) == len(temp_dict3['Keywods Count']):
                    # TODO get the unique values and multiply weightage with occurence
                    for k, v in subar_wtg_ratings.items():
                        for x, y in temp_dict3['Keywods Count'].items():
                            if k == x:
                                if y != " ":
                                    dummy_value = v * y
                                    dummy_list.append(dummy_value)

                dummy_list1.append(wtg_t1)
                dummy_list1.append(wtg_t2)
                dummy_list1.append(wtg_t3)
                tech_final_list = list(map(lambda x: x / 100, dummy_list))
                tier_final_list = list(map(lambda x: x / 25, dummy_list1))
                # number_tech_tier = len(sub_rating) + len(mncs_type_l)
                # cand_rank = sum(final_list) / number_tech_tier
                # revert back if it requires to divide by total number of technolgies nad tire-1,2,3
                # sub_areas_wightage = sum(tech_final_list) / len(subar_wtg_ratings)
                # tier_mncs_wightage = sum(tier_final_list) / len(mncs_type_l)
                sub_areas_wightage = sum(tech_final_list)
                sub_ares_perctg = sub_areas_wightage * int(tech_weight) / 100
                tier_mncs_wightage = sum(tier_final_list)
                tier_mncs_perctg = tier_mncs_wightage * int(tier_weight) / 100
                sub_tier_perctg = sub_ares_perctg + tier_mncs_perctg
                list_sub_tier_perctg.append(round(sub_tier_perctg,2))
                temp_dict3["Subareas Weightage"] = round(sub_areas_wightage, 2)
                temp_dict3["Tier Weightage"] = round(tier_mncs_wightage, 2)
                temp_dict3["Tier-1"] = {sum_t1}
                temp_dict3["Tier-2"] = {sum_t2}
                temp_dict3["Tier-3"] = {sum_t3}
                temp_dict3["Total Weightage"] = round(sub_tier_perctg,2)
                temp_dict_list.append(temp_dict3)

    except Exception as e:
        str(e)

    if session['user_role'] == "user" and len(filesselected) != 0:
        user_data = userdetails()
        list(temp_dict_list)
        # temp_dict_list.sort(key=itemgetter("Subareas Weightage"), reverse=True)
        # temp_dict_list.sort(key=lambda z: z['Subareas Weightage'], reverse=True)
        temp_dict_list.sort(key=lambda z: z['Total Weightage'], reverse=True)
        subares_average = find_subares_average(temp_dict_list)
        tier_average = find_tier_average(temp_dict_list)
        if filesselected:
            total_weitg_avg = sum(list_sub_tier_perctg) / len(list_sub_tier_perctg)
            print("check - 3 : Profiles in queue - ", filesselected)
            screend_profiles = screend_profiles_upload(temp_dict_list, subares_average, tier_average, filesselected)
            print("check - 4 : Screened profile stored in Google cloud storage - ", screend_profiles)
            screend_profiles2 = replace_slash(screend_profiles)
            # Upload sreened files to Google cloud storage
            blob_files = upload_files_gcp(screend_profiles2, profiles_bucket)
            for sp2 in screend_profiles2:
                if sp2.split("/")[-1] in blob_files:
                    print("check - 5 : File opened in the Browser", sp2.split("/")[-1])
                    webbrowser.open(screened_profiles_r + sp2.split("/")[-1])

        for x in tech_skill_org1:
            temp_words_list.append(str(x).strip(' '))
        tech_skill_org = list(dict.fromkeys(temp_words_list))
        try:
            profile_pic1 = os.path.join(app.config["UPLOAD_FOLDER"], str(cs))
        except:
            profile_pic1 = "/static/img/NoRecordFound.PNG"
            return render_template("pf_result.html", areas_subareas=areas_subareas1, filesCount=filesCount,
                                   sign_user=session['user_name'], conf="nav-link disabled", conf_link="nav-link",
                                   login=session['login'], dropdown_toggle="dropdown-toggle", rsrc_name=rsrc_name,
                                   rsrc_rank=rsrc_rank, tech_weightage=tech_weightage, tier_weightage=tier_weightage,
                                   profile_pic1=profile_pic1,
                                   temp_dict_list=temp_dict_list, tech_skill_org=tech_skill_org,
                                   user_data=user_data, chart_hth=chart_hth, chart_wid=chart_wid, filePath=filePath,
                                   tier_companies=mncs_type_l1, subares_average=subares_average,
                                   tier_average=tier_average, screened_profiles_r=screened_profiles_r,
                                   total_weightage=total_weightage,total_weitg_avg=total_weitg_avg)
        finally:
            return render_template("pf_result.html", areas_subareas=areas_subareas1, filesCount=filesCount,
                                   sign_user=session['user_name'], conf="nav-link disabled", conf_link="nav-link",
                                   login=session['login'], dropdown_toggle="dropdown-toggle", rsrc_name=rsrc_name,
                                   rsrc_rank=rsrc_rank, tech_weightage=tech_weightage, tier_weightage=tier_weightage,
                                   temp_dict_list=temp_dict_list, tech_skill_org=tech_skill_org,
                                   profile_pic1=profile_pic1,
                                   user_data=user_data, chart_hth=chart_hth, chart_wid=chart_wid, filePath=filePath,
                                   tier_companies=mncs_type_l1, subares_average=subares_average,
                                   tier_average=tier_average, screened_profiles_r=screened_profiles_r,
                                   total_weightage=total_weightage,total_weitg_avg=total_weitg_avg)
    if session['user_role'] == "admin" and len(filesselected) != 0:
        # areas_subareas = gettechnologies()
        user_data = userdetails()
        list(temp_dict_list)
        #temp_dict_list.sort(key=itemgetter("Subareas Weightage"), reverse=True)
        temp_dict_list.sort(key=lambda z: z['Total Weightage'], reverse=True)
        subares_average = find_subares_average(temp_dict_list)
        tier_average = find_tier_average(temp_dict_list)
        if filesselected:
            total_weitg_avg = sum(list_sub_tier_perctg) / len(list_sub_tier_perctg)
            print("Ravindra---total_weitg_avg", total_weitg_avg)
            print("check - 3 : Profiles in the queue ", filesselected)
            screend_profiles = screend_profiles_upload(temp_dict_list, subares_average, tier_average, filesselected)
            print("check - 4 : Screened profile stored in Google cloud storage ", screend_profiles)
            screend_profiles2 = replace_slash(screend_profiles)
            # Upload screened files to Google cloud storage
            blob_files = upload_files_gcp(screend_profiles2, profiles_bucket)
            print(blob_files, "-- blob files --")
            # Check the condition if the files is available in the GCP
            for sp2 in screend_profiles2:
                if sp2.split("/")[-1] in blob_files:
                    print("check - 5 : File opened in the Browser", sp2.split("/")[-1])
                    webbrowser.open(screened_profiles_r + sp2.split("/")[-1])

        for x in tech_skill_org1:
            temp_words_list.append(str(x).strip(' '))
        tech_skill_org = list(dict.fromkeys(temp_words_list))
        try:
            profile_pic1 = os.path.join(app.config["UPLOAD_FOLDER"], str(cs))
            # profile_pic1 = os.path.join(upld_charts, str(cs))
        except:
            profile_pic1 = "/static/img/NoRecordFound.PNG"
            return render_template("pf_result.html", areas_subareas=areas_subareas1, filesCount=filesCount,
                                   sign_user=session['user_name'], conf="nav-link disabled", conf_link="nav-link",
                                   login=session['login'], dropdown_toggle="dropdown-toggle", rsrc_name=rsrc_name,
                                   profile_pic1=profile_pic1,
                                   rsrc_rank=rsrc_rank, tech_weightage=tech_weightage, tier_weightage=tier_weightage,
                                   temp_dict_list=temp_dict_list, tech_skill_org=tech_skill_org,
                                   user_data=user_data, chart_hth=chart_hth, chart_wid=chart_wid, filePath=filePath,
                                   tier_companies=mncs_type_l1, subares_average=subares_average,
                                   tier_average=tier_average, screened_profiles_r=screened_profiles_r,
                                   total_weightage=total_weightage,total_weitg_avg=total_weitg_avg)
        finally:
            return render_template("pf_result.html", areas_subareas=areas_subareas1, filesCount=filesCount,
                                   sign_user=session['user_name'], conf="nav-link", login=session['login'],
                                   dropdown_toggle="dropdown-toggle", rsrc_name=rsrc_name, rsrc_rank=rsrc_rank,
                                   tech_weightage=tech_weightage, tier_weightage=tier_weightage,
                                   temp_dict_list=temp_dict_list, tech_skill_org=tech_skill_org,
                                   profile_pic1=profile_pic1,
                                   user_data=user_data, chart_hth=chart_hth, chart_wid=chart_wid, filePath=filePath,
                                   tier_companies=mncs_type_l1, subares_average=subares_average,
                                   tier_average=tier_average, screened_profiles_r=screened_profiles_r,
                                   total_weightage=total_weightage,total_weitg_avg=total_weitg_avg)
    else:
        error = 'Data is not available'
        return render_template("login.html", error=error)

    # return render_template("pf_result.html", rsrc_name=rsrc_name, filesCount=filesCount, temp_dict_list=temp_dict_list,
    # tech_skill_org=tech_skill_org, areas_subareas=areas_subareas, profile_pic1=profile_pic1)


@app.route('/storagefiles', methods=["GET",'POST'])
def storagefiles():
    print("storage files calls")
    return render_template("login.html")

def replace_slash(lst1):
    lst2 = []
    for p in lst1:
        if p.__contains__("\\"):
            print("check - 6 : Windows Operating system")
            x = p.replace("\\", "/")
            lst2.append(x)
        if p.__contains__("/"):
            print("check - 6 : Linux Operating system")
            lst2.append(p)
    return lst2


def find_subares_average(ls_dict):
    y = list(x['Subareas Weightage'] for x in ls_dict)
    try:
        z = round(sum(y) / len(y), 2)
    except ZeroDivisionError:
        z = 0
    return z


def find_tier_average(ls_dict):
    y = list(x['Tier Weightage'] for x in ls_dict)
    try:
        z = round(sum(y) / len(y), 2)
    except ZeroDivisionError:
        z = 0
    return z


def screend_profiles_upload(ls_dict, subareas_avg, tier_avg, ls_profiles):
    y = []
    for x in ls_dict:
        if x['Subareas Weightage'] >= subareas_avg and x['Tier Weightage'] >= tier_avg:
            z = [var for var in ls_profiles if var.__contains__(x['Candidate Name'][0])]
            y.append(z[0])
    return y


def find_rank(list2):
    list2.sort()
    for x in range(len(list2)):
        list3.append(x + 1)
    new_lst = list3[::-1]
    return new_lst


def subareas_ratings(tech_subareas):
    subareas = []
    subares_ratings = []
    tech_subareas_list = tech_subareas.split(",")
    for tsl in tech_subareas_list:
        if tsl == "":
            break
        y = tsl.strip(" ").find('(')
        z = tsl.strip(" ").find(')')
        subareas.append(tsl[:y])
        techsubareas_ratings = tsl[y + 1:z]
        subares_ratings.append(int(techsubareas_ratings))
    subareas1 = ','.join([str(elem) for elem in subareas])
    subar_wtg_ratings = dict(zip(subareas, subares_ratings))
    return subareas1, subares_ratings, subar_wtg_ratings


def pdfextract1(file):
    fileReader = PyPDF2.PdfFileReader(open(file, 'rb'))
    countpage = fileReader.getNumPages()
    count = 0
    text = []
    while count < countpage:
        pageObj = fileReader.getPage(count)
        count += 1
        t = pageObj.extractText()
        text.append(t)
    return text


"""def docextract1(file):
    doc = docx.Document(file)
    text = []
    for x in doc.paragraphs:
        text.append(x.text)
    return ('\n'.join(text))"""


def docextract(file):
    text = docxpy.process(file)
    return [text]


def pdfextract(file):
    text = ''
    with fitz.open(file) as doc:
        for page in doc:
            text += page.getText()
    return text


def create_profile(file, technologies, tech_subareas, mncs_type_t1, mncs_comp_t1, mncs_type_t2, mncs_comp_t2,
                   mncs_type_t3, mncs_comp_t3):
    check_pdf_format = file.endswith(".pdf")
    check_docx_format = file.endswith(".docx")
    # check_doc_format = file.endswith(".doc")
    if check_pdf_format:
        text = pdfextract(file)

    if check_docx_format:
        text = docextract(file)

    # TODO Check the file is doc format
    # if check_doc_format:
    # text = pdfextract(file)
    text = str(text)
    text = text.replace("\\n", "")
    text1 = text.lower()
    text = "Tier-1 Tier-2 Tier-3 ." + text1
    # keyword_dict = pd.read_csv('/home/rdy/profilekeys/profiles_temp.txt')
    keyword_dict = pd.DataFrame(tech_subareas.split(","), columns=[technologies])
    tier1_dict = pd.DataFrame(mncs_comp_t1.split(","), columns=[mncs_type_t1])
    tier2_dict = pd.DataFrame(mncs_comp_t2.split(","), columns=[mncs_type_t2])
    tier3_dict = pd.DataFrame(mncs_comp_t3.split(","), columns=[mncs_type_t3])
    technologies_words = [nlp(text) for text in keyword_dict[technologies].dropna(axis=0)]
    mncs_words1 = [nlp(text) for text in tier1_dict[mncs_type_t1].dropna(axis=0)]
    mncs_words2 = [nlp(text) for text in tier2_dict[mncs_type_t2].dropna(axis=0)]
    mncs_words3 = [nlp(text) for text in tier3_dict[mncs_type_t3].dropna(axis=0)]
    matcher = PhraseMatcher(nlp.vocab)
    matcher.add(technologies, None, *technologies_words)
    matcher.add('Tier-1', None, *mncs_words1)
    matcher.add('Tier-2', None, *mncs_words2)
    matcher.add('Tier-3', None, *mncs_words3)
    doc = nlp(text)
    d = []
    matches = matcher(doc)
    for match_id, start, end in matches:
        rule_id = nlp.vocab.strings[match_id]  # get the unicode ID, i.e. 'COLOR'
        span = doc[start: end]  # get the matched slice of the doc
        d.append((rule_id, span.text))
    e = filter_mncs(d)
    keywords = "\n".join(f'{i[0]} {i[1]} ({j})' for i, j in Counter(e).items())
    df = pd.read_csv(StringIO(keywords), names=['Keywords_List'])
    df1 = pd.DataFrame(df.Keywords_List.str.split(' ', 1).tolist(), columns=['Subject', 'Keyword'])
    df2 = pd.DataFrame(df1.Keyword.str.split('(', 1).tolist(), columns=['Keyword', 'Count'])
    df3 = pd.concat([df1['Subject'], df2['Keyword'], df2['Count']], axis=1)
    df3['Count'] = df3['Count'].apply(lambda x: x.rstrip(")"))
    base = os.path.basename(file)
    filename = os.path.splitext(base)[0]
    name = rename_file(filename)
    # name2 = name.lower()  # resource-name
    ## converting str to dataframe
    name3 = pd.read_csv(StringIO(name), names=['Candidate Name'])
    dataf = pd.concat([name3['Candidate Name'], df3['Subject'], df3['Keyword'], df3['Count']], axis=1)
    dataf['Candidate Name'].fillna(dataf['Candidate Name'].iloc[0], inplace=True)
    return (dataf, technologies_words)


def filter_mncs(d):
    ch = []
    ch1 = []
    ch2 = []
    for i in d:
        ch.append(i)
    for i in ch:
        if i[0] == "Tier-1" or i[0] == "Tier-2" or i[0] == "Tier-3":
            ch1.append(i)
        else:
            ch2.append(i)
    d1 = (list(set(ch1)))
    d2 = (list(ch2))
    d = d1 + d2
    return d


def rename_file(filename):
    return filename[:8]


def get_keyt1(val, tier_dict):
    k = ""
    tier1 = []
    for key, vale in tier_dict['Subject'].items():
        if val == vale:
            k = int(key)
            for value in tier_dict['Count'][k]:
                if vale == "Tier-1":
                    tier1.append(int(value))
    return tier1


def get_keyt2(val, tier_dict):
    k = ""
    tier2 = []
    for key, vale in tier_dict['Subject'].items():
        if val == vale:
            k = int(key)
            for value in tier_dict['Count'][k]:
                if vale == "Tier-2":
                    tier2.append(int(value))
    return tier2


def get_keyt3(val, tier_dict):
    k = ""
    tier3 = []
    for key, vale in tier_dict['Subject'].items():
        if val == vale:
            k = int(key)
            for value in tier_dict['Count'][k]:
                if vale == "Tier-3":
                    tier3.append(int(value))
    return tier3


# function end` 1   s
def plotlyChart(final_database, chart_font):
    # code to count words under each category and visulaize it through Matplotlib
    final_database2 = final_database['Keyword'].groupby(
        [final_database['Candidate Name'], final_database['Subject']]).count().unstack()
    final_database2.reset_index(inplace=True)
    final_database2.fillna(0, inplace=True)
    new_data = final_database2.iloc[:, 1:]
    new_data.index = final_database2['Candidate Name']
    # execute the below line if you want to see the candidate profile in a csv format
    new_data.to_csv('static/img/sample3.csv')
    plt.rcParams.update({'font.size': chart_font})
    ax = new_data.plot.barh(title="Resume keywords by category", legend=False, figsize=(50, 25),
                            stacked=True)
    labels = []
    # new_data.rename(columns={new_data.columns[0]: "Technologies"}, inplace=True)
    for j in new_data.columns:
        for i in new_data.index:
            label = str(j) + ": " + str(int(new_data.loc[i][j]))
            labels.append(label)
    patches = ax.patches
    for label, rect in zip(labels, patches):
        width = rect.get_width()
        if width > 0:
            x = rect.get_x()
            y = rect.get_y()
            height = rect.get_height()
            ax.text(x + width / 2., y + height / 2., label, ha='center', va='center')
    # plt.show()
    plt.xticks(rotation='1.5')
    chart_session = filename_generator()
    plt.savefig("static/img/" + chart_session, dpi=40)
    # plt.close()
    # TODO
    return chart_session, new_data


def plotfigre(plt):
    buffer = io.BytesIO()
    plt.savefig(buffer, format='PNG', bbox_inches='tight')
    buffer.seek(0)
    data_uri = base64.b64encode(buffer.read()).decode('ascii')
    return data_uri


def remove_chart():
    for f in glob.glob("static/img/PROFILE_CHART_*"):
        print("Scheduled Job to Remove files - Task Finished")
        os.remove(f)


def tier_ratings(comp_ratings):
    subareas = []
    subares_ratings = []
    # tech_subareas_list =  tech_subareas.split(",")
    for tsl in comp_ratings:
        if tsl == "":
            break
        y = tsl.strip(" ").find('(')
        z = tsl.strip(" ").find(')')
        subareas.append(tsl[:y])
        techsubareas_ratings = tsl[y + 1:z]
        subares_ratings.append(int(techsubareas_ratings))
    subareas1 = ','.join([str(elem) for elem in subareas])
    subar_wtg_ratings = dict(zip(subareas, subares_ratings))

    return subareas1, subares_ratings, subar_wtg_ratings


def ranksplit(tech):
    y = tech.strip(" ").find('{')
    z = tech.strip(" ").find('}')
    subareas = tech[:y]
    techsubareas_ratings = tech[y + 1:z]
    return subareas, techsubareas_ratings


def subareassplit(tech):
    y = tech.strip(" ").find('(')
    z = tech.strip(" ").find(')')
    subareas = tech[:y]
    techsubareas_ratings = tech[y + 1:z]
    return subareas, techsubareas_ratings


if __name__ == "__main__":
    # scheduler.add_job(id = "Scheduler Task",func=remove_chart, trigger="interval", seconds=60)
    # scheduler.start()
    # atexit.register(lambda: scheduler.shutdown())
    sched.add_job(remove_chart, 'cron', day_of_week='0-6', hour=14, minute=25)
    sched.start()
    atexit.register(lambda: sched.shutdown())
    #app.run(debug=True, port="5000", threaded=True)
    # app.run(debug=True,host='0.0.0.0',port="8080",threaded=True)
