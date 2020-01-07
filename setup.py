from setuptools import find_packages, setup

setup(
    name="jobbergate",
    version="1.0.0",
    author="Jimmy Hedman",
    author_email="jimmy.hedman@cygni.se",
    description="Questionnaire application that populates Jinja2 templates with given answers.",
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
        "Flask-WTF==0.14.2",
        "PyYAML==5.1.2",
        "inquirer==2.6.3",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
