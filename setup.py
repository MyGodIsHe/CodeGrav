from setuptools import setup, find_packages


setup(
    name="CodeGrav",
    version="0.1.0",
    author="Ilya Chistyakov",
    author_email="ilchistyakov@gmail.com",
    description="2d code editor for gravis language",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/MyGodIsHe/CodeGrav",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        "pygame==2.5.2",
    ],
    entry_points={
        "console_scripts": [
            "CodeGrav=code_grav.main:main"
        ]
    },
    python_requires='>=3.12',
)
