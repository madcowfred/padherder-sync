from distutils.core import setup
import py2exe

setup(
    options={
        'py2exe': {
            'bundle_files': 1,
            'compressed': True,
            'optimize': 2,
        }
    },
    console=['padherder_sync.py'],
    data_files=[
        ('', ['CHANGELOG', 'cacert.pem']),
    ],
)
