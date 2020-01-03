from setuptools import setup

setup(
    name="qr-scanner",
    version='0.9',
    description="QR scanner",
    keywords="QR",
    author="Angelcam",
    author_email="dev@angelcam.com",
    url="https://bitbucket.org/angelcam/qr-scanner",
    license="MIT",
    long_description=open('README.md').read(),
    install_requires=[
        'avpy == 0.1.3',
        'zbar-py == 1.0.4',
        'Pillow >= 3.4.1',
        'requests >= 2.14.2',
        'pytest >= 3.1.0',
    ],
    packages=['qr_scanner'],
    package_dir={'': 'src'},
)
