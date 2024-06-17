
# Develop

Run `poetry install` to create a virtual environment and install the dependencies.

You can add it to IDE as a python interpreter to run all files in the virtual environment.

Execute `poetry run <my_python_file>.py` to run the python file in the virtual environment.

To test the package, you can just add `Sources Root` to the `lessmore.utils` directory in your IDE.

# Install for your service

Add dependency to your `pyproject.toml` file: 

For your lib:
```toml
"lessmore.utils" = {git = "https://github.com/engineering-friends/lessmore.git", subdirectory = "source/python/libs/lessmore.utils"}
```

For your service specify the revision as well:
```toml
"lessmore.utils" = {git = "https://github.com/engineering-friends/lessmore.git", rev = "<commit_hash_you_want_to_install>", subdirectory = "source/python/libs/lessmore.utils"}
```

Then run `poetry install` to install the package.
