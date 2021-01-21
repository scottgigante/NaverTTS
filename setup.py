from setuptools import setup, find_packages
import os

version_py = os.path.join(os.path.dirname(__file__), "navertts", "version.py")
version = open(version_py).read().strip().split("=")[-1].replace('"', "").strip()

setup(
    name="NaverTTS",
    packages=find_packages(),
    python_requires=">= 3.5",
    setup_requires=[
        "setuptools >= 38.6",
        "wheel >= 0.31.0",
    ],
    include_package_data=True,
    install_requires=[
        "six",
        "beautifulsoup4",
        "click",
        "requests",
    ],
    extras_require={
        "test": [
            "pytest >= 4.6",
            "pytest-cov",
            "flake8",
            "testfixtures",
            "mock",
        ]
    },
    entry_points={"console_scripts": ["navertts-cli=navertts.cli:tts_cli"]},
    description="NaverTTS (NAVER Text-to-Speech), a Python library and CLI tool to interface with NAVER Papago text-to-speech API",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author="Scott Gigante",
    author_email="scottgigante@gmail.com",
    url="https://github.com/scottgigante/NaverTTS",
    version=version,
    test_suite="navertts.tests",
    keywords=[
        "navertts",
        "text to speech",
        "NAVER Papago",
        "TTS",
    ],
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    license="MIT",
)
