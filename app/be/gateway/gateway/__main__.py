#!/usr/bin/env python3
""" Gateway startup
"""

import connexion
from connexion.resolver import RestyResolver


def main():
    """ todoc
    """
    app = connexion.App(__name__, specification_dir="./definitions/")
    options = {"swagger_ui": True}
    app.add_api(
        "api.yaml",
        options=options,
        arguments={"title": "Home API"},
        resolver=RestyResolver("views"),
        strict_validation=True,
        validate_responses=True,
    )
    app.run(port=8080)


if __name__ == "__main__":
    main()
