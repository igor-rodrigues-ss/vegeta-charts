from setuptools import setup, find_packages


setup(
    name="foo",
    version="1.0",
    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'vegeta-charts = vegeta_charts.main:main',                  
        ],              
    },
)