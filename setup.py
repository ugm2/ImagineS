import setuptools
import subprocess
import os

remote_version = (
    subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
    .stdout.decode("utf-8")
    .strip()
)
assert "." in remote_version

assert os.path.isfile("cf_remote/version.py")
with open("cf_remote/VERSION", "w", encoding="utf-8") as fh:
    fh.write(f"{remote_version}\n")

# Requirements
thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

# Readme
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="imagines",
    version=remote_version,
    author="Unai Garay",
    author_email="unaigaraymaestre@gmail.com",
    description="ImagineS (Image Engine Search) tool augments an image dataset by searching a series of queries in Google Images.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ugm2/ImagineS",
    packages=setuptools.find_packages(include=['imagines']),
    package_data={
        'imagines': ['VERSION']
    },
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
