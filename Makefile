beautify:
	python -m isort strava_reporter
	python -m flake8

rebuild_package:
	rm -rf dist
	rm -rf strava_reporter.egg-info
	python ./setup.py sdist --formats=gztar

run:
	pip install .
	python -m strava_reporter --test true --date "2023-04-19"