# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import uuid
import pyqrcode
import io 
import os

from flask import Flask, request, abort, redirect, jsonify, send_file

from google.auth import app_engine
from google.cloud import datastore

# Global configuration
CONFIG_ID = os.environ.get("PLACE_CHECKIN_CONFIG_ID") if os.getenv("PLACE_CHECKIN_CONFIG_ID") is not None else "Default"
CONFIGURATION = None

app = Flask(__name__)
ds_client = datastore.Client()

@app.route('/') 
def root():
    return redirect('static/index.html')

@app.route('/healthcheck')
def healthcheck():
    return "service up & running"

def init(force=False):
    global CONFIGURATION
    global CONFIG_ID

    if CONFIGURATION is None or force is True:

        configEntity = ds_client.get(ds_client.key('Configuration',CONFIG_ID))
        if configEntity is None:
            
            configEntity = datastore.Entity(key=ds_client.key('Configuration',CONFIG_ID))

            configEntity.update({
                'locationId'    : "Default",
                'headerIcon'    : "assets/logo.png",
                'brandColor'    : "#00FFAA",
                'linkImpressum' : "",
                'linkDPInfo'    : ""      
            })
            ds_client.put(configEntity)

        CONFIGURATION = {x: configEntity[x] for x in configEntity.keys()}

@app.route('/getconfig',methods=["GET"])
def getConfiguration():
    init(force=True)
    return jsonify({
        "success" : True,
        "config"  : CONFIGURATION
    })


@app.route('/qrcode',methods=["GET"])
def qrcode():

    # Get value to encode into QR Code
    
    guestUid = request.args.get('guestUid')
    
    if guestUid is not None:
        qrcode = pyqrcode.create(guestUid)
        buffer = io.BytesIO()
        qrcode.png(buffer, scale=10)
        buffer.seek(0)

        return send_file(buffer,mimetype='image/png')
    
    else:
        abort(400,"missing guestUid")


@app.route('/guest/signup',methods=["POST","PUT"])
def dataload():

    requestData = request.json
    
    # Sign up new guest
    if request.method == "POST":

        guestUid = str(uuid.uuid4()).replace("-","")
        entityKey = ds_client.key('Guest-SelfRegistration',guestUid)
        entity = datastore.Entity(key=entityKey)
        entity.update({
            'name': requestData["guest"]["name"],
            'address': requestData["guest"]["address"],
            'zip': requestData["guest"]["zip"],
            'city': requestData["guest"]["city"],
            'email': requestData["guest"]["email"],
            'phone': requestData["guest"]["phone"],
            'confirmedDPS': requestData["guest"]["confirmedDPS"],
            'createDate': datetime.datetime.now(),
            'changeDate': datetime.datetime.now()            
        })
        ds_client.put(entity)

        #sendMailToGuest()

        return jsonify({
            "success"   : True,
            "guestUid"  : guestUid,
            "qrCodeURL" : "/qrcode?guestUid={}".format(guestUid)
        })

    else:
        abort(400,"unsupported method")


'''
def sendMailToGuest(name, email, uid):
    sender_address = '{}@appspot.gserviceaccount.com'.format(app_identity.get_application_id())
    
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Ihr CheckIn QR Code")

    message.to = "Albert Johnson <Albert.Johnson@example.com>"
    message.body = """Hallo {}:
    Danke, dass Sie uns dabei helfen in der aktuellen Zeit Gäste weiterhin empfangen zu können.
    Wir müssen strikte Regeln befolgen, die Besucher dokumentieren und sicherstellen, dass sich niemals zu viele Gäste bei uns aufhalten.
    Der Checkin über diesen QR-Code vereinfacht die Einhaltung dieser Regeln um einiges und wir danke Ihnen für Ihre zusammenarbeit vorab.

    """
        
    message.send()
'''

@app.errorhandler(400)
def bad_reuqest_error(e):
    return jsonify({
        "success" : False,
        "message": "Bad request: <pre>{}</pre>.".format(e)
    })

@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "success" : False,
        "message": "An internal error occurred: <pre>{}</pre>. See logs for full stacktrace".format(e)
    })

    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)