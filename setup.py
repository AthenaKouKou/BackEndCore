from setuptools import setup, find_packages


setup(
    name="BackEndCore",
    version="1.3",
    description="Core code for DataMixMaster's backends.",
    packages=find_packages(),
    url="https://github.com/AthenaKouKou/BackEndCore",
    install_requires=[
        'certifi==2024.7.4',
        'dnspython==2.6.1',
        'numpy',
        'pymongo==4.8.0',
        'python-dateutil',
        'pytz',
        'validators==0.33.0',
    ],
)
