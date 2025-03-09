from setuptools import setup, find_packages

setup(
    name="thecontrarian",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Django==5.1.7",
        "django-crispy-forms==2.3",
        "crispy-bootstrap5==2024.10",
        "python-decouple==3.8",
        "whitenoise==6.6.0",
        "PyMySQL==1.1.0",
    ],
    python_requires=">=3.9",
) 