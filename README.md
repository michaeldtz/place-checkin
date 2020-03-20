# Place Checking for Corona Times
The app provides a place checkin that can be used by restaraunts during the time of Corona restrictions. The app provides a way to checkin and checkout visitors and therefore have a view on the current visitors but also be able to provide a documentation about the names and contact data of visitors on a given day. It consits of two webapps
- The restaurant app that provides a guest overview and allows to checkin / checkout guests via their personal qr code
- The guest app that allows guests to enter their contact data and receive a barcode that can be used to checkin and checkout

The app is designed to run on Google Cloud Platform. Specifically on Google App Engine (Standard, Python) and uses Data Store.

# Preparation
You can start to prepare you GCP Project by activation Google App Engine and  Data Store in the native Data Store mode.
Then visit the files app.yaml in both folders "app-4-restaraunt" and "app-4-guest" and personalize the PLACE_CHECKIN_CONFIG_ID. 

# Deployment
Deploy the restaurant app
```
cd app-4-restaraunt
gcloud app deploy
```

Deploy the guest app
```
cd app-4-guest
gcloud app deploy
```


# Configuration
The restaurant add has an endpoint '/init' that can be called to force the initialization of the config. Afterwards your can open the 
Open the Configuration entity in Data Store and configure the requested stuff: [Google Cloud Console -> Data Store](https://console.cloud.google.com/datastore/entities;kind=Configuration)