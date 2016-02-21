from flask import Flask , render_template , jsonify , request , g , send_file
import numpy as np
import base64
from random import randint
import os
import time
import cPickle as pickle
import cv2
from wand.image import Image

TEMP_FOLDER='tmp/'
OPENCV_PATH="/home/distro/Programs/opencv-3.0.0/"
ClassMapper={0:'0-2',1:'3-7',2:'8-12',3:'13-19',4:'20-36',5:'37-65',6:'66+'}
app = Flask(__name__)
app.config.from_object('config')
app.config['TEMP_FOLDER'] = TEMP_FOLDER
app.config['PIXELS']=64
app.config['OPENCV_PATH']=OPENCV_PATH

if not os.path.exists(app.config['TEMP_FOLDER']):
    os.makedirs(app.config['TEMP_FOLDER'])

# with open('net.pickle') as f:
#     net=pickle.load(f)
face_cascade = cv2.CascadeClassifier(app.config['OPENCV_PATH']+'data/haarcascades/haarcascade_frontalface_default.xml')

def readImage(obj,copy=0):
    filepath=os.path.join(app.config['TEMP_FOLDER'], "inputfile.jpg")
    obj.save(filepath)
    img=cv2.imread(filepath)
    if copy==1:
        imgcopy=np.copy(img)
        img=img/255
        return img,imgcopy
    else:
        img=img/255
        return img

def saveFaces(imgobj):
    fileprefix=str(int(time.time()))+str(randint(0,1000000))
    facefilenamelist=[]
    gray = cv2.cvtColor(imgobj, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    imgcopy=np.copy(imgobj)
    for (x,y,w,h),index in zip(faces,range(1,len(faces)+1)):
        face=(x,y,x+w,y+h)
        filename=fileprefix+"_"+str(index)+".jpg"
        facefilenamelist.append(filename)
        outfilepath=os.path.join(app.config['TEMP_FOLDER'], filename)
        roi=imgobj[face[1]:face[3],face[0]:face[2]]
        cv2.imwrite(outfilepath , roi)
        cv2.rectangle(imgcopy,(x,y),(x+w,y+h),(255,0,0),2)
        with Image(filename=outfilepath) as faceimg:
            faceimg.resize(app.config['PIXELS'], app.config['PIXELS'])
            faceimg.save(filename=outfilepath)
    outfilename=fileprefix+"_"+"imgwithfaces.jpeg"
    cv2.imwrite(os.path.join(app.config['TEMP_FOLDER'], outfilename), imgcopy)
    faces = [(int(x), int(y), int(x + w), int(y + h)) for (x, y, w, h) in faces]
    return (faces,facefilenamelist,outfilename)

def getAgeFromFace(filename):
    filepath=os.path.join(app.config['TEMP_FOLDER'], filename)
    img=cv2.imread(filepath)
    img=img.transpose(2,0,1).reshape(3,app.config['PIXELS'],app.config['PIXELS'])
    TestX = np.zeros((1,3, app.config['PIXELS'], app.config['PIXELS']), dtype='float32')
    TestX[0]=img
    # return net.predict(TestX)
    return [3]

def cleanUp(outfilename,facefilelist):
    basepath=app.config['TEMP_FOLDER']
    inputfilepath=os.path.join(basepath,"inputfile.jpg")
    outfilepath=os.path.join(basepath,outfilename)
    os.remove(inputfilepath)
    os.remove(outfilepath)
    for filename in facefilelist:
        filepath=os.path.join(basepath,filename)
        os.remove(filepath)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getAge/',methods=['POST'])
def getAge():
    start=time.time()
    data={"success":False}
    imgobj=request.files['file']
    if imgobj:
        img,imgcopy=readImage(imgobj,copy=1)
        faces,facefilelist,outfilename=saveFaces(imgcopy)
        encoded = base64.b64encode(open(os.path.join(app.config['TEMP_FOLDER'], outfilename), "rb").read())
        data["img"]=encoded
        data["num_faces"]=len(faces)
        facedatalist=[]
        for face,filename in zip(faces,facefilelist):
            facedict={'face':face}
            facedict['faceimg']=base64.b64encode(open(os.path.join(app.config['TEMP_FOLDER'], filename), "rb").read())
            facedict['age']=ClassMapper[getAgeFromFace(filename)[0]]
            facedatalist.append(facedict)
        data["faces"]=facedatalist
        data["success"]=True
    else:
        print "No file found"
        data["error"]="No URL provided"
    cleanUp(outfilename,facefilelist)
    print "Time Taken for executing query is "+str(time.time() - start)+" seconds"
    return jsonify(data)
        # img=img.transpose(2,0,1).reshape(3,app.config['PIXELS'],app.config['PIXELS'])

if __name__ == '__main__':
    app.run(debug=True)
