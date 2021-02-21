FROM python:3.7
RUN mkdir /api
WORKDIR /api
COPY requirements.txt /api/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
COPY . .
