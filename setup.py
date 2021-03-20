import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='QtModularUiPack',
    version='0.0.7',
    author='Dominik Werner',
    author_email='dominik.wenrer@live.com',
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
        'pyqtgraph>=0.10.0',
        'h5py>=3.2.1'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
)