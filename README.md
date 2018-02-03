> # **Developer Catalog**
> ### **A Udacity Project Submission**
>> **Date: January 2, 2018**  
>> **By: Paul Griz**  

---


## Overview:

1. Working example running online.
    > **Go to [DevShare](https://developer-catalog.herokuapp.com/) for live preview.**
1. To view the website's data in json output:
    1. View the live project's data at: [Link to Json Output](https://developer-catalog.herokuapp.com/catalog/json)
    1. or navigate to ``[localhost]``**/catalog/json** when testing locally.


--- 


## Requirements:

1. **Virtualenv**   
    - [Link to Download](https://virtualenv.pypa.io/en/stable/)
1. **Python 3**  
	- [Link to Download](https://www.python.org/downloads/)


---


## Steps to Locally Run Project:

1. Download this repository.
1. Open command prompt, and Enter: ``virtualenv ENV``
    - Wait for ENV to finish setup.
    - Virtualenv is required for this step. 
    - Link to download Virtualenv in Requirements section above.
1. ``cd`` into ``ENV/Scripts``, and Enter: ``activate``
	- Helpful link if any problems occur: [How to Activate Virtual Environment](https://virtualenv.pypa.io/en/stable/userguide/)
1. Once Activated, ``cd`` back to the main project file where ``app.py`` is located.
1. Once in the directory with ``app.py``
    - Enter command: ``pip install -r requirements.txt``
    - Wait for the required Python Modules to download.
    - Enter command: ``python app.py`` to run the program.
	- Note: This project was develop and tested with Python 3.
1. Open ``localhost:5000`` in a browser to view the site.
1. Initially, no categories or items will be found on the home page.
1. To post content, you must first sign in. 
    - Login botton is located in the top right. 

Removed ENV from Project for Submission Limitations

---