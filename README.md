# Place Checking for Corona Times
Place Checkin for Corona Times. Helps restaurants to track visitor amount and their contact data.
Designed to run on Google Cloud Platform.

# Preparation
Prepare your Google Cloud Platform project. Activate Google App Engine and activate Data Store in the native Data Store mode.
Visit the files app.yaml in both folders "app-4-restaraunt" and "app-4-guest" and personalize the PLACE_CHECKIN_CONFIG_ID. 

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
Open the Configuration entity in Data Store and configure the requested stuff: (https://pantheon.corp.google.com/datastore/entities;kind=Configuration)