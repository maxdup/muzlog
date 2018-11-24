from flask_security.utils import hash_password

from muzapi import create_app, db
from muzapi.models import Role, User
from muzapi.util_fakedata import fake_user, fake_album, fake_log, fake_comment


def reset_db():
    from muzapi import create_app
    app = create_app('config')

    with app.app_context():
        db.connection.drop_database(app.config['MONGODB_DB'])


reset_db()


def populate_init():

    from muzapi import create_app
    app = create_app('config')

    with app.app_context():

        if not Role.objects(name="admin"):
            role_admin = Role(name="admin",
                              description="includes all permissions")
            role_admin.save()
        else:
            role_admin = Role.objects.get(name="admin")

        if not Role.objects(name="logger"):
            role_logger = Role(name="logger",
                               description="includes all permissions")
            role_logger.save()
        else:
            role_logger = Role.objects.get(name="admin")

        user = User(email='admin@muzlog.com',
                    username='Admin',
                    password=hash_password('changeme'),
                    roles=[role_admin])
        user.save()


populate_init()


def populate_fake():

    from muzapi import create_app
    app = create_app('config')

    with app.app_context():

        main_user = fake_user()
        main_user.save()

        for x in range(0, 100):
            album = fake_album()
            album.save()
            album.reload()

            log = fake_log(main_user, album)
            log.save()

            album.logs.append(log)
            album.save()


populate_fake()
