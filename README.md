# 💻MLCC_BE

2021-03 ~ ing

### MLCC 적층 얼라인먼트 시스템

삼성기전의 반도체 품질검사 공정에서 사용할 목적으로 만든 모델 서빙 | 모니터링 서비스입니다.
반도체의 품질(마진률)을 비롯한 평가 데이터 모델 산출물을 공정 내 전문가들이 쉽게 확인해 
품질 분석 및 모델 성능 향상에 기여할 수 있도록 웹 형태로 제작했습니다.

- Celery 기반 모델 서빙
- 분석 데이터 모니터링을 위한 API 구현


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
