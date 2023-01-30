FROM python:3.7 # 자신이 사용하고 있는 파이썬 버전

RUN mkdir /echo
COTY flask_app.py /echo

CMD ["python", "/echo/flask_app.py"]