### MYSQL Settings
DB name: mydb <br>
username: root <br>
password: 96173880

<hr/>

### How to start the website
1. Create a MYSQL database using the above details
2. Clone repository onto your preferred ide
3. Run "pip install -r requirements.txt" in the command line
4. Run main.py
5. Let the application create the database (if not created yet)
6. Import the information for the property table using clean_properties.csv
7. Make sure that the property table has these information first. If not, continuously refresh the schemas until the actual property table appears <br/>
![property_table_columns_image](property_table_columns.png)
8. Import the information for the property_images table using property_images_db.csv 
9. Make sure that the property_images table has these information first. If not, continuously refresh the schemas until the actual property_images table appears <br/>
![property_images_columns_image](property_images_columns.png)
10. Website is now working
11. NOTE: Website may stop working if the secret_key email/password combination has been changed
12. You are free to change it to your own email/password

<hr/>

### Default Accounts
1. Landlord <br>
email: johndoe@landlord.com <br>
password: 123456789aA$ <br>
{Account is the owner of all default properties}

2. Admin <br>
email: admin@admin.com <br>
password: 123456789aA$ 

3. Tenant <br>
email: jackdoe@tenant.com<br>
password: 123456789aA$

<hr/>

### Things to take note when editing/deleting default properties
1. **ALL** default properties are using the same placeholder image and approval documents
2. To prevent default properties from having broken images and approval documents, **DO NOT** edit/delete them
3. **ONLY** edit/delete properties that you have created



