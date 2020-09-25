# bike-buddy

This is a Flask-based API project aimed at aggregating the details of the various bike sharing schemes in Ireland.  

The idea is that the application will periodically retrieve data from the APIs of each individual bike share operators, and will write this information to a database.  The BikeBuddy application will then expose an API allowing the user to query availability of bikes belonging to any of the operators.

At present only the first step is in place, where the data is retrieved from the operator's API.  It is currently just returned as-is to the caller. The database layer is not yet implemented.

Aside from implementing the database layer, the intention is to add support for the Bleeper Bikes scheme, as they have a publicly available API.
