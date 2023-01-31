import os, json
from django.core.exceptions import ImproperlyConfigured

# SECRET_KEY 파일 위치
secret_file = os.path.join(BASE_DIR, 'secrets.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())

# secrets.json 파일에서 SECRET_KEY 가져오기    
def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

SECRET_KEY = get_secret("SECRET_KEY")