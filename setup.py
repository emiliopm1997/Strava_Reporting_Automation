from setuptools import find_packages, setup

VERSION = "1.0.0"
DESCRIPTION = "Extract a weekly report of the athletes within the club."
LONG_DESCRIPTION = (
    "Extract a weekly report of the athletes that are members of the club, "
    + "and classify them between those who completed the weekly challenge and "
    + "those who didn't."
)

# Setting up
setup(
    name="strava_reporter",
    version=VERSION,
    author="Emilio Padron",
    author_email="emiliopm1997@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["numpy", "pandas", "stravalib"],
    keywords=["python", "strava", "reporting"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
    ],
)
