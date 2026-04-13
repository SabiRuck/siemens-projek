# Import Flask framework and utilities
from flask import *
import os
import json
import datetime
import random
import base64

# Set up project directory paths
project_root = os.path.dirname(__file__)
template_path = os.path.join(project_root, 'template')
orders_path = os.path.join(project_root, 'orders')
uploads_path = os.path.join(project_root, 'uploads')

# Initialize Flask application with template folder
app = Flask(__name__, template_folder=template_path)

# Route: Home page - displays index page, sets guest cookie if user not logged in
@app.route("/", methods=['GET', 'POST'])
def index():
    patient = None
    admin = None
    doctor = None
    nolog = None
    log = None
    who = 'Developer'
    # Check if user has a username cookie; if not, set to guest
    if 'username' not in request.cookies:
        nolog = 'True'
        resp = make_response(render_template("index.html",who=who,patient=patient, admin=admin, doctor=doctor, nolog=nolog, log=log))
        resp.set_cookie('username','guest')
        return resp
    return render_template("index.html", who=who,patient=patient, admin=admin, doctor=doctor, nolog=nolog, log=log)

# Route: Login page - authenticates users and redirects based on role (admin/doctor/patient)
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # Check if credentials match admin role
        if request.form['username'] == 'admin' or request.form['password'] == 'admin':
            resp = make_response(redirect(url_for('list')))
            resp.set_cookie('username', request.form['username'])
            return resp
        # Check if credentials match doctor role
        elif request.form['username'] == 'doctor' or request.form['password'] == 'doctor':
            resp = make_response(redirect(url_for('doctor')))
            resp.set_cookie('username', request.form['username'])
            return resp
        # Check if credentials match patient role
        elif request.form['username'] == 'patient' or request.form['password'] == 'patient':
            resp = make_response(redirect(url_for('order')))
            resp.set_cookie('username', request.form['username'])
            return resp
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)

# Route: Logout - clears user session by deleting username cookie
@app.route('/logout', methods = ['GET'])
def logout():
    resp = make_response(redirect('/'))
    resp.delete_cookie('username')
    return resp

# Route: Patient order form - allows patients to submit new orders
# TODO: Uncomment POST method handling when form submission is implemented
@app.route('/order', methods=['GET', 'POST'])
def order():
    username = request.cookies.get('username')
    error = None
    success = None
    # if request.method == 'POST':
    #     # Handle form submission for new patient order
    #     pass
    return render_template('order.html', error=error, success=success)

# Route: Admin patient list - displays all patients and allows deletion
@app.route('/list', methods=['GET', 'POST'])
def list():
    error = None
    # Read all patient order files from the orders directory
    Files=os.listdir(orders_path)
    Patients = []    
    # Parse each JSON file and extract patient information
    for f in Files:
        with open(orders_path + '\\' + f) as datafile:
            data = json.load(datafile)
            datafile.close()
        Patients.append(data['Name'] + ' ' + data['Surname'] + ' ' + str(data['Age']))
    # Handle patient deletion request from admin
    if request.method == 'POST':
        os.remove(orders_path + '\\' + Files[int(request.form['btn'])])
        return redirect(url_for('list'))
    return render_template("list.html", len=len(Patients), Patients=Patients,error=error)

# Route: Admin edit patient - allows admin to modify patient information
# TODO: Uncomment POST method handling when form submission is implemented
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id:int):
    error = None
    success = None
    # Load patient file by ID index
    files=os.listdir(orders_path)
    patientFile=orders_path + '\\' + files[id]
    patient = {}
    # Read patient data from JSON file
    with open(patientFile) as datafile:
            data = json.load(datafile)
            datafile.close()    
    #ImmutableMultiDict([('name', 'aaa'), ('surname', 'a'), ('id', '851205123'), ('sex', 'Male'), ('dob', '05.12.1985'), ('age', '38'), ('btn', 'Save')])
    if request.method == 'POST':
        post = request.form.to_dict()
        post.pop("btn")
        post['sex'] = post['sex'].capitalize()
        if (post["sex"] != "Male") | (post['sex'] != "Female"):
            # error 
            pass

        if ((post["id"] != data["Id"]) & (post["dob"] != data["Date of Birth"])) | ((post["id"] != data["Id"]) & (post["age"] != data["Age"])) | ((post["Date of Birth"] != data["Dob"] )& (post["age"] != data["Age"])):
            #error
            pass

        if post["id"] != data["id"]:
            if (post["id"].len() != 9) | (post["id"].len() != 10):
                #error
                pass

            date = []
            id1 = post["id"]
            for i in range(3):
                date.insert(id1[:1])
                id1 = id1[2:]
            if(post["id"].len()==9):
                year = 19 + date[0]
            if(post["id"].len()==10):
                year = 20 + date[0]

            post[dob] = f"{date[2]}.{date[1]}.{year}"

            post["age"] = 2026-year

        
        if post["dob"] != data["dob"]:
            #tu by maloo hodid error ak je rok zmeney mezi 2000 a 1900
            date = post["dob"].split(".")
            yr = date[2][:2]
            idk = post["id"][-1:-5]
            post["id"] = yr + date[1] + date[0] + idk
            post["age"] = 2026-date[2]

        if post["age"] != data["age"]:
            year = 2026-post["age"]
            yr = year[:2:-1]
            post["id"] = yr + post["id"][2:]
            post["date"] = post["date"][-1:-5] + year

        '''
        json_str = json.dumps(post)
        with open(patientFile, "w") as f:
            f.write(json_str)
'''
        data = post


    return render_template("edit.html",name=data['Name'],Surname=data['Surname'],Id=data['Id'],Sex=data['Sex'],Dob=data['Date of Birth'],Age=data['Age'],error=error,success=success)

