deps:
	pip3 install -r requirements.txt
	pip3 install -r requirements.dev.txt

test:
	nose2 -v

black:
	black lifeguard
	black tests

settings:
	support/display_settings

clean:
	find . -iname "*.pyc" | xargs rm
