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

@app.route('/init',methods=["POST"])
def initService():
    init(force=True)

    return jsonify({
        "success" : True,
        "config"  : CONFIGURATION
    })


def init(force=False):
    global CONFIGURATION
    global CONFIG_ID

    if CONFIGURATION is None or force is True:

        configEntity = ds_client.get(ds_client.key('Configuration',CONFIG_ID))
        if configEntity is None:
            
            configEntity = datastore.Entity(key=ds_client.key('Configuration',CONFIG_ID))

            configEntity.update({
                'locationId'    : "Default",
                'headerIcon'    : "/assets/logo.png",
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


@app.route('/checkin',methods=["POST"])
def checkin():
    # Init and read configuration
    init()
    locationId = CONFIGURATION["locationId"]

    # Get value to encode into QR Code
    requestData = request.json
    guestUid = requestData["guestUid"]
    
    if guestUid is not None:

        guestEntity = ds_client.get(ds_client.key('Guest-SelfRegistration',guestUid))

        if guestEntity is not None:
            guestStatusUid = guestUid + "-" + locationId
            guestStatusEntity = ds_client.get(ds_client.key('Guest-Status',guestStatusUid))

            if guestStatusEntity is None: 
                guestStatusEntity = datastore.Entity(key=ds_client.key('Guest-Status',guestStatusUid))
                guestStatusEntity.update({
                    'guestUid'   : guestUid,
                    'locationId' : locationId,
                    'checkInDate': datetime.datetime.now()       
                })
                ds_client.put(guestStatusEntity)

                checkInTime = datetime.datetime.now()
                visitUid = guestUid + "-" + str(checkInTime.timestamp())
                visitEntity = datastore.Entity(key=ds_client.key('Guest-Visits',visitUid))
                visitEntity.update({
                    'guestUid'    : guestUid,
                    'locationId'  : locationId,
                    'checkInDate' : checkInTime,
                    'checkOutDate': None           
                })
                ds_client.put(visitEntity)
                
                return jsonify({
                    "success"     : True,
                    "message"     : "Guest successfully checked in",
                    "checkInDate" : checkInTime,
                    "visitUid"    : visitUid
                })

            else: 
                return jsonify({
                    "success"   : False,
                    "message"   : "Guest already checking in at this location"
                })
        else: 
            return jsonify({
                "success"   : False,
                "message"   : "Guest does not exist"
            })
    else:
        abort(400,"missing guestUid")


@app.route('/checkout',methods=["POST"])
def checkout():

    # Init and read configuration
    init()
    locationId = CONFIGURATION["locationId"]

     # Get value to encode into QR Code
    requestData = request.json
    guestUid = requestData["guestUid"]
    
    if guestUid is not None:

        guestEntity = ds_client.get(ds_client.key('Guest-SelfRegistration',guestUid))

        if guestEntity is not None:

            guestStatusUid = guestUid + "-" + locationId
            guestStatusEntity = ds_client.get(ds_client.key('Guest-Status',guestStatusUid))
            
            if guestStatusEntity is not None:
                ds_client.delete(ds_client.key('Guest-Status',guestStatusUid))

                checkOutTime = datetime.datetime.now()
                query = ds_client.query(kind='Guest-Visits')
                query.add_filter('guestUid', '=', guestUid)
                query.add_filter('locationId', '=', locationId)
                query.add_filter('checkOutDate', '=', None)
                result = query.fetch()

                for visitEntity in list(result):
                    visitEntity.update({
                        'checkOutDate': checkOutTime           
                    })
                    ds_client.put(visitEntity)

                return jsonify({
                    "success"      : True,
                    "message"      : "Guest successfully checked out",
                    "checkOutDate" : checkOutTime
                })

            else: 
                return jsonify({
                    "success"   : False,
                    "message"   : "Guest is not checked in"
                })

        else: 
            return jsonify({
                "success"   : False,
                "message"   : "Guest does not exist"
            })

    else:
        abort(400,"unsupported method")


@app.errorhandler(400)
def bad_reuqest_error(e):
    return jsonify({
        "success" : False,
        "message" : e
    })

@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "success" : False,
        "message" : e
    })

    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)