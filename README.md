# MONDE web-crawling server
web-crawling main server
<br></br>
## How to install 
```
$ pip install -r requirements.txt
or
$ pipenv install
``` 

## redis install
```
$ wget http://download.redis.io/redis-stable.tar.gz
$ tar xvzf redis-stable.tar.gz
$ cd redis-stable
$ make
```
## 1.redis 
```
$ redis-server # redis 실행
$ redis-cli ping # 정상 설치되었는지 확인
> PONG
```

## 2.celery 
```
$ celery -A   [파일이름]   worker -l info
```

## 3.How to run 
```
$ python task.py 
```

