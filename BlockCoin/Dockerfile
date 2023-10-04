FROM python
ADD requirements.txt ./
RUN pip install -r requirements.txt
ADD blockcoin.py ./
ADD utils.py ./
ADD identities.py ./
ADD models.py ./

CMD ["python", "blockcoin.py", "serve"]
