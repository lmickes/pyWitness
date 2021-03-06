from setuptools import setup, find_packages

setup(
    name='pyWitness',
    version='0.1',
    packages=find_packages(exclude=["docs"]),
    # Not sure how strict these need to be...
    install_requires=["matplotlib",
                      "numpy",
                      "scipy",
                      "pandas"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    python_requires=">=3.7.*",

    author='Laura Mickes',
    author_email='laura.mickes@rhul.ac.uk',
    description=("Python utilities for eyewitness research"),
    license="GPL3",
    url='https://github.com/lmickes/pyWitness'
)
