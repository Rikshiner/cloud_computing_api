#Shows what version of python we are using, creates a directory to work from, copy data in current directory to this, installs all requirements, exposes the ports we will use and runs the command python app.py to run my rest api script
FROM python:3.7-alpine
WORKDIR /ghibli
COPY . /api
RUN pip install -U -r requirements.txt
EXPOSE 8080
CMD ["python" , "app.py"]
