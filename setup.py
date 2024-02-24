from setuptools import setup, find_packages

setup(
    name='neuropacs',
    version='1.4.9',
    description='NeuroPACS Python SDK',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Kerrick Cavanaugh',
    author_email='kerrick@neuropacs.com',
    url='https://github.com/neuropacs/neuropacs-py-sdk',
    packages=find_packages(),
    install_requires=[
        'certifi==2023.5.7',
        'cffi==1.15.1',
        'charset-normalizer==3.1.0',
        'cryptography==41.0.1',
        'idna==3.4',
        'Naked==0.1.32',
        'pip==23.3.1',
        'pycparser==2.21',
        'pycryptodome==3.18.0',
        'PyYAML==6.0',
        'requests==2.31.0',
        'setuptools==69.0.2',
        'shellescape==3.8.1',
        'urllib3==1.26.6',
        'wheel==0.41.2',
        'python-socketio==5.10.0',
        'tqdm==4.66.1'
        # add secrets
        # add string
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)

# To update this SDK:
# 1. Remove /build /dist /neuropacs.egg-info
# 2. Update version in setup.py and __init__.py
# 3. Run: python setup.py sdist bdist_wheel
# 4. Run: twine upload dist/*
