from setuptools import find_packages
from setuptools import setup

version = '0.1'

setup(name='CrudAlchemy',
      version=version,
      description="Helper which encapsulates CRUD operations on SQLAlchemy models.",
      long_description="""\
An helper class which encapsulates common CRUD operations on SQLAlchemy mapped classes.""",
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Topic :: Database'],
      keywords='crud sqlalchemy',
      author='Stefano Fontanelli',
      author_email='s.fontanelli@asidev.com',
      url='https://github.com/stefanofontanelli/CrudAlchemy',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
            'SQLAlchemy',
            'ColanderAlchemy'],
      tests_require=[],
      test_suite='tests',
      )
