import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="quick-queue",
    version="1.0.6",
    author="Ramon Invarato Menendez",
    author_email="r.invarato@gmail.com",
    description="Quick Multiprocessing Queue for Python (Wrap of multiprocessing.queue to increase data transfer "
                "velocity between processes)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Invarato/sort_in_disk_project",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
