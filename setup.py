from setuptools import setup


setup(
    name = 'ppsp',
    packages = ['ppsp'],
    version = '3.0.1',
    description = 'PPSP is a useful python utility '
                'for running a command, getting command '
                'line output, and writing additional commands '
                'while the process is running.',
    url = 'https://github.com/brandongraylong/PPSP',
    download_url = 'https://github.com/brandongraylong/PPSP/archive/v3.0.1.tar.gz',
    author = 'Brandon Long',
    license = 'MIT',
    keywords = ['PERSISTENT', 'SHELL', 'PROCESS'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
)
