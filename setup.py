from setuptools import find_packages, setup

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.rst")) as f:
    long_description = f.read()

setup(
    name="jobbergate",
    version="1.3.0",
    author="Jimmy Hedman",
    author_email="jimmy.hedman@cygni.se",
    description="Questionnaire application that populates Jinja2 templates with given answers.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    scripts=["wrapper.sh"],
    url="https://github.com/HeMan/jobbergate",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Flask==1.1.1",
        "Flask-Bcrypt==0.7.1",
        "Flask-Bootstrap==3.3.7.1",
        "Flask-DebugToolbar==0.10.1",
        "Flask-Login==0.4.1",
        "Flask-Migrate==2.5.2",
        "Flask-SQLAlchemy==2.4.1",
        "Flask-WTF==0.14.3",
        "PyYAML==5.1.2",
        "inquirer==2.6.3",
        "flask-ldap3-login==0.9.16",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
