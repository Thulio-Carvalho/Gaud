FROM python:2

WORKDIR /usr/src/app/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR src/

CMD [ "python", "./main.py" ]
