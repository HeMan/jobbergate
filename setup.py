from setuptools import find_packages, setup

setup(
    name="jobbergate",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Flask",
        "Flask-Bcrypt",
        "Flask-Bootstrap",
        "Flask-DebugToolbar",
        "Flask-Login",
        "Flask-Migrate",
        "Flask-SQLAlchemy",
        "Flask-WTF",
        "inquirer",
        "PyYAML",
    ],
)
