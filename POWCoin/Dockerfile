FROM python:3.7.0
ADD requirements.txt ./
RUN pip install -r requirements.txt
ADD utils.py ./
ADD identities.py ./
ADD models.py ./
ADD powcoin.py ./

CMD ["python", "-u", "powcoin.py", "serve"]
