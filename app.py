import os

from flask import Flask, render_template, request, redirect, session
from flask import make_response, jsonify
from flask_session.__init__ import Session
import cv2
import numpy as np
from flask import Flask
from flask_mail import Mail, Message

from ocr_core import ocr_core
import fpdf
from flask import send_file
import random
import string


UPLOAD_FOLDER = '/static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
extracted_text=''
fpdf.set_global("SYSTEM_TTFONTS", os.path.join(os.path.dirname(__file__),'fonts'))

app = Flask(__name__)
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'tedtesande@gmail.com'
app.config['MAIL_PASSWORD'] = '07162078'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

sess = Session()
app.secret_key = 'sfskjh873##$gfh'
app.config['SESSION_TYPE'] = 'filesystem'

sess.init_app(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/', methods=['GET', 'POST'])
@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    try:
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                return render_template('index.html', msg='No file selected')
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                return render_template('index.html', msg='No file selected')

            if file and allowed_file(file.filename):
                file.save(os.path.join(os.getcwd() + UPLOAD_FOLDER, file.filename))
                APP_ROOT = os.path.dirname(os.path.abspath(__file__))
                filepath = os.path.join(APP_ROOT, 'static/uploads/', file.filename)
                
                #return filepath
                img = cv2.imread(filepath)
                
                gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                
                gray, img_bin = cv2.threshold(gray,128,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                gray = cv2.bitwise_not(img_bin)
                kernel = np.ones((2, 1), np.uint8)
                
                img = cv2.erode(gray, kernel, iterations=1)
                img = cv2.dilate(img, kernel, iterations=1)
                #out_below = pytesseract.image_to_string(img)
                # call the OCR function on it
                #return filepath
                # call the OCR function on it
                extracted_text = ocr_core(file)
                pdf = fpdf.FPDF()
                
                fontpath = os.path.join(APP_ROOT, 'fonts','GeezAble.ttf')
                pdf.add_page()
                pdf.set_xy(0, 0)
                pdf.add_font('GeezAble', style="B", fname=fontpath, uni=True)
                pdf.set_font('GeezAble', 'B', 13.0)
                pdf.multi_cell( h=5.0,  align='J', w=0, txt=' ', border=0)
                pdf.multi_cell( h=10.0,  align='J', w=0, txt=extracted_text.replace('\n','').rstrip('\n'), border=0)
                char_set = string.ascii_uppercase + string.digits
                filename = os.path.splitext(os.path.basename(os.path.join(app.root_path, 'static/uploads/', file.filename)))[0].join(random.sample(char_set*6, 6))
                filename=(filename.strip(), filename[0:30].strip() )[len(filename) > 30]
                pdf.output(os.path.join(app.root_path, 'static/uploads/', filename.strip() + ".pdf"), 'F')
                # extract the text and display it
                session['my_var'] = filename + ".pdf"
                write_to_doc(extracted_text, filename)
                res=jsonify(message="File uploaded",
                msg="Successfully processed", flag=True, extracted_text= extracted_text, img_src=UPLOAD_FOLDER + file.filename,
                name=filename + ".pdf", namedoc=filename + ".doc", nametxt=filename + ".txt")
                return res
                # return render_template('index.html',
                #                     msg='Successfully processed', flag=True,
                #                     extracted_text=extracted_text,
                #                     img_src=UPLOAD_FOLDER + file.filename, name=filename + ".pdf")
            else:
                res=jsonify(msg="format_error")
                return res  
                #return render_template('index.html', msg1=" Not allowed file format")  
        elif request.method == 'GET':
            return render_template('index.html', msg='')
    except:
        res1=jsonify(msgexe="txt-err")
        return res1
      #return render_template('index.html')


@app.route('/pdf1/<uuid>')
def to_pdf1(uuid):
    try:
            #my_var = session.get('my_var', None)
            #return uuid
            path=os.path.join(app.root_path, 'static/uploads/', uuid)
            #path=path.replace("//","/")
            #return path
            return send_file(path, as_attachment=True, cache_timeout=0)
            #return app.send_static_file('test.pdf', cache_timeout=app.config['FILE_DOWNindex_CACHE_TIMEOUT'])
    except:
            return render_template('index.html', msg1="xtx-err")



def write_to_doc(extracted_text, filename):
        fdoc= open("static/uploads/" + filename + ".doc","w+", encoding='utf-8')
        ftxt=open("static/uploads/" + filename + ".txt", "w+", encoding='utf-8')
        fdoc.writelines(extracted_text)
        ftxt.writelines(extracted_text)
        fdoc.close()
        ftxt.close()


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    try:
        if request.method == 'POST':
            senderName=request.form['txtName']
            
            senderEmail=request.form['txtEmail']
            senderMsg=request.form['txtMsg']
            
            msg = Message("OCR-Tigrinya" + senderName ,
                        sender=senderEmail,
                        recipients=['tta2yta@gmail.com'])
            
            msg.body = "Sender Emal= " + senderEmail + " " + " Sender Message= " + senderMsg
            # msg.add_alternative()
                            
            mail.send(msg)
            return render_template("contactus.html", msg="Thank You. You have Succesfully sent an email")

        elif request.method == 'GET':
            return render_template("contactus.html")
    except:
        return render_template("contactus.html", msg="Please Try Again")



if __name__ == '__main__':
   app.run(host="0.0.0.0", port=5000, debug=True)
