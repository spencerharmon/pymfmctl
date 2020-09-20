from setuptools import setup, find_namespace_packages

setup(
    name="pymfmctl",
    version="0.1",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    author="Spencer Harmon",
    author_email="the.spencer.harmon@gmail.com",
    description="Runs the mfm simulator and searches JSON output for specified conditions",
    keywords="MFM Ulam artificial life",
    url="http://www.github.com/spencerharmon/pymfmctl",
    entry_points = {"console_scripts": 
                    [ "pymfmctl = pymfmctl.__main__:main" ],
                    },
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ]
)
