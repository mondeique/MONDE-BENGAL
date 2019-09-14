# MONDE web-crawling server
web-crawling main server
<br></br>
## How to install 
```
$ pip install -r requirements.txt
or
$ pipenv install
``` 
- mysqlclient 가 설치되지 않는 error (OSX Mojave)
```
$ brew reinstall openssl
$ LDFLAGS=-L/usr/local/opt/openssl/lib pip install mysqlclient
```
## redis install (ubuntu)
```
$ wget http://download.redis.io/redis-stable.tar.gz
$ tar xvzf redis-stable.tar.gz
$ cd redis-stable
$ make
```
## redis install (macOS)
```
$ brew install redis
$ brew services start redis
$ brew services stop redis
$ brew services restart redis
```
## 1.redis 
```
$ redis-server # redis 실행
$ redis-cli ping # 정상 설치되었는지 확인
> PONG
$ redis-cli shutdown # redis server 중지
```

## 2.celery 
```
$ celery -A   [파일이름]   worker -l info
```

## 3.How to run 
```
$ python task.py 
```



