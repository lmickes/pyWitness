from setuptools import setup, find_packages

setup(
    name='pyWitness',
    version='1.1',
    packages=find_packages(exclude=["docs"]),
    # Not sure how strict these need to be...
    install_requires=["ipython",
                      "matplotlib",
                      "numpy",
                      "scipy",
                      "pandas",
                      "openpyxl",
                      "xlrd",
                      "pyreadstat"],
    #setup_requires=["pytest-runner"],
    #tests_require=["pytest"],
    python_requires=">=3.7.*",

    author='Laura Mickes',
    author_email='laura.mickes@bristol.ac.uk',
    description=("Python utilities for eyewitness research"),
    license="GPL3",
    url='https://github.com/lmickes/pyWitness'
)
