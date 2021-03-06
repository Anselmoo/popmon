# Utility function to set matplotlib backend

import logging
import os
import sys

logger = logging.getLogger()


def set_matplotlib_backend(backend=None, batch=None, silent=True):
    """Set Matplotlib backend.

    Copyright Eskapade: Kindly taken and modified from Eskapade package.
    Reference link: https://github.com/KaveIO/Eskapade-Core/blob/master/python/escore/utils.py
    License: https://github.com/KaveIO/Eskapade-Core/blob/master/LICENSE
    All modifications copyright ING WBAA.

    :param str backend: backend to set
    :param bool batch: require backend to be non-interactive
    :param bool silent: do not raise exception if backend cannot be set
    :raises: RuntimeError
    """
    try:
        # it's very useful to call this function in the configuration of popmon,
        # but we don't require matplotlib to be installed
        import matplotlib
    except (ModuleNotFoundError, AttributeError):
        # matplotlib library not found, so anyhow nothing to configure
        return

    # determine if we think batch mode is required
    run_interactive = check_interactive_backend()

    # priority: 1) function arg, 2) check_interactive_backend()
    if (batch is not None) and isinstance(batch, bool):
        run_batch = batch
    else:
        run_batch = not run_interactive

    # check if interactive mode actually can be used, if it is requested
    if (not run_batch) and (not run_interactive):
        if not silent:
            raise RuntimeError(
                "Interactive Matplotlib mode requested, but no display found."
            )
        logger.warning("Matplotlib cannot be used interactively; no display found.")

    if run_batch:
        matplotlib.interactive(False)

    # get Matplotlib backends (note: this imports pyplot behind the scenes!)
    pyplot_imported = "matplotlib.pyplot" in sys.modules
    curr_backend = matplotlib.get_backend().lower()
    ni_backends = [nib.lower() for nib in matplotlib.rcsetup.non_interactive_bk]

    # determine backend to be set
    if not backend:
        # try to use current backend
        backend = (
            curr_backend
            if not run_batch or curr_backend in ni_backends
            else ni_backends[0]
        )
    backend = str(backend).lower()

    # check if backend is compatible with mode
    if run_batch and backend not in ni_backends:
        if not silent:
            raise RuntimeError(
                'Non-interactive Matplotlib backend required, but "{!s}" requested.'.format(
                    backend
                )
            )
        logger.warning(
            'Set Matplotlib backend to "{0:s}"; non-interactive backend required, but "{1:s}" requested.'.format(
                ni_backends[0], backend
            )
        )
        backend = ni_backends[0]

    # check if backend has to change
    if backend == curr_backend:
        return

    # check if backend can still be set
    if pyplot_imported:
        if not silent:
            raise RuntimeError(
                "Cannot set Matplotlib backend: pyplot module already loaded."
            )
        else:
            logger.warning(
                "Cannot set Matplotlib backend: pyplot module already loaded."
            )
        return

    # set matplotlib backend
    matplotlib.use(backend)


def check_interactive_backend():
    """Check whether an interactive backend is required

    Copyright Eskapade:
    Kindly taken from Eskapade package.
    Reference link: https://github.com/KaveIO/Eskapade-Core/blob/master/python/escore/utils.py
    License: https://github.com/KaveIO/Eskapade-Core/blob/master/LICENSE

    :return: true if interactive
    :rtype: bool
    """
    run_ipynb = in_ipynb()
    display = os.environ.get("DISPLAY")
    run_display = (
        display is None or not display.startswith(":") or not display[1].isdigit()
    )
    return True if run_ipynb or not run_display else False


def in_ipynb():
    """Detect whether an Jupyter/Ipython-kernel is being run

    Copyright Eskapade:
    Kindly taken from Eskapade package.
    Reference link: https://github.com/KaveIO/Eskapade-Core/blob/master/python/escore/utils.py
    License: https://github.com/KaveIO/Eskapade-Core/blob/master/LICENSE

    :return: true if in ipynb
    :rtype: bool
    """
    try:
        import IPython.core.getipython as gip

        cfg = gip.get_ipython().config
        return True if "IPKernelApp" in cfg.keys() else False
    except (ModuleNotFoundError, AttributeError):
        return False
