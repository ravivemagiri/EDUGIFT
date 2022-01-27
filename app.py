from cv2 import add
from django.shortcuts import render
from flask import Flask, redirect, render_template, request, session, url_for
import sqlite3

from datetime import datetime



app = Flask(__name__)
app.secret_key = "RAVI VEMAGIRI"

from datetime import date
import time

def get_status_of_session(given_date, st_time, ed_time):
    today = date.today()
    today = [int(x) for x in str(today).split("-")]
    print(today)

    # given_date = "2022-01-25"
    given_date = [int(x) for x in str(given_date).split("-")]

    # st_time = "20:30"
    # ed_time = "21:30"
    st_time = [int(x) for x in str(st_time).split(":")]
    ed_time = [int(x) for x in str(ed_time).split(":")]


    time_tracked = time.localtime()

    status = "This session is expired already."
    if given_date[0] >= today[0]:
        if given_date[1] >= today[1]:
            if given_date[2]==today[2]:
                if time_tracked.tm_hour >= st_time[0] and time_tracked.tm_hour<= ed_time[0]:
                    if time_tracked.tm_min < st_time[1]:
                        status = "Upcoming session"
                    else:
                        status = "Session in progress"
                else:
                    status = status
            elif given_date[2]>today[2]:
                status = "Upcoming session"
            else:
                status = status
        else:
            status = status
    else:
        status = status
    return status

@app.route('/')
def index():   
    return render_template('index.html')

@app.route('/error_page')
def error_page():   
    return render_template('error.html')

@app.route("/volunteer_session")
def volunteer_session():
    return render_template('teacher_session.html')

@app.route("/volunteer_files")
def volunteer_files():
    return render_template('docs.html')

@app.route("/volunteer_uploaded_videos")
def volunteer_uploaded_videos():
    conn = sqlite3.connect('student_details.db')
    vol_videos = conn.execute("select * from VOLUNTEER_VIDEO")
    conn.commit()   
    all_videos = vol_videos.fetchall()
    all_video_inf = []
    for each_query in all_videos:
        temp = (each_query[0], each_query[1], each_query[2].replace("watch?v=", "embed/"), each_query[3])
        all_video_inf.append(temp)
    return render_template('volunteer_videos.html', query_inf = all_video_inf)

@app.route("/volunteer_sessions")
def volunteer_sessions():
    conn = sqlite3.connect('student_details.db')
    vol_sessions = conn.execute("select * from VOLUNTEER_SESSION")
    conn.commit()   
    no_of_records = vol_sessions.fetchall()
    query_inf = []
    for each_query in no_of_records:
        try:
            vol_details = conn.execute('select * from VOLUNTEER_DETAILS WHERE EMAIL = "{}"'.format(str(each_query[1])))
            conn.commit()
            vol_account = vol_details.fetchone()
            name_of_volunteer = vol_account[3] + " " + vol_account[4]
            gender = vol_account[5]
            email = vol_account[1]
            address = vol_account[8]
            aoe = vol_account[9]
            topic_name = each_query[2]
            meeting_id = each_query[3]
            start_time = each_query[4]
            end_time = each_query[5]
            meeting_desc = each_query[6]
            session_date = each_query[7]
            status = get_status_of_session(session_date, start_time, end_time)
            if "expired" in status:
                meeting_id = "#"
            temp = [meeting_id, name_of_volunteer, email, gender, address, aoe, status, topic_name, start_time, end_time, session_date, meeting_desc]
            query_inf.append(temp)
        except:
            pass
    return render_template('view_sessions.html', query_inf = query_inf)

@app.route("/student_doubt_posting", methods=["POST", "GET"])
def student_doubt_posting():
    msg = ''
    if request.method == 'POST':
        topic_name = str(request.form['topic_name'])
        if topic_name !="":
            posting_date = str(request.form['posting_date'])
            query_desc = str(request.form['query_desc'])

            conn = sqlite3.connect('student_details.db')
            student_results = conn.execute("select * from POST_DOUBT")
            no_of_records = len(student_results.fetchall())
            sqlite_insert_query = 'INSERT INTO POST_DOUBT VALUES ("{}","{}", "{}", "{}", "{}")'.format(no_of_records+1, session["username"],topic_name, posting_date, query_desc)
            conn.execute(sqlite_insert_query)
            conn.commit()
            conn.close()
            msg = 'Successfully posted your query to Instructor portal !'
        else:
            msg = 'Please fill your query to post.'

    else:
        msg = 'Please fill out the form !'
    return render_template('post_a_doubt.html', msg =msg)    

