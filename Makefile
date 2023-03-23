beautify:
	python -m isort strava_reporter
	python -m black --line-length 80 strava_reporter