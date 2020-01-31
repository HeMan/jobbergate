Configuration
=============

Configuration could be done in ``config.py`` as objects and selected via
environment variable ``APP_SETTINGS``. This could be done to have differente
setting for developement, test, production etc. This file is part of the
installation and should seldom be changed.

Configuration could also be done in ``jobbergate.yaml``, which overrides
configuration done in ``config.py``. It only overrides the same variables, so
if you have different variables in the files they are all going to be set.

The environment variable ``JOBBERGATE_PATH`` points to the directory where
``jobbergate.yaml`` resides, and could therefor point to a project or user
configuration.


Flask configuration
-------------------
To start flask in debug mode, set ``FLASK_DEBUG`` to ``true``.

LDAP
^^^^

Jobbergate uses ``flask-ldap3-login`` to be able to authenticate via LDAP and
Active Directory. Configuration options is described at `flask-ldap3-login`_.

The configuration could reside in both ``config.py`` and in
``jobbergate.yaml``.

A configuration for Active Directory could look like this:

.. code-block:: python

   class ProductionConfig(BaseConfig):
       """Production configuration."""

       BCRYPT_LOG_ROUNDS = 13
       SQLALCHEMY_DATABASE_URI = os.environ.get(
           "DATABASE_URL", "sqlite:///{0}".format(os.path.join(basedir, "prod.db"))
       )
       WTF_CSRF_ENABLED = True
       LDAP_SEARCH_FOR_GROUPS = False
       LDAP_USE_SSL = True
       LDAP_PORT = 636
       LDAP_HOST = "ad.server.examlpe.com"
       LDAP_USER_DN = "OU=Users"
       LDAP_BASE_DN = "dc=ad,dc=server,dc=example,dc=com"
       LDAP_USER_LOGIN_ATTR = "cn"
       LDAP_USER_RDN_ATTR = "cn"

.. _flask-ldap3-login: https://flask-ldap3-login.readthedocs.io/en/latest/configuration.html

Jobbergate configuration
------------------------
``jobbergate.yaml`` has one section called ``apps:`` that has ``path:``
pointing to the directory containing all the applications.

``jobbergate.yaml`` is also passed in the data structure flowing through the
application as ``data["jobbergateconfig"]``.

Application specific
--------------------
You could have an application specific configuration file called
``config.yaml`` that is added to the data structure flowing through the
application.

