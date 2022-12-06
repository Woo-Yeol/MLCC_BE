# 💻MLCC_BE

2021-03 ~ ing

### MLCC 적층 얼라인먼트 시스템

MLCC(Multilayer Ceramic Capacitors)란 0.3mm의 얇은 두께의 내부에 최대한 얇게 많은 층을 쌓아 많은 전기를 축적하는 부품입니다.   
삼성기전의 반도체 품질검사 공정에서 받아온 MLCC 사진을 분석 모델을 통해 품질(마진률)을 비롯한 평가 데이터를 DB에 적재하고   
이를 공정 내 전문가들이 품질 분석 및 모델 성능 향상에 기여할 수 있도록 웹 형태로 시각화한 모델 서빙 | 모니터링 플랫폼입니다.   
삼성기전 공정 내에서 웹을 통해 바로 공정 모니터링 및 어노테이션, 모델 자가학습을 진행할 수 있도록 기여했습니다.



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
