import base64
import re
import uuid
from django.core.files.base import ContentFile
import secrets
from django.core.cache import cache
import kavenegar
import hashlib
from rest_framework_jwt.settings import api_settings


def imageSize(b64string):
    return (len(b64string) * 3) / 4 - b64string.count('=', -2)


def imageConvertor(base_64_image):
    base64_file = base_64_image
    image_size = imageSize(base_64_image)
    format, imgstr = base64_file.split(';base64,')
    ext = format.split('/')[-1]
    name = str(uuid.uuid4())
    data = ContentFile(base64.b64decode(imgstr), name=name + "." + ext)
    return data, ext, name, image_size


class OneTimePassMixin:
    def generate(self, request, ttl, template):
        secretsGenerator = secrets.SystemRandom()
        # data = secretsGenerator.randint(11111, 11111)
        data = 11111
        cache.set("{}{}".format(template, request.data.get('mobile', request.user)),
                  hashlib.md5(str(data).encode()).hexdigest(), timeout=ttl)
        # api_key = ""
        # api = kavenegar.KavenegarAPI(api_key)
        # params = {
        #     'receptor': request.data.get('mobile', request.user),
        #     'template': template,
        #     'token': data,
        #     'type': 'sms',
        # }
        # response = api.verify_lookup(params)

    def getTTL(self, request, template):
        return cache.ttl("{}{}".format(template, request.data.get('mobile', request.user)))

    def getValue(self, request, template):
        token = cache.get("{}{}".format(template, request.data.get('mobile', request.user)))
        return token

    def deleteValue(self, request, template):
        cache.delete("{}{}".format(template, request.data.get('mobile', request.user)))


class jWTMixin:
    def getToken(self, user):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        return jwt_encode_handler(payload)
