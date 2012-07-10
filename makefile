update-env:
	pip install -r requirements.txt

test:
	python rules_engine/manage.py test
