# MLCC_BE
MLCC 적층 얼라인먼트 검사 시스템

### Install

#### Git Clone
```
    $ git clone https://github.com/Woo-Yeol/MLCC_BE.git
```

#### Create Venv
```
    $ python -m venv venv
```

#### Activate Venv
```
    Mac
    $ source venv/bin/activate
    
    Window
    $ source venv/Scripts/activate
```

#### Requirements Install
```
    $ pip install -r requirements.txt 
```

#### Settings.py -> secrets.json 생성
```
    {
    "SECRET_KEY": "*******************"
    }
```

#### Migration
```
    $ python manage.py makemigrations
    $ python manage.py migrate
```

#### Run Server
```
    $ python manage.py runserver
```