assembla2jirajson
=================

Crappy script for convert Assembla export to JSON compatible with JIRA importer


How to use
############

Log to your account at https://www.assembla.com
Inside your project page go to "admin" tab.
Choose "Backup and Data Export" and click on "Export my data".
Wait for file and download it.
Extract file content.

Into extracted file, you will find one named "dump.js", it's you SOURCE_FILE.

All other files contained into multiple subfolder match to your Assembla project's attachment.
To be imported, this file need to be put into the root of an unique folder, under Linux (and probably MacOS) this could be made with the following command:

 .. code-block:: bash
    $ find /path_where_you_extract_content -type f -exec mv '{}' ./ \;

Now move this folder with all this file into a location accessible by http from you jira install, for exemple:
 http://mydomain.com/my-content-folder/

Copy "config-sample.json" to "config.json" and edit it to match to your project (user list is the most important part, look into SOURCE_FILE at "user_roles" line to find Assembla user's ID)

You are now ready to run the script

 .. code-block:: bash
    $ python assembla2jirajson.py SOURCE_FILE DESTINATION_FILE URL_OF_YOUR_CONTENT

Finally, you can log into JIRA and go to "Administration > System" .
Click on "IMPORT & EXPORT > External System Import" and choose "Import from JSON".
Select your DESTINATION_FILE and "Begin Import"
