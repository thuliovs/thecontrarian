from setuptools import setup, find_packages

setup(
    name="thecontrarian",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "django==5.1.7",
        "crispy-bootstrap5==2024.10",
        "uvicorn[standard]==0.34.0",
        "ptpython==3.0.29",
        "docopt==0.6.2",
        "httpx==0.28.1",
        "python-decouple==3.8",
        "whitenoise==6.6.0",
        "gunicorn==21.2.0",
    ],
) 