FROM jupyter/base-notebook:1fbaef522f17

COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT ["tini", "--", "python", "app.py"]