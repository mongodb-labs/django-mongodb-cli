Django allauth
==============

.. _django-allauth-results:

Results
-------

Via ``dm repo test django-filter``

+---------------------------+------------+-----------+-----------+----------------+--------------+----------------------------+------------------+
|  **PERCENTAGE PASSED**    | **TOTAL**  |  **PASS** | **FAIL**  |  **SKIPPED**   |   **ERROR**  | **EXPECTED FAILURES**      |  **WARNING**     |
+---------------------------+------------+-----------+-----------+----------------+--------------+----------------------------+------------------+
|  63%                      | 1621       |     1023  | 584       |        1       |       13     |                    0       |   21             |
+---------------------------+------------+-----------+-----------+----------------+--------------+----------------------------+------------------+

- `django-filter.txt <../_static/django-filter.txt>`_

Settings
--------

Via ``dm repo test django-filter --show``

::

    {
        "apps_file": {
            "source": "config/allauth/allauth_apps.py",
            "target": "src/django-allauth/allauth/mongo_apps.py",
        },
        "clone_dir": "src/django-allauth",
        "migrations_dir": {
            "source": "src/django-mongodb-project/mongo_migrations",
            "target": "src/django-allauth/allauth/mongo_migrations",
        },
        "settings": {
            "test": {
                "source": "config/allauth/allauth_settings.py",
                "target": "src/django-allauth/allauth/mongo_settings.py",
            },
            "migrations": {
                "source": "config/allauth/allauth_settings.py",
                "target": "src/django-allauth/allauth/mongo_settings.py",
            },
            "module": {
                "test": "allauth.mongo_settings",
                "migrations": "allauth.mongo_settings",
            },
        },
        "test_command": "pytest",
        "test_dir": "src/django-allauth",
        "test_dirs": [
            "src/django-allauth/allauth/usersessions/tests",
            "src/django-allauth/allauth/core/tests",
            "src/django-allauth/allauth/core/internal/tests",
            "src/django-allauth/allauth/tests",
            "src/django-allauth/allauth/mfa/recovery_codes/tests",
            "src/django-allauth/allauth/mfa/webauthn/tests",
            "src/django-allauth/allauth/mfa/totp/tests",
            "src/django-allauth/allauth/mfa/base/tests",
            "src/django-allauth/allauth/socialaccount/providers/oauth2/tests",
            "src/django-allauth/allauth/socialaccount/tests",
            "src/django-allauth/allauth/socialaccount/internal/tests",
            "src/django-allauth/allauth/templates/tests",
            "src/django-allauth/allauth/headless/usersessions/tests",
            "src/django-allauth/allauth/headless/tests",
            "src/django-allauth/allauth/headless/spec/tests",
            "src/django-allauth/allauth/headless/internal/tests",
            "src/django-allauth/allauth/headless/mfa/tests",
            "src/django-allauth/allauth/headless/socialaccount/tests",
            "src/django-allauth/allauth/headless/contrib/ninja/tests",
            "src/django-allauth/allauth/headless/contrib/rest_framework/tests",
            "src/django-allauth/allauth/headless/account/tests",
            "src/django-allauth/allauth/headless/base/tests",
            "src/django-allauth/allauth/account/tests",
            "src/django-allauth/tests",
        ],
    }

Tests
-----

Via ``dm repo test django-filter -l``

::

    src/django-allauth/allauth/usersessions/tests
        ├── test_middleware.py
        └── test_views.py

    src/django-allauth/allauth/core/tests
        └── test_ratelimit.py

    src/django-allauth/allauth/core/internal/tests
        ├── test_httpkit.py
        └── test_modelkit.py

    src/django-allauth/allauth/tests
        └── test_utils.py

    src/django-allauth/allauth/mfa/recovery_codes/tests
        ├── test_auth.py
        └── test_views.py

    src/django-allauth/allauth/mfa/webauthn/tests
        └── test_views.py

    src/django-allauth/allauth/mfa/totp/tests
        ├── test_unit.py
        └── test_views.py

    src/django-allauth/allauth/mfa/base/tests
        ├── test_trust.py
        ├── test_trust_fingerprint.py
        └── test_views.py

    src/django-allauth/allauth/socialaccount/providers/oauth2/tests
        └── test_views.py

    src/django-allauth/allauth/socialaccount/tests
        ├── conftest.py
        ├── test_adapter.py
        ├── test_connect.py
        ├── test_login.py
        ├── test_registry.py
        ├── test_signup.py
        └── test_utils.py

    src/django-allauth/allauth/socialaccount/internal/tests
        ├── test_jwtkit.py
        └── test_statekit.py

    src/django-allauth/allauth/templates/tests
        └── test_403_csrf.html

    src/django-allauth/allauth/headless/usersessions/tests
        └── test_views.py

    src/django-allauth/allauth/headless/tests
        └── test_tokens.py

    src/django-allauth/allauth/headless/spec/tests
        └── test_views.py

    src/django-allauth/allauth/headless/internal/tests
        └── test_authkit.py

    src/django-allauth/allauth/headless/mfa/tests
        ├── test_recovery_codes.py
        ├── test_totp.py
        ├── test_trust.py
        ├── test_views.py
        └── test_webauthn.py

    src/django-allauth/allauth/headless/socialaccount/tests
        ├── test_inputs.py
        └── test_views.py

    src/django-allauth/allauth/headless/contrib/ninja/tests
        └── test_security.py

    src/django-allauth/allauth/headless/contrib/rest_framework/tests
        └── test_authentication.py

    src/django-allauth/allauth/headless/account/tests
        ├── test_change_email.py
        ├── test_change_password.py
        ├── test_email_verification.py
        ├── test_email_verification_by_code.py
        ├── test_login.py
        ├── test_login_by_code.py
        ├── test_phone.py
        ├── test_reauthentication.py
        ├── test_reset_password.py
        ├── test_reset_password_by_code.py
        ├── test_session.py
        └── test_signup.py

    src/django-allauth/allauth/headless/base/tests
        └── test_views.py

    src/django-allauth/allauth/account/tests
        ├── test_adapter.py
        ├── test_ajax.py
        ├── test_auth_backends.py
        ├── test_change_email.py
        ├── test_change_password.py
        ├── test_commands.py
        ├── test_decorators.py
        ├── test_email_verification.py
        ├── test_email_verification_by_code.py
        ├── test_login.py
        ├── test_login_by_code.py
        ├── test_logout.py
        ├── test_middleware.py
        ├── test_models.py
        ├── test_phone.py
        ├── test_ratelimit.py
        ├── test_reauthentication.py
        ├── test_reset_password.py
        ├── test_reset_password_by_code.py
        ├── test_security.py
        ├── test_signup.py
        └── test_utils.py

    src/django-allauth/tests
        ├── account_only
        ├── common
        ├── headless_only
        ├── login_required_mw
        └── regular
