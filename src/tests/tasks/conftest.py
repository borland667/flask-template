import pytest

from restify.extensions import db
from restify.models.pypi import Package


@pytest.fixture
def drop_table():
    """Drops the pypi.Package table from the database."""
    Package.query.delete()  # Drop all rows.
    db.session.commit()
    Package.__table__.drop(db.engine)  # Drop the table.
    db.session.commit()
    db.create_all()
    assert [] == Package.query.all()
