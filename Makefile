deps:
	pip3 install -r requirements.txt
	pip3 install -r requirements.dev.txt

test:
	nose2 -v --with-coverage --coverage-report html --coverage-report term --coverage-report xml

black:
	black lifeguard
	black tests

black-ci:
	black --check --diff lifeguard
	black --check --diff tests

clean:
	find . -iname "*.pyc" | xargs rm
