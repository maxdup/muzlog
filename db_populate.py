from muzapi import create_app, db
from muzapi.fake_data import fake_user, fake_album, fake_log, fake_comment


def populate():

    from muzapi import create_app
    app = create_app('config')

    with app.app_context():
        db.connection.drop_database(app.config['MONGODB_DB'])

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


populate()
