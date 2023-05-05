beautify:
	python -m isort strava_reporter
	python -m flake8

rebuild_package:
	rm -rf dist
	rm -rf strava_reporter.egg-info
	python ./setup.py sdist --formats=gztar

run:
	pip install .
	python -m strava_reporter --n_skip 1 --stop_after 7 --date "2023-05-04"