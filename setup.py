# -*- coding: utf-8 -*-
import codecs

from setuptools import setup, find_packages

setup(
    name='ocrd_repair_inconsistencies',
    description='Repair glyph/word/line order inconsistencies',
    #long_description=codecs.open('README.md', encoding='utf-8').read(),
    author='Mike Gerber',
    author_email='mike.gerber@sbb.spk-berlin.de',
    license='Apache License 2.0',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=open('requirements.txt').read().split('\n'),
    package_data={
        '': ['*.json', '*.yml', '*.yaml'],
    },
    entry_points={
        'console_scripts': [
            'ocrd-repair-inconsistencies=ocrd_repair_inconsistencies.cli:ocrd_repair_inconsistencies',
        ]
    },
)
