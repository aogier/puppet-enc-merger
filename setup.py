'''
Created on 17/feb/2014

@author: oggei
'''

from setuptools import setup, find_packages

setup(
    name='ieo-enc',
    version='1.0',

    description='IEO - External Node Classifier',

    author='Alessandro Ogier',
    author_email='alessandro.ogier@ieo.eu',

    url='https://devel.ieo.eu/',
    download_url='https://devel.ieo.eu/',

    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: Apache Software License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3',
                 'Intended Audience :: Developers',
                 'Environment :: Console',
                 ],

    platforms=['Any'],

    scripts=[],

    provides=['ieo_enc',
              ],

    data_files = [
                  ('etc/ieo_enc', ['.placeholder']),
                  ],

    packages=find_packages(),
    include_package_data=True,
    install_requires = ['PyYAML==3.10',
                        'SQLAlchemy==0.9.2',
                        'psycopg2==2.5.2',
                        'stevedore==0.14.1',
                        ],
    entry_points={
                  'console_scripts': [
                                      'stub = enc:main',
                                      ],
                  'eu.ieo.puppet.classes': [
                                            'ieo::classes::calendar::client = enc.plugins.calendars:CalendarPlugin'
                                            ],
    },

    zip_safe=False,
)