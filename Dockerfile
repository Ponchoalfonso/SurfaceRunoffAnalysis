FROM python:3

WORKDIR /usr/src/app

COPY . ./

RUN apt update
RUN apt install libgdal libgdal-dev
RUN pip install --user pipenv
RUN pipenv install
RUN pip install GDAL==$(gdal-config --version)

CMD python app.py