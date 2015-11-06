from setuptools import setup, find_packages
import platform

# Pull version from source without importing
# since we can't import something we haven't built yet :)
exec(open('kafka_influxdb/version.py').read())


def readme():
    with open('README.rst') as readme_file:
        return readme_file.read()

requires = [
    "certifi",
    "funcsigs",
    "influxdb",
    "kafka-python",
    "mock",
    "nose",
    "pbr",
    "python-dateutil",
    "pytz",
    "PyYAML",
    "requests",
    "virtualenv",
    "wheel"
]

test_requires = [
    'nose',
    'nose-cover3',
    'profilehooks'
]

# Get an additional speedup with ujson,
# which is faster than the normal Python json module
# ujson does not work with PyPy
# See https://github.com/esnme/ultrajson/issues/98
if not platform.python_implementation() == 'PyPy':
    requires.append("ujson")

setup(name='kafka_influxdb',
      version=__version__,
      description='A Kafka consumer for InfluxDB',
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: Apache Software License',
          'Topic :: Utilities',
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: Implementation :: PyPy",
      ],
      keywords='kafka influxdb metrics consumer',
      url='http://github.com/mre/kafka-influxdb',
      author='Matthias Endler',
      author_email='matthias-endler@gmx.net',
      license='Apache',
      packages=find_packages(),
      install_requires=requires,
      test_suite='nose.collector',
      tests_require=test_requires,
      entry_points={
          'console_scripts': ['kafka_influxdb=kafka_influxdb.__main__:main'],
      },
      include_package_data=True,
      zip_safe=False)
