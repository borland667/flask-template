import pytest

from restify.extensions import database
from restify.models.pypi import Package


@pytest.fixture
def drop_table():
    """Drops the pypi.Package table from the database."""
    Package.query.delete()  # Drop all rows.
    database.session.commit()
    Package.__table__.drop(database.engine)  # Drop the table.
    database.session.commit()
    database.create_all()
    assert [] == Package.query.all()
