# MONDE web-crawling server
__web-crawling server
<br></br>
## How to install 
```
$ pip install -r requirements.txt
or
$ pipenv install
``` 
- mysqlclient의 경우 따로 install 해야함 

(OSX Mojave)
```
$ brew reinstall openssl
$ LDFLAGS=-L/usr/local/opt/openssl/lib pip install mysqlclient
```
(Ubuntu 18.04 LTS)
```
$ sudo apt-get install mysql-client
$ apt-get install python3-dev libmysqlclient-dev gcc
$ pip install mysqlclient
```
### redis install (ubuntu)
```
$ wget http://download.redis.io/redis-stable.tar.gz
$ tar xvzf redis-stable.tar.gz
$ cd redis-stable
$ make
```
### redis install (macOS)
```
$ brew install redis
$ brew services start redis
$ brew services stop redis
$ brew services restart redis
```
## How to run for bag crawling(DEPRECATED)
### 1. redis
```
$ redis-server # redis 실행
$ redis-cli ping # 정상 설치되었는지 확인
> PONG
$ redis-cli shutdown # redis server 중지
```

### 2.celery 
```
$ celery -A   [파일이름]   worker -l info
```

### 3. run main python file
```
$ python task.py 
```




