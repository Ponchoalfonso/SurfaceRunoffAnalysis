FROM python:3

WORKDIR /usr/src/app

RUN sudo apt update
RUN sudo apt install libgdal-dev
RUN pip install --user pipenv
RUN pivenv install
RUN pip install GDAL==$(gdal-config --version)

CMD python app.py