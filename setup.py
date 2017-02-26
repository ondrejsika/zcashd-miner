from setuptools import setup, find_packages

setup(
    name='zcashd-miner',
    version='1.0.0',
    url='https://github.com/ondrejsika/zcashd-miner',
    license='MIT',
    description='CPU miner for Zcash',
    author='Ondrej Sika',
    author_email='ondrej@ondrejsika.com',
    packages=find_packages(),
    package_data={'': ['*.so']},
    include_package_data=True,
    scripts=[
        'zcashd-miner.py',
    ],
    install_requires=[
        'jsonrpc-requests>=0.3',
        'cffi>=1.9.1',
    ],
)
