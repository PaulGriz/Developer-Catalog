Developer-Catalog
=============

## File Structure

     Docs
     |----> All Documentation

     models
     |----> Data models   
          - category.py
          - items.py
          - user.py

     resources
     |----> Api Endpoint Resources
          - category.py
          - items.py
          - user.py

     Templates
     |----> All HTML, CSS, and JS Files
          - Not Developed Yet

     ### Main Project Files

     app.py
     db.py
     security.py
     run.py

     ### Heroku Files

     Procfile
     requirements.txt
     runtime.txt
     uwsgi.ini

     ### Github Files

     README.md
     .gitignore


## TODO List

     1.) Need to add category items class after:

          A.) Class Category and CategoryList is finished in resources/category.py
          B.) Class CategoryModel is finished in models/category.py

     2.) Set every category with matching category items

          A.) Category items will be text descriptions at first

     3.) Add Google and Github OAth into the site and possibly remove
          the current authentication for security

     4.) Build a working website for users to interact with: CRUD

     5.) Allow deeper features in the category items

          A.) Pictures
          B.) Videos
          C.) Codepen Plugin
          D.) Other useful features for users

     6.) Add JavaScript to the website for an added fluid feel

## Requirements:

     1.) Virtualenv
          [Link](https://virtualenv.pypa.io/en/stable/)

     2.) Python 3

     3.) Flask

     4.) Flask RESTful

     5.) Flask JWT

     6.) Flask-SQLAlchemy
