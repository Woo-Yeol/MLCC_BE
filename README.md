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
    $ sh migrate.sh
```

#### Run Server
```
    $ python manage.py runserver
```

### After Pull

#### Reset Migration
- Error 발생시
```
    $ rm ./db.sqlite3
    $ sh reset_migration.sh
    $ sh migrate.sh
```

#### 종속성 업데이트
```
    $ pip install -r requirements.txt
```