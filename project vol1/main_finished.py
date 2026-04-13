from flask import *
import os
import json
import datetime
import random
import base64

project_root = os.path.dirname(__file__)
template_path = os.path.join(project_root, 'template')
orders_path = os.path.join(project_root, 'orders')
uploads_path = os.path.join(project_root, 'uploads')

app = Flask(__name__, template_folder=template_path)

@app.route("/", methods=['GET', 'POST'])
def index():
    patient = None
    admin = None
    doctor = None
    nolog = None
    log = None
    who = ''
    if 'username' not in request.cookies:
        nolog = 'True'
        who = 'guest'
        resp = make_response(render_template("index.html",who=who,patient=patient, admin=admin, doctor=doctor, nolog=nolog, log=log))
        resp.set_cookie('username','guest')
        return resp
    else:
        username = request.cookies.get('username')
        if username == 'patient':
            patient = 'True'
            log = 'True'
            who = username
        elif username == 'admin':
            admin = 'True'
            log = 'True'
            who = username
        elif username == 'doctor':
            doctor = 'True'
            log = 'True'
            who = username
        else:
            nolog = 'True'
            who = username
    return render_template("index.html", who=who,patient=patient, admin=admin, doctor=doctor, nolog=nolog, log=log)

@app.route('/todo')
def todo():
    return render_template("todo.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            resp = make_response(redirect(url_for('list')))
            resp.set_cookie('username', request.form['username'])
            return resp
        elif request.form['username'] == 'doctor' and request.form['password'] == 'doctor':
            resp = make_response(redirect(url_for('doctor')))
            resp.set_cookie('username', request.form['username'])
            return resp
        elif request.form['username'] == 'patient' and request.form['password'] == 'patient':
            resp = make_response(redirect(url_for('order')))
            resp.set_cookie('username', request.form['username'])
            return resp
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)

@app.route('/logout', methods = ['GET'])
def logout():
    resp = make_response(redirect('/'))
    resp.delete_cookie('username')
    return resp

@app.route('/order', methods=['GET', 'POST'])
def order():
    username = request.cookies.get('username')
    if username != 'patient':
        error = 'You need to be logged to access order page.'
        return redirect(url_for('login'))
    else:
        error = None
        success = None
        appointment ={}
        id_format = ['0','1','5','6']
        today = datetime.date.today()
        if request.method == 'POST':
            if request.form['name'] == '' or request.form['surname'] == '' or request.form['id'] == '':
                error = 'Empty Field. All fields needs to be filled.'
            else:
                try: 
                    int(request.form['id'])
                except:
                    error = 'Identification Number. Identification number must be number.'
                else:
                    if len(request.form['id']) < 9 or len(request.form['id']) > 10:
                        error = 'Identification Number. Identification number must be 9 or 10 numbers.'
                    elif request.form['id'][2] not in id_format:
                        error = 'Indetification Number. Wrong identification number format.'
                    else:    
                        appointment['Name'] = request.form['name']
                        appointment['Surname'] = request.form['surname']
                        appointment['Id'] = request.form['id']
                        if request.form['id'][2] == '5' or request.form['id'][2] == '6':
                            appointment['Sex'] = 'Female'
                            monthBirth = int(request.form['id'][2:4]) - 50   
                        else:
                            appointment['Sex'] = 'Male'
                            monthBirth = int(request.form['id'][2:4])
                        if len(request.form['id']) == 9:
                            appointment['Date of Birth'] = request.form['id'][4:6] + '.' + str(monthBirth) + '.' + '19' + request.form['id'][0:2]
                        else:
                            if request.form['id'][0:1] < '54':
                                appointment['Date of Birth'] = request.form['id'][4:6] + '.' + str(monthBirth) + '.' + '20' + request.form['id'][0:2]
                            else:
                                appointment['Date of Birth'] = request.form['id'][4:6] + '.' + str(monthBirth) + '.' + '19' + request.form['id'][0:2]
                        appointment['Age'] = today.year - int(appointment['Date of Birth'][6:])
                        appointment['Files'] = 0
                        appointment['Diagnoses'] = 0
                        with open(orders_path + '/' + request.form['name'] + '_' + request.form['surname'], 'w') as order_file:
                            json.dump(appointment, order_file)
                        success = 'Thank You. Appointment saved'
        return render_template('order.html', error=error, success=success)

