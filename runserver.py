from muzapi import create_app
muzlog = create_app('config')
muzlog.run(host='0.0.0.0')
