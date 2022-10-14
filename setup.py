import setuptools
import versioneer

# from iplotLogging._version import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iplotLogging",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    # setup_requires=["setuptools-git-versioning"],
    # version_config={
    #     "version_callback": __version__,
    #     "template": "{tag}",
    #     "dirty_template": "{tag}.dev{ccount}.{sha}",
    # },
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
    python_requires=">=3.6",
    packages=["iplotLogging"],
)