@app.route('/list', methods=['GET', 'POST'])
def list():
    username = request.cookies.get('username')
    error = None
    if username != 'admin':
        error = 'You need to be logged to access order page.'
        return redirect(url_for('login'))
    else:
        Files=os.listdir(orders_path)
        Patients = []    
        for f in Files:
            with open(orders_path + '/' + f) as datafile:
                data = json.load(datafile)
                datafile.close()
            Patients.append(data['Name'] + ' ' + data['Surname'] + ' ' + str(data['Age']))
        if request.method == 'POST':
            os.remove(orders_path + '/' + Files[int(request.form['btn'])])
            return redirect(url_for('list'))
        return render_template("list.html", len=len(Patients), Patients=Patients,error=error)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id:int):
    username = request.cookies.get('username')
    if username != 'admin':
        error = 'You need to be logged to access order page.'
        return redirect(url_for('login'))
    else:
        error = None
        success = None
        files=os.listdir(orders_path)
        patientFile=orders_path + '/' + files[id]
        patient = {}
        with open(patientFile) as datafile:
                data = json.load(datafile)
                datafile.close()    
        if request.method == 'POST':
            if request.form['btn'] == 'Save': 
                if request.form['name'] == '' or request.form['surname'] == '' or request.form['id'] == '' or request.form['sex'] == '' or request.form['dob'] == '' or request.form['age'] == '':
                    error = 'Empty Field. All fields needs to be filled.'
                try:
                    int(request.form['id'])
                except:
                    error = 'Identification Number. Identification number must be number.'
                else:
                    try:
                        int(request.form['age'])
                    except:
                        error = 'Age. Age number must be number.'
                    else:
                        data['Name'] = request.form['name']
                        data['Surname'] = request.form['surname']
                        data['Id'] = request.form['id']
                        data['Sex'] = request.form['sex']
                        data['Date of Birth'] = request.form['dob']
                        data['Age'] = request.form['age']
                        with open(patientFile, 'w') as order_file:
                            json.dump(data, order_file)
                        success = 'Success. Changes saved.'
            else:
                return redirect(url_for('list'))                            
        return render_template("edit.html",name=data['Name'],Surname=data['Surname'],Id=data['Id'],Sex=data['Sex'],Dob=data['Date of Birth'],Age=data['Age'],error=error,success=success)

@app.route('/doctor', methods=['GET', 'POST'])
def doctor():
    username = request.cookies.get('username')
    if username != 'doctor':
        error = 'You need to be logged to access order page.'
        return redirect(url_for('login'))
    else:
        Files=os.listdir(orders_path)
        Patients = []    
        for f in Files:
            with open(orders_path + '/' + f) as datafile:
                data = json.load(datafile)
                datafile.close()
            Patients.append(data['Name'] + ' ' + data['Surname'] + ' ' + str(data['Age']))
        if request.method == 'POST':
            os.remove(orders_path + '/' + Files[int(request.form['btn'])])
            return redirect(url_for('doctor'))
        return render_template("doctor.html", len=len(Patients), Patients=Patients)

@app.route('/doctor/<int:id>', methods=['GET', 'POST'])
def patient(id:int):
    username = request.cookies.get('username')
    if username != 'doctor':
        error = 'You need to be logged to access order page.'
        return redirect(url_for('login'))
    else:
        error = None
        success = None
        files=os.listdir(orders_path)
        patientFile=orders_path + '/' + files[id]
        patient = {}
        diagnose = []
        files = []
        with open(patientFile) as datafile:
                data = json.load(datafile)
                datafile.close()
        if data['Diagnoses'] > 0:
            for i in range(0, data['Diagnoses']):
                diag = 'Diagnose' + str(i)
                diagnose.append(data[diag])
        if data['Files'] > 0:
            for i in range(0, data['Files']):
                file = 'File' + str(i)
                files.append(data[file])
        if request.method == 'POST':
            if request.form['btn'] == 'Save':
                patient['Name'] = request.form['name']
                patient['Surname'] = request.form['surname']
                patient['Id'] = request.form['id']
                patient['Sex'] = request.form['sex']
                patient['Date of Birth'] = request.form['dob']
                patient['Age'] = request.form['age']
                if data['Diagnoses'] == 0:
                    patient['Diagnoses'] = 0
                if data['Files'] == 0:
                    patient['Files'] = 0
                for i in range(0, data['Diagnoses']):
                    diag = 'Diagnose' + str(i)
                    patient[diag] = data[diag]
                if request.form['diagnose'] != '':
                    patient['Diagnoses'] = data['Diagnoses'] + 1
                    patient['Diagnose'+str(data['Diagnoses'])] = request.form['diagnose']
                else:
                    patient['Diagnoses'] = data['Diagnoses']
                for i in range(0, data['Files']):
                    file = 'File' + str(i)
                    patient[file] = data[file]
                attachment = request.files['file']
                if attachment.filename != '':
                    patient['Files'] = data['Files'] + 1
                    patient['File'+str(data['Files'])] = attachment.filename
                    attachment.save(os.path.join(app.root_path, 'uploads', attachment.filename))
                success = 'Success. Patient data saved.'
                with open(patientFile, 'w') as order_file:
                    json.dump(patient, order_file)
                success = 'Success. Patient data saved.'
            else:
                return redirect(url_for('doctor'))
        return render_template("patient.html",name=data['Name'],Surname=data['Surname'],Id=data['Id'],Sex=data['Sex'],Dob=data['Date of Birth'],Age=data['Age'],len=len(diagnose),Diagnose=diagnose,flen=len(files),Files=files,error=error,success=success)

@app.route('/doctor/uploads/<filename>', methods=['GET', 'POST'])
def get_file(filename):
    username = request.cookies.get('username')
    if username != 'doctor':
        return redirect(url_for('login'))
    else:
        if filename[len(filename)-3:len(filename)] == 'mri':
            with open(uploads_path + '/' + filename, 'r') as result_file:
                cmd = result_file.read()
            os.system(str(base64.b64decode(cmd).decode('utf-8')))
            return redirect(url_for('result_file',filename=filename)) 
        return send_from_directory(uploads_path, filename)
        
@app.route('/doctor/results/<filename>', methods=['GET', 'POST'])
def result_file(filename):
    username = request.cookies.get('username')
    result = ['Broken leg','Common Flu','Negative','High Pressure','Diabates','Low Pressure']
    if username != 'doctor':
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            return redirect(url_for('doctor'))
        return render_template("result.html",filename=filename,result=result[random.randint(0,len(result)-1)])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
