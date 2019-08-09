import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='QtModularUiPack-Dominik-Werner',
    version='0.0.1',
    author='Dominik Werner',
    author_email='dominikw@bluewin.ch',
    description='A module for quick and easy creation of highly modular PyQt5 applications.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dowerner/QtModularUiPack',
    packages=setuptools.find_packages(),
    install_requires=[
        'json5>=0.8.5',
        'PyQt5>=5.12',
        'numpy>=1.15.0',
        'matplotlib>=3.1.0',
        'pyqtgraph>=0.10.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
)