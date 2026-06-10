from setuptools import setup, find_packages

setup(
    name="agent-context-handoff",
    version="0.2.0",
    description="A universal cross-agent engineering context handoff package",
    long_description=open("README.md").read() if open("README.md") else "",
    long_description_content_type="text/markdown",
    author="wangerpan",
    url="https://github.com/wangerpan/agent-context-handoff",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "ai-context-handoff=agent_context_handoff.cli:main",
        ],
    },
)
