import os
import random
import re
import mysql
from flask import request, session

import dbcon
import datetime
import pandas as pd
import base64



def current_date():
    crnt_date = datetime.datetime.now()
    return crnt_date


def _processdata():
    try:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        emailId = request.form['emailId']
        password1 = request.form['password']
        address = request.form['address']
        country = request.form['country']
        mobilenumber = request.form['mobilenumber']
        role = request.form['role']
        crntdate = current_date()
        modifieddate = current_date()
        h_db, h_cursor = dbcon.AppInst.db_conn()
        #h_db, h_cursor = cloudsqldbcon.GcpAppInst.db_conn()
        pass_decode, decode_pass = str_hash(password1)
        # h_cursor.execute("create table HPS.H_USER_TAB(FIRST_NAME varchar(70),LAST_NAME varchar(70),MAIL_ID varchar(210) NOT NULL PRIMARY KEY,H_PASSWORD varchar(70),H_ADDRESS varchar(210),H_COUNTRY varchar(70),MOBILE_NUMBER varchar(70),USER_ROLE varchar(50),CREATED_DATE varchar(70),MODIFIED_DATE varchar(70));")
        sql_statement = "insert into HPS.H_USER_TAB(FIRST_NAME, LAST_NAME, MAIL_ID, H_PASSWORD, H_ADDRESS, H_COUNTRY, MOBILE_NUMBER, USER_ROLE, CREATED_DATE, MODIFIED_DATE) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        h_cursor.execute(sql_statement,
                         [firstname, lastname, emailId, pass_decode, address, country, mobilenumber, role, crntdate,
                          modifieddate])
        h_db.commit()
    except Exception as e:
        str(e)


def str_hash(password1):
    str_byt = password1.encode("utf-8")
    pwd_base64 = base64.b64encode(str_byt)
    pass_decode = pwd_base64.decode("utf-8")
    pwd_decode_by = base64.b64decode(pass_decode)
    decode_pass = pwd_decode_by.decode()
    return pass_decode, decode_pass


