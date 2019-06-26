# Item Catalog

Item Catalog is an item listing program with back end user authorization and authentication.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


### Installing

To get the app running on your local machine just run the following commands in your terminal:

```
git clone https://github.com/victoray/ItemCatalog.git item_catalog
cd item_catalog

# create a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install r- requirements.txt
FLASK_APP=app.py flask run
```

Open a web browser, and navigate to the app at http://localhost:5000/.



## App Live Demo

[Heroku](https://itemcatalogv3.herokuapp.com/) with Facbook and Google Sign in  
[Azure](http://itemcatalogv2.azurewebsites.net/) With Google Sign in  
[Ubuntu Server](http://40.114.111.144/) Azure VM running APACHE with basic oauth

## JSON Endpoints

link/<category_id>/<item_id>/JSON  
link/<category_id>/JSON

Sample

https://itemcatalogv3.herokuapp.com/1/2/JSON  
https://itemcatalogv3.herokuapp.com/1/JSON


## Deployment

To deploy on Azure:

[Python app in Azure](https://docs.microsoft.com/en-us/azure/app-service/containers/quickstart-python)  

To Deploy on Heroku:

[Getting Started on Heroku with Python](https://devcenter.heroku.com/articles/getting-started-with-python)    
Add the following code to the Procfile

```
web: gunicorn app:app --preload
```



## Built With

* Python3
* [Flask](https://www.palletsprojects.com/p/flask/) - Flask is a lightweight WSGI web application framework.  
* [Apache](https://www.apache.org/) -  Apache, is free and open-source cross-platform web server software.  
* [mod_wsgi](https://modwsgi.readthedocs.io/en/develop/) - The mod_wsgi package implements a simple to use Apache module which can host any Python web application which supports the Python WSGI specification.  
* [SQLite](https://sqlite.org) - SQLite is a C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine.  
* [SQLAlchemy](https://www.sqlalchemy.org/) - SQLAlchemy is an open-source SQL toolkit and object-relational mapper for the Python


## Authors

* **Victor A.** 

## Acknowledgments

* [Drift](http://drift.g-axon.work) - Template Design
