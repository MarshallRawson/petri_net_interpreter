import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="petri_net_interpreter",
    version="0.0.1",
    author="Marshall Rawson",
    author_email="marshallrawson@ufl.edu",
    description="Yet another concurrent programming framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MarshallRawson/petri_net_interpreter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'make_petri_net = petri_net_interpreter.__main__:main'
        ]
    },
)
