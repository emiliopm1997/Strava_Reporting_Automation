beautify:
	python -m isort strava_reporter
	python -m black --line-length 80 strava_reporter

rebuild_package:
	rm -rf dist
	rm -rf strava_reporter.egg-info
	python ./setup.py sdist --formats=gztar

run:
	pip install .
	python -m strava_reporter --test true