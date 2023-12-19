import setuptools
import os
import sys

sys.path.append(os.getcwd())
import versioneer

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iplotLogging",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Lana Abadie",
    author_email="lana.abadie@iter.org",
    description="General logging support for IDV components",
    long_description=long_description,
    url="https://git.iter.org/scm/vis/logging.git",
    project_urls={
        "Bug Tracker": "https://jira.iter.org/issues/?jql=project+%3D+IDV+AND+component+%3D+Logging",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="ITER logging",
    setup_requires=["setuptools"],
    python_requires=">=3.6",
    packages=["iplotLogging"],
    tests_require=["pytest"],
    test_suite="tests",
)
