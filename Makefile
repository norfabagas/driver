freeze:
	@pip freeze | grep -v "pkg-resources" > requirements.txt
serve:
	@export FLASK_APP=wsgi.py FLASK_ENV=development && flask run