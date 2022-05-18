from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='access_instructor_client',
    version='0.0.1',
    description='Access instructor client',
    long_description=readme(),
    author='Sam Pepler',
    author_email='sam.pepler@stfc.ac.uk',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
    keywords='ingest',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    package_data={},
    install_requires=[
        'requests',
        'click'
    ],
    entry_points={
        'console_scripts': [
            'access_instructor=access_instructor.access_instructor:main',
        ],
    },
)

