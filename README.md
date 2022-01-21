## Requirements
- Python (3.5, 3.6, 3.7, 3.8)
- Mysql (optional)
## Installation 
- Create  virtual environment(optional)
- Install the dependencies and devDependencies  
```sh
$ pip install -r requirements.txt
```

- Copy  sweet/settings_sample.py to  sweet/settings.py
```sh
$ cp  sweet/settings_sample.py sweet/settings.py
```
- Set DataBase Connection in sweet/settings.py
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test',
        'USER': 'test',
        'PASSWORD': 'test@test',
        'HOST': '127.0.0.1',  # Or an IP Address that your DB is hosted on
        'PORT': '3306',
        'OPTIONS': {
            # Tell MySQLdb to connect with 'utf8mb4' character set
            'charset': 'utf8mb4',
        },
    }
}
```
- Create Table In DataBase   
```sh
$ python manage.py migrate
```
- Create Super User
```sh
$ python manage.py createsuperuser
```
- Run Server and admin route  http://127.0.0.1:8000/admin
```sh
$ python manage.py runserver
```

## Standard
####Naming in Projects
- application  (Plural => e.x: packages,users,...)
- API VIew Method (request method => e.x: get,post,put,delete,...)
- Class  (PascalCase => e.x User)
- method (camelCase => e.x: userLoginCount )
- property or other variables (snake_case => e.x: user_login_count )
 


License
----
Pec

- If You want more info like rest api request file Such as Postman Contact Us
baharimahdi93@gmail.com