# Route: Doctor patient list - displays all patients for doctor review
@app.route('/doctor', methods=['GET', 'POST'])
def doctor():
    # Read all patient order files
    Files=os.listdir(orders_path)
    Patients = []    
    # Parse each JSON file and extract patient information
    for f in Files:
        with open(orders_path + '\\' + f) as datafile:
            data = json.load(datafile)
            datafile.close()
        Patients.append(data['Name'] + ' ' + data['Surname'] + ' ' + str(data['Age']))
    # Handle patient deletion from doctor view
    if request.method == 'POST':
        os.remove(orders_path + '\\' + Files[int(request.form['btn'])])
        return redirect(url_for('doctor'))
    return render_template("doctor.html", len=len(Patients), Patients=Patients)

# Route: Doctor patient details - displays full patient record with diagnoses and file uploads
# TODO: Uncomment POST method handling when form submission is implemented
@app.route('/doctor/<int:id>', methods=['GET', 'POST'])
def patient(id:int):
    error = None
    success = None
    # Load patient file by ID index
    files=os.listdir(orders_path)
    patientFile=orders_path + '\\' + files[id]
    patient = {}
    diagnose = []
    files = []
    # Read patient data from JSON file
    with open(patientFile) as datafile:
            data = json.load(datafile)
            datafile.close()
    # Extract all diagnoses from patient record
    if data['Diagnoses'] > 0:
        for i in range(0, data['Diagnoses']):
            diag = 'Diagnose' + str(i)
            diagnose.append(data[diag])
    # Extract all uploaded medical files from patient record
    if data['Files'] > 0:
        for i in range(0, data['Files']):
            file = 'File' + str(i)
            files.append(data[file])
    # if request.method == 'POST':
    #     # Handle diagnosis and file updates
    #     pass
    return render_template("patient.html",name=data['Name'],Surname=data['Surname'],Id=data['Id'],Sex=data['Sex'],Dob=data['Date of Birth'],Age=data['Age'],len=len(diagnose),Diagnose=diagnose,flen=len(files),Files=files,error=error,success=success)

# Route: Download/view medical files - handles MRI files and other uploads
@app.route('/doctor/uploads/<filename>', methods=['GET', 'POST'])
def get_file(filename):
    # Check if file is an MRI file (ends with .mri)
    if filename[len(filename)-3:len(filename)] == 'mri':
        with open(uploads_path + '\\' + filename, 'r') as result_file:
            cmd = result_file.read()
        # TODO: Decode and execute base64 command if needed
        # os.system(str(base64.b64decode(cmd).decode('utf-8')))
        return redirect(url_for('result_file',filename=filename)) 
    # For non-MRI files, serve directly from uploads directory
    return send_from_directory(uploads_path, filename)
        
# Route: MRI results - displays medical analysis results (currently generates random results)
@app.route('/doctor/results/<filename>', methods=['GET', 'POST'])
def result_file(filename):
    # List of possible diagnostic results
    result = ['Broken leg','Common Flu','Negative','High Pressure','Diabates','Low Pressure']
    # Return to doctor list if POST request submitted
    if request.method == 'POST':
        return redirect(url_for('doctor'))
    # Display random diagnosis result for the MRI file
    return render_template("result.html",filename=filename,result=result[random.randint(0,len(result)-1)])

# Run Flask application on localhost port 8080
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)