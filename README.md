# bike-buddy

This is a Flask-based API project aimed at aggregating the details of the various bike sharing schemes in Ireland, to allow them to be exposed through one single common interface. 

The idea is that the application will periodically retrieve data from the APIs of each individual bike share operators, and will write this information to a database.  For most bike share schemes this data will relate to bike stations, such as the number of available bikes and number of available free spaces.  For dockless schemes this data will relate to individual bikes.

The BikeBuddy application will then expose a public-facing API allowing the user to query availability of bikes belonging to any of the operators.

The application uses MongoDB for data storage.  The idea is to also leverage its support for geospatial operations.  At present the application converts the location details for each station or bike into a GeoJSON object before storing it in the database.  This should in future facilitate features such as finding the nearest bike or station.