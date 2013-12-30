import platform
import sys

def user_agent(name, version):
    """
    Returns an internet-friendly user_agent string.

    The majority of this code has been wilfully stolen from the equivalent
    function in Requests.

    :param name: The intended name of the user-agent, e.g. "python-requests".
    :param version: The version of the user-agent, e.g. "0.0.1".
    """
    _implementation = platform.python_implementation()

    if _implementation == 'CPython':
        _implementation_version = platform.python_version()
    elif _implementation == 'PyPy':
        _implementation_version = '%s.%s.%s' % (sys.pypy_version_info.major,
                                                sys.pypy_version_info.minor,
                                                sys.pypy_version_info.micro)
        if sys.pypy_version_info.releaselevel != 'final':
            _implementation_version = ''.join([_implementation_version, sys.pypy_version_info.releaselevel])
    elif _implementation == 'Jython':
        _implementation_version = platform.python_version()  # Complete Guess
    elif _implementation == 'IronPython':
        _implementation_version = platform.python_version()  # Complete Guess
    else:
        _implementation_version = 'Unknown'

    try:
        p_system = platform.system()
        p_release = platform.release()
    except IOError:
        p_system = 'Unknown'
        p_release = 'Unknown'

    return " ".join(['%s/%s' % (name, version),
                     '%s/%s' % (_implementation, _implementation_version),
                     '%s/%s' % (p_system, p_release)])
