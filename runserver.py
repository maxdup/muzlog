from muzapi import create_app
from muzapi.db_ensure import db_ensure_roles, db_ensure_admin
muzlog = create_app()
db_ensure_roles(muzlog)
db_ensure_admin(muzlog)
muzlog.run(host='0.0.0.0')
