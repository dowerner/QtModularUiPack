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
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache License 2.0',
        'Operating System :: OS Independent',
    ],
)

"""namespace_packages=['QtModularUiPack.Framework',
                        'QtModularUiPack.ModularApplications',
                        'QtModularUiPack.ViewModels',
                        'QtModularUiPack.Widgets'],"""
