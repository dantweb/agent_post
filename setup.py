from setuptools import setup, find_packages

setup(
    name='message_processor',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests',
        'SQLAlchemy>=1.4.0',  # Specify SQLAlchemy version for clarity and compatibility
        'schedule',
        'pytest'  # For testing
    ],
    entry_points={
        'console_scripts': [
            'message_processor = service:main'
        ]
    }
)
