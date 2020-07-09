from setuptools import find_packages
from setuptools import setup

setup(
    name="unchained-bot-LivingWithHippos",
    version="0.1",
    description="Telegram Bot for Real-Debrid.",
    url="https://github.com/LivingWithHippos/unchained-bot",
    author="LivingWithHippos",
    author_email="",
    install_requires=[
        "python-telegram-bot",
        "requests",
    ],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4'
)
