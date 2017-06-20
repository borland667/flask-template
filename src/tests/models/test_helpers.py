from restify.extensions import database
from restify.models.helpers import count
from restify.models.pypi import Package


def test_count():
    Package.query.delete()
    database.session.commit()

    assert 0 == count(Package.name, '')
    assert 0 == count(Package.name, '%')
    assert 0 == count(Package.name, '%', True)

    database.session.add(Package(name='packageA', summary='Test Package', latest_version='1.0.0'))
    database.session.commit()

    assert 0 == count(Package.name, '%')
    assert 1 == count(Package.name, '%', True)

    database.session.add(Package(name='packageB', summary='Test Package', latest_version='1.0.0'))
    database.session.commit()

    assert 0 == count(Package.name, 'package')
    assert 1 == count(Package.name, 'packagea')
    assert 0 == count(Package.name, 'package%')
    assert 2 == count(Package.name, 'package%', True)
