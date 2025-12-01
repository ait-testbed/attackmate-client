from setuptools import setup

setup(
    name='attackmate_client',
    version='1.0.0',
    description='A command-line client for remote execution of AttackMate playbooks.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Thorina Boenke',
    url='https://github.com/ait-testbed/attackmate-client',
    py_modules=['attackmate_client'],
    install_requires=[
        'httpx',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'attackmate-client = client:main', 
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)