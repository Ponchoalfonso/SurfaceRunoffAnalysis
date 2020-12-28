FROM python:3

WORKDIR /usr/src/app
RUN mkdir "out"

# Copy application and requirements
COPY requirements.txt ./
COPY app.py ./
COPY src ./src

# Install GDAL
RUN apt update
RUN apt -y install gdal-bin libgdal-dev
# Install python packages
RUN pip install -r requirements.txt
RUN pip install GDAL==$(gdal-config --version)

CMD python app.py