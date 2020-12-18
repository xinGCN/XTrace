import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="XTrace",
    version="0.0.1",
    author="Xin Gu",
    author_email="xing1481092111@gmail.com",
    description="Trace Java or OBJC methods with options that show method entry, return value, print stack, and method execution time.Base on frida.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xinGCN/XTrace",
    install_requires=[
        "frida",
    ],
    packages=["agent"],
    entry_points={
        'console_scripts': [
            "xtrace = agent.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)