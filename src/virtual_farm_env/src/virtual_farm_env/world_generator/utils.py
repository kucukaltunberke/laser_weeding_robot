from __future__ import annotations

from argparse import ArgumentParser
from inspect import getfullargspec




def parser_from_function(func: object, description: str = "") -> ArgumentParser:
    # Dynamically create argument parser with world description parameters
    argspec = getfullargspec(func)
    possible_kwargs = argspec.args[1:]
    defaults = argspec.defaults

    parser = ArgumentParser(
        description=description,
    )
    for argname, default in zip(possible_kwargs, defaults):
        # we analyze the default value's type to guess the type for that argument
        if type(default) == list:
            parser.add_argument(
                "--" + argname,
                type=type(default[0]),
                nargs="*",
                help=f"default_value: {default}",
                required=False,
            )
        else:
            parser.add_argument(
                "--" + argname,
                type=type(default),
                help=f"default_value: {default}",
                required=False,
            )

    return parser
