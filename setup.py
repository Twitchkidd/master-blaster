import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="master-blaster",
    version="1.0.6",
    author="Gareth Field",
    author_email="field.gareth@gmail.com",
    description="Rename primary branches of code repositories.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Twitchkidd/master-blaster",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    scripts=["bin/master-blaster"]
)
