import falcon
#from waitress import serve
from keras.preprocessing.image import img_to_array
import imutils
import cv2
from keras.models import load_model
import numpy as np
from PIL import Image
import json
from falcon_multipart.middleware import MultipartMiddleware
import os
import sys

class ImageResource(object):
    #def on_get(self, req, resp):
     #   resp.status = falcon.HTTP_200
     #   resp.body = "hello world"
    def on_post(self, req, resp):
        """
        POST METHOD
        """
        emotion_container = {}
        detection_model_path = '/home/marce/Falcon_API/haarcascade_files/haarcascade_frontalface_default.xml'
        emotion_model_path = '/home/marce/Falcon_API/models/_mini_XCEPTION.102-0.66.hdf5'
        face_detection = cv2.CascadeClassifier(detection_model_path)
        emotion_classifier = load_model(emotion_model_path, compile=False)
        EMOTIONS = ["angry" ,"disgust","scared", "happy", "sad", "surprised", "neutral"]
        input_file = req.get_param('file')
        frame = cv2.imread(input_file)
        frame = imutils.resize(frame,width=300)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_detection.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE)
    
        canvas = np.zeros((250, 300, 3), dtype="uint8")
        frameClone = frame.copy()


        if len(faces) > 0:
            faces = sorted(faces, reverse=True,
            key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
            (fX, fY, fW, fH) = faces
                    # Extract the ROI of the face from the grayscale image, resize it to a fixed 28x28 pixels, and then prepare
            # the ROI for classification via the CNN
            roi = gray[fY:fY + fH, fX:fX + fW]
            roi = cv2.resize(roi, (64, 64))
            roi = roi.astype("float") / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)
        
        
            preds = emotion_classifier.predict(roi)[0]
            emotion_probability = np.max(preds)
            label = EMOTIONS[preds.argmax()]
    
        else: pass

        for (i, (emotion, prob)) in enumerate(zip(EMOTIONS, preds)):
    #text = "{}: {:.2f}%".format(emotion, prob * 100)
            emotion_container.update({ emotion : float("{:.2f}".format(prob * 100))})

        to_json= json.dumps(emotion_container)
        resp.status = falcon.HTTP_200
        resp.body = to_json

        
        
        # Test if the file was uploaded
        if input_file.filename:
            # Retrieve filename
            filename = input_file.filename

            # Define file_path
            file_path = os.path.join("images", filename)

            # Write to a temporary file to prevent incomplete files
            # from being used.
            temp_file_path = file_path + '~'

            open(temp_file_path, 'wb').write(input_file.file.read())

            # Now that we know the file has been fully saved to disk
            # move it into place.
            os.rename(temp_file_path, file_path)

            resp.status = falcon.HTTP_201
            resp.body = "hello world"

#app = falcon.API()
app = falcon.API(middleware=[MultipartMiddleware()])
app.req_options.auto_parse_form_urlencoded=True

faceemotion = ImageResource()

app.add_route('/api/upload', faceemotion)
#serve(app, listen='*:8080')