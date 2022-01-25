import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="dataset-augmentation", # Replace with your own username
    version="0.0.1",
    author="Unai Garay",
    author_email="unaigaraymaestre@gmail.com",
    description="Dataset Creation Tool library to help create a Dataset using scraping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ugm2/dataset-creation-tool",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)