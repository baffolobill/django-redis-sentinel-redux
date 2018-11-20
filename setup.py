from setuptools import setup

from django_redis_sentinel import __version__

description = """
Full featured redis cache backend for Django for Sentinel Redis Clusters.
"""

setup(
    name="django-redis-sentinel-redux",
    url="https://github.com/baffolobill/django-redis-sentinel-redux",
    author="Dani Gonzalez @danigosa",
    author_email="danigosa@gmail.com",
    version=__version__,
    packages=[
        "django_redis_sentinel",
        "django_redis_sentinel.client"
    ],
    description=description.strip(),
    install_requires=[
        "django-redis==4.10.0",
        # "git+https://github.com/gmr/consulate.git@e8acd07",
        "consulate",
    ],
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django :: 2.0",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
