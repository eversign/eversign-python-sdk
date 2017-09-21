from distutils.core import setup

setup(
    name='eversign',
    version='0.2.4',
    packages=['eversign'],
    url='https://github.com/eversign/eversign-python-sdk',
    license='MIT',
    author='clemensehrenreich',
    author_email='clemensehrenreich@gmail.com',
    description='Eversign Python SDK',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "requests",
        "schematics",
        "six"
    ]
)