def logout():
    session.pop('login', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    session.pop('user_role', None)
    return True


def login_sc():
    session1 = {}
    emailid = request.form['email']
    password1 = request.form['password']
    pass_decode, decode_pass = str_hash(password1)
    try:
        h_db, h_cursor = dbcon.AppInst.db_conn()
        h_cursor.execute("select * from HPS.H_USER_TAB where MAIL_ID=%s and H_PASSWORD=%s;", (emailid, pass_decode,))
        result = h_cursor.fetchone()
        if result:
            session['login'] = True
            session['user_name'] = result[0]
            session['user_email'] = result[2]
            session['user_role'] = result[7]
            return 1, session
        else:
            return 0, session
    except Exception as e:
        str(e)


def configskills_db():
    keyword_text = request.form["skills"]
    if keyword_text == "":
        skill_rate = 0
        return False, skill_rate
    pipe = keyword_text.find('|') + 1
    dup = []
    dup = keyword_text[pipe:]
    mnc1 = list(dup.strip(" ").split(','))
    d = []
    for i in mnc1:
        x = i.find('(')
        d.append(i[:x])
    skills, subareas, subareas_ratings = _skillsSubAreas(keyword_text)
    repeat = subareas_validation1()

    if pipe == 0 or pipe == "" or keyword_text[pipe + 1:] == "" or keyword_text[pipe + 1:] == 0:
        skill_rate = "pipeline"
        return False, skill_rate

    elif (len(set(d))) != (len(d)):
        skill_rate = "Duplicate"
        return False, skill_rate

    elif skills in repeat:
        skill_rate = "Repeat"
        return False, skill_rate

    elif not skills and (subareas == ")" or subareas == "(") and subareas_ratings == 0:
        skill_rate = "()"
        return False, skill_rate

    elif 0 in subareas_ratings or "0" in subareas_ratings:
        skill_rate = "zero"
        return False, skill_rate

    elif not skills and subareas == 00 and subareas_ratings == 0:
        skill_rate = 1
        return False, skill_rate

    elif sum(subareas_ratings) != 100:
        skill_rate = "rating error"
        return False, skill_rate

    elif skills.capitalize() not in gettechnologies() and sum(subareas_ratings) == 100:
        crntdate = current_date()
        modifieddate = current_date()
        h_db, h_cursor = dbcon.AppInst.db_conn()
        # sql_statement = "create table H_TECHNOLOGIES(TECH_NAME varchar(225) NOT NULL PRIMARY KEY,TECH_SUBAREAS text,CREATED_DATE varchar(70),MODIFIED_DATE varchar(70));"
        sql_insert = "insert into HPS.H_TECHNOLOGIES(TECH_NAME,TECH_SUBAREAS,CREATED_DATE,MODIFIED_DATE) values(%s,%s,%s,%s);"
        h_cursor.execute(sql_insert, [skills.capitalize(), subareas.lower(), crntdate, modifieddate])
        h_db.commit()
        return True, subareas_ratings
    else:
        return False, subareas_ratings


def configmncs_db():
    mncs_text = request.form["mncs"]
    x = mncs_text.find('-')
    y = mncs_text.find('(')
    z = mncs_text[x + 1:y]
    y1 = y + 1
    z1 = mncs_text[y1:mncs_text.find(')')]
    mnc_re, tier_check, test = mnc_validation1()
    mnc_res = 25 - sum(mnc_re)
    z2 = mncs_text[mncs_text.find('T'):mncs_text.find('-')]
    z3 = mncs_text[mncs_text.find('T'):mncs_text.find('(')]
    z4 = mncs_text.find('|')

    tiercomp = mnc_duplication()
    d = mncs_text[mncs_text.find('|') + 1:]
    d = d.split(',')
    dup = []

    for i in tiercomp:
        for j in i:
            dup.append(j)

    for i in d:
        if i in dup:
            comp = "duplicate"
            return False, comp
    try:
        if mncs_text == "":
            comp_ratings = 0
            return False, comp_ratings

        if len(set(d)) != len(d):
            comp = "duplicate"
            return False, comp

        if int(z1) == 0:
            comp_ratings = "Tier Value"
            return False, comp_ratings

        if int(z) > 3:
            comp_ratings = 4
            return False, comp_ratings

        if z2 != "Tier":
            comp_ratings = "spell check"
            return False, comp_ratings

        if z4 == -1 or z4 == "-1":
            c = "syntax"
            return False, c

        if z3 in tier_check:
            comp_ratings = "Company Exit"
            return False, comp_ratings

        add = ""
        try:
            if sum(mnc_re) == 0 or len(mnc_re) == 1:
                add = 1
            if int((mnc_res) == int(z1) and sum(mnc_re) <= 25) or (add == 1 and sum(mnc_re) <= 25):
                tier_type, tier_compns, comp_ratings = _tier_type_compns(mncs_text)
                crntdate = current_date()
                modifieddate = current_date()
                h_db, h_cursor = dbcon.AppInst.db_conn()
                # sql_statement = "create table HPS.MNCS_COMPANIES(MNCS_TYPE varchar(225) NOT NULL PRIMARY KEY,MNCS_NAME text,CREATED_DATE varchar(70),MODIFIED_DATE varchar(70));"
                sql_insert = "insert into HPS.MNCS_COMPANIES(MNCS_TYPE,MNCS_NAME,CREATED_DATE,MODIFIED_DATE) values(%s,%s,%s,%s);"
                h_cursor.execute(sql_insert, [tier_type.capitalize(), tier_compns.lower(), crntdate, modifieddate])
                h_db.commit()
                comp_ratings = "Data added"
                return True, comp_ratings
            else:
                comp_ratings = "Greater than 25"
                return False, comp_ratings
        except:
            if int(z1) == 0:
                comp_ratings = "Tier Value"
                return False, comp_ratings

    except:
        comp_ratings = "spell check"
        return False, comp_ratings


# Verify the keyword-text contains special characters,if it contains return's true
def verifyseclChar(keyword_text):
    pattern = "^[A-Za-z0-9 |,.#-]*$"  # allows space , # .
    state = bool(re.match(pattern, keyword_text))
    return state


def filename_generator():
    n = random.randint(0, 99999999)
    ps_file_name = "PROFILE_CHART_"
    file_format = ".png"
    file_name = ps_file_name + str(n) + file_format
    # session['chart_file_name'] = file_name
    return file_name


def _skillsSubAreas(text):
    subares_ratings = []
    x = text.strip(" ").find('|')
    tech_areas = text[:x]
    tech_subareas = text[x + 1:]
    tech_subareas_list = tech_subareas.split(",")
    for tsl in tech_subareas_list:
        if tsl == "":
            break
        y = tsl.find('(')
        z = tsl.find(')')
        if (tsl[y + 1:z]) == 0 or (tsl[y + 1:z]) == "":
            error = 00
            r = 0
            return False, error, r
        if y == -1:
            error = "("
            r = 0
            return False, error, r
        if z == -1:
            error = ")"
            r = 0
            return False, error, r
        techsubareas_ratings = tsl[y + 1:z]
        subares_ratings.append(int(techsubareas_ratings))

    return tech_areas, tech_subareas, subares_ratings


def _tier_type_compns(text):
    x = text.strip(" ").find('|')
    tier_type = text[:x]
    tier_compns = text[x + 1:]
    y = tier_type.strip(" ").find('(')
    z = tier_type.strip(" ").find(')')
    tiercomp_ratings = tier_type[y + 1:z]
    return tier_type, tier_compns, tiercomp_ratings


# function to get technologies at drop down
def gettechnologies():
    tech_name_l = []
    try:
        h_db, h_cursor = dbcon.AppInst.db_conn()
        sql_statement = "select * from HPS.H_TECHNOLOGIES;"
        h_cursor.execute(sql_statement)
        result = h_cursor.fetchall()
        for row in result:
            tech_name = row[0]
            tech_name_l.append(tech_name)
    except Exception as e:
        str(e)
    return tech_name_l;


# function to get technologies at drop down
def getmncs():
    mncs_l = []
    try:
        h_db, h_cursor = dbcon.AppInst.db_conn()
        sql_statement = "select * from HPS.MNCS_COMPANIES;"
        h_cursor.execute(sql_statement)
        result = h_cursor.fetchall()
        for row in result:
            tier_comp = row[0]
            mncs_l.append(tier_comp)
    except Exception as e:
        str(e)
    return mncs_l;


# function to get technologies at drop down
def getmncscomp():
    mncs_type_l = []
    mncs_l = []
    try:
        h_db, h_cursor = dbcon.AppInst.db_conn()
        sql_statement = "select * from HPS.MNCS_COMPANIES;"
        h_cursor.execute(sql_statement)
        result = h_cursor.fetchall()
        for row in result:
            tier_type = row[0]
            tier_comp = row[1]
            mncs_type_l.append(tier_type)
            mncs_l.append(tier_comp)
    except Exception as e:
        str(e)
    return mncs_type_l, mncs_l;


def mncs_c():
    mncs_name_l = []
    try:
        h_db, h_cursor = dbcon.AppInst.db_conn()
        sql_statement = "select * from HPS.MNCS_TAB;"
        h_cursor.execute(sql_statement)
        result = h_cursor.fetchall()
        for row in result:
            mncs_name = row[0]
            mncs_name_l.append(mncs_name)
    except Exception as e:
        str(e)
    return mncs_name_l;


def userdetails_res():
    try:
        h_db, h_cursor = dbcon.AppInst.db_conn()
        sql_statement = "select * from HPS.H_USER_TAB where MAIL_ID=%s;"
        user_email = (session['user_email'],)
        h_cursor.execute(sql_statement, user_email)
        result = h_cursor.fetchone()
    except Exception as e:
        str(e)
    return result[0], result[1], result[2], result[6], result[4], result[5]


# function to get sub-areas of technologies
def getskillareas(technologies):
    try:
        h_db, h_cursor = dbcon.AppInst.db_conn()
        sql_statement = "select TECH_SUBAREAS from HPS.H_TECHNOLOGIES where TECH_NAME=%s;"
        technologies = (technologies,)
        h_cursor.execute(sql_statement, technologies)
        result = h_cursor.fetchone()
    except Exception as e:
        str(e)
    return result[0]


# function to get comp_names of comp_type
def getcompnames(comptype):
    try:
        h_db, h_cursor = dbcon.AppInst.db_conn()
        sql_statement = "select MNCS_NAME from HPS.MNCS_COMPANIES where MNCS_TYPE =%s;"
        comptype = (comptype,)
        h_cursor.execute(sql_statement, comptype)
        result = h_cursor.fetchone()
    except Exception as e:
        str(e)
    return result[0]


# function to fetch sub-areas available in database
def _techsubAreas():
    tech_dict1 = dict()
    tech_dict = dict()
    try:
        h_db, h_cursor = dbcon.AppInst.db_conn()
        sql_statement = "select * from HPS.H_TECHNOLOGIES;"
        h_cursor.execute(sql_statement)
        result = h_cursor.fetchall()
        for row in result:
            tech_name1 = row[0]
            tech_subareas1 = row[1]
            tech_dict1[tech_name1] = [tech_subareas1]

        for tech_name, tech_subareas in tech_dict1.items():
            splt_subareas = ' '.join(map(str, tech_subareas)).split(",")
            tech_dict[tech_name] = splt_subareas
        df = pd.DataFrame(dict([(keys, pd.Series(value)) for keys, value in tech_dict.items()])).fillna(" ")
    except Exception as e:
        str(e)
    return df;


# function to fetch sub-areas available in database
def _techcomp():
    tech_dict1 = dict()
    tech_dict = dict()
    try:
        h_db, h_cursor = dbcon.AppInst.db_conn()
        sql_statement = "select * from HPS.MNCS_COMPANIES;"
        h_cursor.execute(sql_statement)
        result = h_cursor.fetchall()
        for row in result:
            tech_name1 = row[0]
            tech_subareas1 = row[1]
            tech_dict1[tech_name1] = [tech_subareas1]

        for tech_name, tech_subareas in tech_dict1.items():
            splt_subareas = ' '.join(map(str, tech_subareas)).split(",")
            tech_dict[tech_name] = splt_subareas
        df = pd.DataFrame(dict([(keys, pd.Series(value)) for keys, value in tech_dict.items()])).fillna(" ")
    except Exception as e:
        str(e)
    return df.to_dict();


# function to update the sub-areas of technologies
# function to delete the technologies.
def up_del_modal():
    up_text = request.form["skillsId"]
    res = mnc_validation1()[2]
    if up_text.find("Tier-1") == 0 or up_text.find("Tier-2") == 0 or up_text.find("Tier-3") == 0:
        up = update_duplication(up_text)
        if up != "add":
            c = "Duplicate"
            return False, c
        comp_type, comp_names = _skillssplit(up_text)
        if len(set(comp_names)) != len(comp_names):
            c = "Duplicate"
            return False, c

        c = update_compnames(comp_type, comp_names)
        if c not in res or c == "":
            c = "Values"
            return True, c
        else:
            c = "Tier"
            return True, c
    else:
        areas, subareas = _skillssplit(up_text)  # modified-areas,modified-subareas
        mnc1 = []
        d = []
        for i in subareas:
            d.append(i[:i.find('(')])
            c = i.find('(')
            if c == -1:
                c = "zero"
                return False, c

        pipe = up_text.find('|')
        if pipe == -1:
            c = "syntax"
            return False, c

        if len(set(d)) != len(d):
            c = "Duplicate"
            return False, c

        for i in subareas:
            mnc1.append(i[i.find('(') + 1:i.find(')')])

        a = [int(i) for i in mnc1]
        for i in a:
            if i == 0 or i == "0":
                c = "zero"
                return False, c

        if sum(a) != 100:
            c = "Greater"
            return False, c

        c = update_subares(areas, subareas)
        return True, c


# ------------------------------------------------------------------------------------------------------------------
def del_model():
    del_text = request.form["skillsId"]
    if del_text.find("Tier-1") == 0 or del_text.find("Tier-2") == 0 or del_text.find("Tier-3") == 0:
        comp_type, comp_names = _skillssplit(del_text)
        delete_comptype(comp_type)
    else:
        areas, subareas = _skillssplit(del_text)
        delete_areas(areas)


# -------------------------------------------------------------------------------------------------------------------
# Function to clean up  2,3 white spaces,null,empty string, left and right white spaces while fetching data from modal
def _skillssplit(text):
    x = text.strip(" ").find('|')
    tech_areas = text[:x]
    tech_subareas1 = text[x + 1:]
    tech_subareas = tech_subareas1.strip(' ').split(',')
    while ("   " in tech_subareas):
        tech_subareas.remove("   ")
    while ("" in tech_subareas):
        tech_subareas.remove("")
    techsubares = list(x.strip('  ') for x in tech_subareas)
    return tech_areas, techsubares


# function to update sub-areas at modal level
def update_subares(areas, subareas):
    try:
        c = 1
        listConvtoStr = ','.join(map(str, subareas))
        TECH_NAME = areas
        TECH_SUBAREAS = listConvtoStr.lower()
        MODIFIED_DATE = current_date()
        h_db, h_cursor = dbcon.AppInst.db_conn()
        h_cursor.execute(
            """UPDATE HPS.H_TECHNOLOGIES SET  TECH_SUBAREAS = %s,MODIFIED_DATE = %s WHERE TECH_NAME = %s;""",
            (TECH_SUBAREAS, MODIFIED_DATE, TECH_NAME))
        h_db.commit()
        return c
    except Exception as e:
        str(e)


# function to delete technologies at modal level
def delete_areas(areas):
    try:
        h_db, h_cursor = dbcon.AppInst.db_conn()
        sql_query = """DELETE FROM HPS.H_TECHNOLOGIES WHERE TECH_NAME = %s;"""
        h_cursor.execute(sql_query, (areas,))
        h_db.commit()
    except mysql.connector.Error as error:
        print("Failed to Delete record from table: {}".format(error))


# function to delete technologies at modal level
def delete_comptype(comptype):
    try:
        h_db, h_cursor = dbcon.AppInst.db_conn()
        sql_query = """DELETE FROM HPS.MNCS_COMPANIES WHERE MNCS_TYPE  = %s;"""
        h_cursor.execute(sql_query, (comptype,))
        h_db.commit()
    except mysql.connector.Error as error:
        print("Failed to Delete record from table: {}".format(error))


# function to update compnames on the base of comp type at modal level
def update_compnames(comptype, compnames):
    try:
        listConvtoStr = ','.join(map(str, compnames))
        COMP_TYPE = comptype
        COMP_NAMES = listConvtoStr.lower()
        MODIFIED_DATE = current_date()
        h_db, h_cursor = dbcon.AppInst.db_conn()
        h_cursor.execute("""UPDATE HPS.MNCS_COMPANIES SET  MNCS_NAME = %s,MODIFIED_DATE = %s WHERE MNCS_TYPE = %s;""",
                         (COMP_NAMES, MODIFIED_DATE, COMP_TYPE))
        h_db.commit()
        return str(comptype[comptype.find('T'):comptype.find(')') + 1])
    except Exception as e:
        str(e)


def mnc_validation1():
    mncs_l = []
    tiercomp = []
    tier_check = []
    h_db, h_cursor = dbcon.AppInst.db_conn()
    sql_statement = "select MNCS_TYPE from HPS.MNCS_COMPANIES;"
    h_cursor.execute(sql_statement)
    result = h_cursor.fetchall()
    for row in result:
        tier_comp = row[0]
        tiercomp.append(tier_comp)
        x = tier_comp.find("(")
        y = tier_comp.find(")")
        z = tier_comp[x + 1:y]
        mncs_l.append(z)
        z1 = tier_comp[tier_comp.find('T'):tier_comp.find('(')]
        tier_check.append(z1)
    res = [int(x) for x in mncs_l]
    return res, tier_check, tiercomp


def subareas_validation1():
    tiercomp = []
    h_db, h_cursor = dbcon.AppInst.db_conn()
    sql_statement = "select TECH_NAME FROM HPS.H_TECHNOLOGIES;"
    h_cursor.execute(sql_statement)
    result = h_cursor.fetchall()
    for row in result:
        tier_comp = row[0]
        tiercomp.append(tier_comp)
    return tiercomp


def mnc_duplication():
    tiercomp = []
    h_db, h_cursor = dbcon.AppInst.db_conn()
    sql_statement = "select MNCS_NAME FROM HPS.MNCS_COMPANIES;"
    h_cursor.execute(sql_statement)
    result = h_cursor.fetchall()
    for row in result:
        tier_comp = row[0]
        tiercomp.append(tier_comp.split(','))
    return tiercomp



def update_duplication(up_text):
    tiercomp = []
    h_db, h_cursor = dbcon.AppInst.db_conn()
    sql_statement = "select MNCS_NAME FROM HPS.MNCS_COMPANIES;"
    h_cursor.execute(sql_statement)
    result = h_cursor.fetchall()
    for row in result:
        tier_comp = row[0]
        tiercomp.append(tier_comp)
    mnc = up_text
    x = mnc.find("|") + 1
    x1 = mnc[x:]
    x1 = x1.split(',')
    c = 0
    d = 0
    if mnc.find("Tier-3") == 0:
        for i in x1:
            b = i.lstrip()
            a = b.rstrip()
            if a not in tiercomp[0].split(',') and a not in tiercomp[1].split(','):
                d = 1
            else:
                c += 1

    if mnc.find("Tier-2") == 0:
        for i in x1:
            b = i.lstrip()
            a = b.rstrip()
            if a not in tiercomp[0].split(',') and a not in tiercomp[2].split(','):
                d = 1
            else:
                c += 1

    if mnc.find("Tier-1") == 0:
        for i in x1:
            b = i.lstrip()
            a = b.rstrip()
            if a not in tiercomp[1].split(',') and a not in tiercomp[2].split(','):
                d = 1
            else:
                c = c + 1

    if c == 0:
        return "add"