@app.route("/student_profile_page")
def student_profile_page():
    if session["username"] != 'None':
        conn = sqlite3.connect('student_details.db')
        student_results = conn.execute('select * from STUDENT_DETAILS WHERE email = "{}"'.format(str(session["username"])))
        account = student_results.fetchone()
        return render_template('student_account.html', account_details = account)
    else:
        return redirect(url_for('index'))

@app.route("/volunteer_session_planner", methods=["POST", "GET"])
def volunteer_session_planner():
    msg = ''
    if request.method == 'POST' and 'topic_name' in request.form and 'starttime' in request.form and request.form['topic_name']!="":
        
        topic_name = str(request.form['topic_name'])
        start_time = str(request.form['starttime'])
        end_time = str(request.form['endtime'])
        meeting_id = str(request.form['meeting_id'])
        meeting_desc = str(request.form['meet_desc'])
        dt_string = str(request.form['session_date'])
        print(topic_name, start_time, end_time, meeting_id, meeting_desc)
        conn = sqlite3.connect('student_details.db')
        student_results = conn.execute("select * from VOLUNTEER_SESSION")
        no_of_records = len(student_results.fetchall())
       
        sqlite_insert_query = 'INSERT INTO VOLUNTEER_SESSION VALUES ("{}","{}", "{}", "{}", "{}", "{}"," {}", "{}")'.format(no_of_records+1, session["username"], topic_name, meeting_id, start_time, end_time, meeting_desc, dt_string)
        conn.execute(sqlite_insert_query)
        conn.commit()
        conn.close()
        msg = 'All the best! Successfully saved your session!'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'

    return render_template('session_planner.html',msg = msg)

@app.route("/volunteer_invoice")
def volunteer_invoice():
    return render_template('orders.html')

@app.route("/volunteer_doubts")
def volunteer_doubts():
    conn = sqlite3.connect('student_details.db')
    student_results = conn.execute("select * from POST_DOUBT")
    conn.commit()   
    no_of_records = student_results.fetchall()
    query_inf = []
    for each_query in no_of_records:
        try:
            student_details = conn.execute('select * from STUDENT_DETAILS WHERE EMAIL = "{}"'.format(str(each_query[1])))
            conn.commit()
            stu_account = student_details.fetchone()
            name_of_student = stu_account[3] + " " + stu_account[4]
            query_inf.append([each_query[4], name_of_student, each_query[3], each_query[2]])
        except:
            pass
    return render_template('students_doubt_platform.html', query_inf = query_inf)

@app.route("/volunteer_video", methods = ["POST", "GET"])
def volunteer_video():
    msg = ''
    if request.method == 'POST' and 'video_url' in request.form:
        video_url = str(request.form['video_url'])
        if len(video_url)>5:
            conn = sqlite3.connect('student_details.db')

            student_results = conn.execute("select * from VOLUNTEER_VIDEO")
            no_of_records = len(student_results.fetchall())
            now = datetime.now()
            # dd/mm/YY H:M:S
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

            sqlite_insert_query = 'INSERT INTO VOLUNTEER_VIDEO VALUES ("{}","{}", "{}", "{}")'.format(no_of_records+1, session['username'], video_url, dt_string)
            conn.execute(sqlite_insert_query)
            conn.commit()
            conn.close()
            msg = "Successfully uploaded the video to the student Portal. We wish you a very happy earnings."
        else:
            msg = "Sorry. No data found to upload. Please try again."
    else:
        msg = "Sorry. No data found to upload. Please try again."
    return  render_template('upload_video.html', msg = msg)

@app.route("/volunteer_profile")
def volunteer_profile():
    if session["username"] != 'None':
        conn = sqlite3.connect('student_details.db')
        volunteer_results = conn.execute('select * from VOLUNTEER_DETAILS WHERE email = "{}"'.format(str(session["username"])))
        account = volunteer_results.fetchone()
        return render_template('account.html', account_details = account)
    else:
        return redirect(url_for('index'))

