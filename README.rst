This is the main edX platform which consists of LMS and Studio.
_______________________________________________________________

|

Installation
============

1. Install Open edX Cypress From this link given below:
#######################################################

+----------------------------------------------------------------------------------------------------+
|https://openedx.atlassian.net/wiki/display/OpenOPS/Native+Open+edX+Ubuntu+12.04+64+bit+Installation |
+----------------------------------------------------------------------------------------------------+

|

2. Cypress - IITBombayX
#######################

* **Run commands below to clone edx-platform from github**
+----------------------------------------------------------------------------------------------------+
|cd /edx/app/edxapp                                                                                  |
|                                                                                                    |
|sudo mv  edx-platform edx-platform-old                                                              |
|                                                                                                    |
|sudo -H -S -u edxapp /bin/sh -c "git clone https://github.com/openiitbombayx/edx-platform.git"      |
+----------------------------------------------------------------------------------------------------+

|

* **Run command below to make directory and clone theme from github**
+-----------------------------------------------------------------------------------------------------+
|cd /edx/app/edxapp                                                                                   |
|                                                                                                     |
|sudo -H -S -u edxapp /bin/sh -c "mkdir themes"                                                       |
|                                                                                                     |
|cd /edx/app/edxapp/themes                                                                            |
|                                                                                                     |
|sudo -H -S -u edxapp /bin/sh -c "git clone https://github.com/openiitbombayx/iitbxcypress-theme.git" |      
+-----------------------------------------------------------------------------------------------------+

|

* **Edit lms.env.json, cms.env.json both and change values below:**
+-----------------------------------------------+
|sudo vi /edx/app/edxapp/lms.env.json           |
+-----------------------------------------------+
"USE_CUSTOM_THEME": true

"THEME_NAME": "iitbxcypress-theme",

"PLATFORM_NAME": "IITBombayX",

|

+-----------------------------------------------+
|sudo vi /edx/app/edxapp/cms.env.json           |
+-----------------------------------------------+
"USE_CUSTOM_THEME": true

"THEME_NAME": "iitbxcypress-theme",

"PLATFORM_NAME": "IITBombayX",

|

|

* **Compile assets manually**

+-------------------------------------------------------------------------------------------------------------------------------------------+
| cd /edx/app/edxapp/edx-platform                                                                                                           |
|                                                                                                                                           |
| sudo -H -u edxapp bash                                                                                                                    |
|                                                                                                                                           |
| source /edx/app/edxapp/edxapp_env                                                                                                         |
|                                                                                                                                           |
| cd /edx/app/edxapp/edx-platform                                                                                                           |
|                                                                                                                                           |
| gem install bundle                                                                                                                        |
|                                                                                                                                           |
| bundle install --binstubs                                                                                                                 |
|                                                                                                                                           |
| npm install                                                                                                                               |
|                                                                                                                                           |
| pip install -i https://pypi.python.org/simple --exists-action w --use-mirrors -r /edx/app/edxapp/edx-platform/requirements/edx/pre.txt    |
|                                                                                                                                           |           
| pip install -i https://pypi.python.org/simple --exists-action w --use-mirrors -r /edx/app/edxapp/edx-platform/requirements/edx/base.txt   |     
|                                                                                                                                           | 
| pip install -i https://pypi.python.org/simple --exists-action w --use-mirrors -r /edx/app/edxapp/edx-platform/requirements/edx/local.txt  |     
|                                                                                                                                           | 
| pip install -i https://pypi.python.org/simple --exists-action w --use-mirrors -r /edx/app/edxapp/edx-platform/requirements/edx/github.txt |    
|                                                                                                                                           | 
| pip install -i https://pypi.python.org/simple --exists-action w --use-mirrors -r /edx/app/edxapp/edx-platform/requirements/edx/post.txt   |   
|                                                                                                                                           | 
| pip install -i https://pypi.python.org/simple --exists-action w --use-mirrors -r /edx/app/edxapp/edx-platform/requirements/edx/paver.txt  | 
|                                                                                                                                           | 
|* **First time paver LMS and CMS**                                                                                                         |
|                                                                                                                                           | 
| paver update_assets lms --settings=aws                                                                                                    |     
|                                                                                                                                           | 
| paver update_assets cms --settings=aws                                                                                                    |    
+-------------------------------------------------------------------------------------------------------------------------------------------+



* **Add the following variables in /edx/app/edxapp/lms.env.json file.**
**If it is already present, just change the values. OR the lines should be added before: "ANALYTICS_SERVER_URL": "",** 

+-------------------------------------------------------+
|"ADVANCED_SECURITY_CONFIG": {                          |
|				                        |
|"MIN_DIFFERENT_STAFF_PASSWORDS_BEFORE_REUSE":1,        |
|							|
|"MIN_DIFFERENT_STUDENT_PASSWORDS_BEFORE_REUSE":1       |
|							|
|},                                                     |
|							|
|"ADVANCED_SECURITY": true,                             |
+-------------------------------------------------------+

|

* **Inside the "FEATURES" dictionary of lms.env.json file, there is an entry called ENFORCE_PASSWORD_POLICY. Change it as follows if not add this:**
+---------------------------------+
|"ENFORCE_PASSWORD_POLICY": true, |
+---------------------------------+

|

* **There is a dictionary called "REGISTRATION_EXTRA_FIELDS" in /edx/app/edxapp/lms.env.json file. Delete the entire dictionary.**
**eg. if the dictionary is as follows:**


+-----------------------------------------------+
|REGISTRATION_EXTRA_FIELDS = {			|
|						|
|'state':'required',				|
|						|
|'city': 'required',				|
|						|
|'pincode': 'required',				|
|						|
|'aadhar_id':'optional',			|
|						|
|'level_of_education': 'optional',		|
|						|
|'gender': 'optional',				|
|						|
|'year_of_birth': 'optional',			|
|						|
|'mailing_address': 'optional',			|
|						|
|'goals': 'optional',				|
|						|
|'honor_code': 'required',			|
|						|
|'terms_of_service': 'hidden',			|
|						|
|'country': 'hidden',				|
|						|
|} 						|
+-----------------------------------------------+

|
**delete the entire text above. (If not deleted this State and City will not comes While REGITER User Account)**

|

* **Edit cms.env.json**
+-----------------------------------------+
|sudo vi /edx/app/edxapp/cms.env.json     |
+-----------------------------------------+

"STUDIO_NAME": "IITBombayX Studio",

|

* **Restart LMS and CMS**

+-------------------------------------------------------------+
|sudo /edx/bin/supervisorctl restart edxapp:                  |
+-------------------------------------------------------------+

|

* **Use this step if not migrated earlier**

+---------------------------------------------------------------------------------------------------+
|cd /edx/app/edxapp/edx-platform                                                                    |
|                                                                                                   |
|sudo -u www-data /edx/bin/python.edxapp ./manage.py lms migrate student --settings aws             |
|                                                                                                   |
|sudo -u www-data /edx/bin/python.edxapp ./manage.py lms migrate courseware --settings aws          |
+---------------------------------------------------------------------------------------------------+
