# Dockerfile 

FROM python:3.7.4
MAINTAINER eren@mondeique.com

ENV PYTHONUNBUFFERED 0

# 우분투 환경 업데이트 및 기본 패키지 설치
RUN apt-get -y update
RUN apt-get upgrade -y
RUN apt-get -y dist-upgrade
RUN apt-get install -y python3-pip git vim 

RUN pip3 install --upgrade pip
RUN pip install --upgrade pip

# pyenv setting 
RUN apt-get install -y make build-essential \
curl \
libreadline-gplv2-dev \
libncursesw5-dev \
libssl-dev \
libsqlite3-dev \
tk-dev \
libgdbm-dev \
libc6-dev \
libbz2-dev \
zlib1g-dev \
openssl \
libffi-dev \
python3-dev \
python3-setuptools \
wget
RUN curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
ENV PATH /root/.pyenv/bin:$PATH
RUN pyenv install 3.7.4

# zsh 
#RUN apt-get install -y zsh
#RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true
#RUN chsh -s /usr/bin/zsh

# pyenv settings
RUN echo 'export PATH="/root/.pyenv/bin:$PATH"' >> ~/.bashrc
RUN echo 'eval "$(pyenv init -)"' >> ~/.bashrc
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
RUN ["/bin/bash", "-c", "source ~/.bashrc"]

# pyenv virtualenv
RUN pyenv virtualenv 3.7.4 mondeique-crawling
CMD ["pyenv", "activate", "mondeique-crawling"]

# uWGSI install
#RUN /root/.pyenv/versions/app/bin/pip install uwsgi

# Nginx install
#RUN apt-get -y install nginx

# supervisord install
#RUN apt-get -y install supervisor

# make folder
COPY . /mondeique_crawler
WORKDIR /mondeique_crawler

# pip upgrade & requirements install
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# mysqlclient install
RUN apt-get install -y mariadb-client
RUN apt-get install -y python3-dev default-libmysqlclient-dev gcc
RUN pip install mysqlclient==1.4.4

# 원하는 포트를 열어준다. runserver가 8000번을 default로 쓰기때문에 8000번을 열어줌
EXPOSE 8000

# manage.py가 있는 directory로 이동한 후에 runesrver 실행
# manage.py가 dockerfile과 같은 dir에 있으면 따로 WORKDIR를 지정할 필요는 없다.
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