@app.route("/student_home")
def student_home():
    return render_template('student_home.html', user=session['username'])

@app.route("/volunteer_home")
def volunteer_home():
    return render_template('volunteer_home.html', user=session['username'])

@app.route("/student_login", methods= ["POST", "GET"])
def student_login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        username = str(request.form['email'])
        password = str(request.form['password'])
        conn = sqlite3.connect('student_details.db')
        student_results = conn.execute('select * from STUDENT_DETAILS WHERE email = "{}" and password = "{}" '.format(username, password))
        account = student_results.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account[1]
            msg = 'Logged in successfully !'
            print(session['username'], "here")
            return redirect(url_for('student_home'))
        else:
            msg = 'Sorry. Invalid username / password !'
        conn.commit()
        conn.close()        
    return render_template('student_login.html', msg = msg)

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('index'))
   
@app.route("/confirm_type_of_login")
def confirm_type_of_login():
    return render_template('login_conf.html')

@app.route("/student_register", methods = ["POST", "GET"])
def student_register():
    msg = ''
    if request.method == 'POST' and 'fname' in request.form and 'password' in request.form and 'lname' in request.form :
        email = str(request.form['email'])
        password = str(request.form['password'])
        fname = str(request.form['fname'])
        lname = str(request.form['lname'])
        gender = str(request.form['radiogroup1'])
        contact = str(request.form['contact_num'])
        address = str(request.form['address'])
        class_studying = str(request.form['class_studying'])
        print(email, password, fname, lname, gender, contact, address, class_studying)
        conn = sqlite3.connect('student_details.db')
        student_results = conn.execute("select * from STUDENT_DETAILS")
        no_of_records = len(student_results.fetchall())
        sqlite_insert_query = 'INSERT INTO STUDENT_DETAILS VALUES ("{}","{}", "{}", "{}", "{}", "{}"," {}", "{}"," {}")'.format(no_of_records+1, email, password, fname, lname, gender, contact, address, class_studying)
        conn.execute(sqlite_insert_query)
        conn.commit()
        conn.close()
        msg = 'Hurray! Successfully joined EDUGIFT student community !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
        
    return render_template('student_register.html', msg = msg)
    
@app.route("/volunteer_registration", methods = ["POST", "GET"])
def volunteer_registration():
    msg = ''
    if request.method == 'POST' and 'fname' in request.form and 'password' in request.form and 'lname' in request.form :
        email = str(request.form['email'])
        password = str(request.form['password'])
        fname = str(request.form['fname'])
        lname = str(request.form['lname'])
        gender = str(request.form['radiogroup1'])
        contact = str(request.form['contact_num'])
        workhours = str(request.form['workhours'])
        address = str(request.form['address'])
        aoe = str(request.form['aoe'])
        conn = sqlite3.connect('student_details.db')
        volunteer_results = conn.execute("select * from VOLUNTEER_DETAILS")
        no_of_records = len(volunteer_results.fetchall())
        sqlite_insert_query = 'INSERT INTO VOLUNTEER_DETAILS VALUES ("{}","{}", "{}", "{}", "{}", "{}"," {}", "{}", "{}"," {}")'.format(no_of_records+1, email, password, fname, lname, gender, contact, workhours, address, aoe)
        conn.execute(sqlite_insert_query)
        conn.commit()
        conn.close()
        msg = 'Hurray! You are a valuable EDUGIFT Volunteer group now!'
    elif request.method == 'POST':
        msg = 'Please fill all the details !'
        
    return render_template('volunteer_register.html', msg = msg)

@app.route("/volunteer_login", methods=["POST", "GET"])
def volunteer_login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        username = str(request.form['email'])
        password = str(request.form['password'])
        conn = sqlite3.connect('student_details.db')
        student_results = conn.execute('select * from VOLUNTEER_DETAILS WHERE email = "{}" and password = "{}" '.format(username, password))
        account = student_results.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account[1]
            msg = 'Logged in successfully !'
            print(session['username'], "here")
            return redirect(url_for('volunteer_home'))
        else:
            msg = 'Sorry! Invalid username / password!'
        conn.commit()
        conn.close()        
    return render_template('volunteer_login.html', msg=msg)






if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000', debug=True)
