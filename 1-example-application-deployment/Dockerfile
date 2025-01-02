FROM python

RUN mkdir /workdir
WORKDIR /workdir
ADD . /workdir/
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "app/apigateway.py"]