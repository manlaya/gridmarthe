# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
#

import difflib
import functools
import warnings
from typing import Any, Callable, Dict


def _get_closest_match(key, choices, n=1, cutoff=0.6):
    """Get the closest match to x in choices using difflib.get_close_matches."""
    matches = difflib.get_close_matches(key, choices, n=n, cutoff=cutoff)
    return matches[:n] if matches else None


def _get_signature(func: Callable) -> str:
    """Get the signature of a function as a dict."""
    from inspect import signature  #, getargs, getfullargspec
    # available_args = getfullargspec(func).args
    available_args = list(signature(func).parameters.keys())
    return available_args


def _check_args(func: Callable, kwargs: Dict[str, Any]):
    """Check if the provided kwargs are valid for the function."""
    available_args = _get_signature(func)
    for key in kwargs:
        if key not in available_args:
            closest = _get_closest_match(key, available_args)
            msg = f"Argument '{key}' is not valid for function '{func.__name__}'."
            if closest:
                msg += f" Did you mean '{closest[0]}'?"
            raise TypeError(msg)


# def check_args(func: Callable):
#     """Decorator to check if the provided kwargs are valid for the function.
#     Usage:
#     @check_args
#     def my_function(arg1, arg2, ...):
#         ...
#     """
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         _check_args(func, kwargs)
#         return func(*args, **kwargs)
#     return wrapper


# decorator and deprecation argument from :
# https://stackoverflow.com/questions/49802412/how-to-implement-deprecation-in-python-with-argument-alias
def deprecated_alias(**aliases: str) -> Callable:
    """Decorator for deprecated function and method arguments.

    Use as follows:

    @deprecated_alias(old_arg='new_arg')
    def myfunc(new_arg):
        ...

    """

    def deco(f: Callable):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            rename_kwargs(f.__name__, kwargs, aliases)
            return f(*args, **kwargs)
        return wrapper
    return deco


def rename_kwargs(func_name: str, kwargs: Dict[str, Any], aliases: Dict[str, str]):
    """Helper function for deprecating function arguments."""
    for alias, new in aliases.items():
        if alias in kwargs:
            if new in kwargs:
                raise TypeError(
                    f"{func_name} received both {alias} and {new} as arguments!"
                    f" {alias} is deprecated, use {new} instead."
                )
            warnings.warn(
                message=(
                    f"`{alias}` is deprecated as an argument to `{func_name}`; "
                    f" Please use `{new}` as a replacement."
                ),
                category=DeprecationWarning,
                stacklevel=3,
            )
            kwargs[new] = kwargs.pop(alias)
