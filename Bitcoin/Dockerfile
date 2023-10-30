FROM python:3.7.0
ADD requirements.txt ./
RUN pip install -r requirements.txt
ADD utils.py ./
ADD models.py ./
ADD butcoin.py ./

CMD ["python", "-u", "butcoin.py", "serve"]
