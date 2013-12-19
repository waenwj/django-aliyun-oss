__author__ = 'waen'
import os
import mimetypes

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import Storage
from django.core.exceptions import ImproperlyConfigured

from aliyun_oss.oss.oss_api import OssAPI
from aliyun_oss.oss.oss_util import convert_header2map, safe_get_element

ACCESS_ADDRESS          = getattr(settings, 'OSS_ACCESS_URL', 'oss.aliyuncs.com')
ACCESS_KEY_NAME     = getattr(settings, 'OSS_ACCESS_KEY_ID')
SECRET_KEY_NAME     = getattr(settings, 'OSS_SECRET_ACCESS_KEY')
HEADERS             = getattr(settings, 'OSS_HEADERS', {})
DEFAULT_ACL         = getattr(settings, 'OSS_DEFAULT_ACL', 'public-read')
OSS_STORAGE_BUCKET_NAME = getattr(settings, 'OSS_STORAGE_BUCKET_NAME')
BUCKET_PREFIX       = getattr(settings, 'OSS_BUCKET_PREFIX', '')


class OSSStorage(Storage):
    """Aliyun Open Storage Service"""

    def __init__(self, bucket=OSS_STORAGE_BUCKET_NAME,
                access_key=None,
                secret_key=None,
                acl=DEFAULT_ACL,
                # calling_format=CALLING_FORMAT,
                encrypt=False,
                # gzip=IS_GZIPPED,
                # gzip_content_types=GZIP_CONTENT_TYPES,
                # preload_metadata=PRELOAD_METADATA
            ):
        self.bucket = bucket
        self.acl = acl

        if not access_key and not secret_key:
            access_key, secret_key = self._get_access_keys()

        self.connection = OssAPI(ACCESS_ADDRESS, access_key, secret_key)
        self.headers = HEADERS


    def _get_access_keys(self):
        access_key = ACCESS_KEY_NAME
        secret_key = SECRET_KEY_NAME
        if (access_key or secret_key) and (not access_key or not secret_key):
            access_key = os.environ.get(ACCESS_KEY_NAME)
            secret_key = os.environ.get(SECRET_KEY_NAME)

        if access_key and secret_key:
            return access_key, secret_key

        return None, None

    def _clean_name(self, name):
        # Useful for windows' paths
        return os.path.join(BUCKET_PREFIX, os.path.normpath(name).replace('\\', '/'))

    def _put_file(self, name, content, content_type=None):
        if content_type:
            pass
        else:
            content_type = mimetypes.guess_type(name)[0] or "application/x-octet-stream"

        self.headers.update({
            'x-oss-acl': self.acl,
            'Content-Type': content_type,
            'Content-Length': str(len(content)),
        })
        fp = StringIO(content)
        response = self.connection.put_object_from_fp(self.bucket, name, fp, content_type, self.headers)
        if (res.status / 100) != 2:
            raise IOError("OSSStorageError: %s" % response.read())

    def _open(self, name, mode='rb'):
        name = self._clean_name(name)
        remote_file = OSSStorageFile(name, self, mode=mode)
        return remote_file

    def _read(self, name, start_range=None, end_range=None):
        name = self._clean_name(name)
        if start_range is None:
            headers = {}
        else:
            headers = {'Range': 'bytes=%s-%s' % (start_range, end_range)}
        response = self.connection.get_object(self.bucket, name, headers)
        if (res.status / 100) != 2:
            raise IOError("OSSStorageError: %s" % response.read())

        header_map = convert_header2map(response.getheaders())
        content_len = safe_get_element("content-length", header_map)
        etag = safe_get_element("etag", header_map).upper()
        return response.read(), etag, content_len

    def _save(self, name, content):
        name = self._clean_name(name)
        content.open()
        if hasattr(content, 'chunks'):
            content_str = ''.join(chunk for chunk in content.chunks())
        else:
            content_str = content.read()
        self._put_file(name, content_str)
        return name

    def delete(self, name):
        name = self._clean_name(name)
        response = self.connection.delete_object(self.bucket, name)
        if response.status != 204:
            raise IOError("OSSStorageError: %s" % response.read())

    def exists(self, name):
        name = self._clean_name(name)
        response = self.connection.head_object(self.bucket, name)
        return response.status == 200

    def size(self, name):
        name = self._clean_name(name)
        response = self.connection.head_object(self.bucket, name)
        header_map = convert_header2map(response.getheaders())
        content_len = safe_get_element("content-length", header_map)
        return content_len and int(content_len) or 0

    def url(self, name):
        name = self._clean_name(name)
        return '%s%s' % (settings.MEDIA_URL, name)

    def modified_time(self, name):
        try:
           from dateutil import parser, tz
        except ImportError:
            raise NotImplementedError()
        name = self._clean_name(name)
        response = self.connection.head_object(self.bucket, name)
        header_map = convert_header2map(response.getheaders())
        last_modified = response.getheader('Last-Modified')
        # convert to string to date
        last_modified_date = parser.parse(last_modified)
        # if the date has no timzone, assume UTC
        if last_modified_date.tzinfo == None:
            last_modified_date = last_modified_date.replace(tzinfo=tz.tzutc())
        # convert date to local time w/o timezone
        return last_modified_date.astimezone(tz.tzlocal()).replace(tzinfo=None)

    ## UNCOMMENT BELOW IF NECESSARY
    #def get_available_name(self, name):
    #    """ Overwrite existing file with the same name. """
    #    name = self._clean_name(name)
    #    return name

    def copy_to_file(self, name, target):
        name = self._clean_name(name)
        response = self.connection.get_object_to_file(self.bucket, name, target)
        if response.status / 100 != 2:
            raise IOError("OSSStorageError: %s" % response.read())

    def save_file(self, filename, name):
        name = self._clean_name(name)
        response = self.connection.put_object_from_file(self.bucket, name, filename=filename, headers=self.headers)
        if response.status / 100 != 2:
            raise IOError("OSSStorageError: %s" % response.read())


class OSSStorageFile(File):
    def __init__(self, name, storage, mode):
        self._name = name
        self._storage = storage
        self._mode = mode
        self._is_dirty = False
        self.file = StringIO()
        self.start_range = 0

    @property
    def size(self):
        if not hasattr(self, '_size'):
            self._size = self._storage.size(self._name)
        return self._size

    def read(self, num_bytes=None):
        if num_bytes is None:
            args = []
            self.start_range = 0
        else:
            args = [self.start_range, self.start_range+num_bytes-1]
        data, etags, content_range = self._storage._read(self._name, *args)
        if content_range is not None:
            current_range, size = content_range.split(' ', 1)[1].split('/', 1)
            start_range, end_range = current_range.split('-', 1)
            self._size, self.start_range = int(size), int(end_range)+1
        self.file = StringIO(data)
        return self.file.getvalue()

    def write(self, content):
        if 'w' not in self._mode:
            raise AttributeError("File was opened for read-only access.")
        self.file = StringIO(content)
        self._is_dirty = True

    def close(self):
        if self._is_dirty:
            self._storage._put_file(self._name, self.file.getvalue())
        self.file.close()
