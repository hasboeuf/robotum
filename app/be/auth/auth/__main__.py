#!/usr/bin/env python3
""" Auth startup
"""

import connexion
from connexion.resolver import RestyResolver
from flask import appcontext_tearing_down

from auth.database import db_session, init_db


def shutdown_session(exception=None):
    """ todoc
    """
    db_session.remove()


def main():
    """ todoc
    """
    app = connexion.App(__name__, specification_dir="./definitions/")
    options = {"swagger_ui": True}
    app.add_api(
        "api.yaml",
        options=options,
        arguments={"title": "Auth API"},
        resolver=RestyResolver("."),
        strict_validation=True,
        validate_responses=True,
    )
    init_db()
    appcontext_tearing_down.connect(shutdown_session, app)
    app.run(port=8081)


if __name__ == "__main__":
    main()
