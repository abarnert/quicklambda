from distutils.core import setup
import sys

modules = ['quicklambda']

setup(name = 'quicklambda',
      version = '0.1',
      description = 'An expression template library for building "quick lambdas", like "5 + _1"',
      long_description = """
        *quicklambda* lets you write functions without the lambda keyword.
        Any expression involving a placeholder (_1 through _3), or any value
        wrapped by the _ function, becomes a function. For example:

        >>> from quicklambda import *
        >>> add1 = _1 + 1
        >>> add1(3)
        4
        >>> add1 = 1 + _1
        >>> add1(3)
        4
        >>> add = _1 + _2
        >>> add(1, 2)
        3
        >>> add = _(1) + 2
        >>> add()
        3
      """,        
      author = 'Andrew Barnert',
      author_email = 'abarnert@yahoo.com',
      url = 'https://github.com/abarnert/quicklambda',
      py_modules = modules,
      classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development"
    ],
    )
