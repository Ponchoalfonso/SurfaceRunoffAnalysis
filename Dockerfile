FROM python:3

WORKDIR /usr/src/app

RUN git clone https://github.com/Ponchoalfonso/SurfaceRunoffAnalysis.git .

# Install GDAL
RUN apt update
RUN apt -y install gdal-bin libgdal-dev
# Install pipenv
RUN pip install pipenv
RUN pipenv --python $(which python)
# Install python packages
RUN pipenv install
RUN pip install GDAL==$(gdal-config --version)

CMD python app.py