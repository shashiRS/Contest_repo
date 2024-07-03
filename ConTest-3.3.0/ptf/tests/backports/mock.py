#############################################
# ===== Start of backport of mock_open ==== #
#############################################
# This is a backport from python 3.7.2 from
# https://github.com/python/cpython/blob/9a3ffc0492d1310ead9ce8f5ee678c26b20a338d/Lib/unittest/mock.py
# It adds support for __iter__ calls that are done within file parsing.

# Since this is a copy from upstream, we don't care about pylint issues
# pylint: disable=all

from unittest.mock import MagicMock, _iterate_read_data, DEFAULT
file_spec = None

def mock_open(mock=None, read_data=''):
    """
    A helper function to create a mock to replace the use of `open`. It works
    for `open` called directly or used as a context manager.

    The `mock` argument is the mock object to configure. If `None` (the
    default) then a `MagicMock` will be created for you, with the API limited
    to methods or attributes available on standard file handles.

    `read_data` is a string for the `read` methoddline`, and `readlines` of the
    file handle to return.  This is an empty string by default.
    """
    def _readlines_side_effect(*args, **kwargs):
        if handle.readlines.return_value is not None:
            return handle.readlines.return_value
        return list(_state[0])

    def _read_side_effect(*args, **kwargs):
        if handle.read.return_value is not None:
            return handle.read.return_value
        return type(read_data)().join(_state[0])

    def _readline_side_effect():
        yield from _iter_side_effect()
        while True:
            yield type(read_data)()

    def _iter_side_effect():
        if handle.readline.return_value is not None:
            while True:
                yield handle.readline.return_value
        for line in _state[0]:
            yield line

    global file_spec
    if file_spec is None:
        import _io
        file_spec = list(set(dir(_io.TextIOWrapper)).union(set(dir(_io.BytesIO))))

    if mock is None:
        mock = MagicMock(name='open', spec=open)

    handle = MagicMock(spec=file_spec)
    handle.__enter__.return_value = handle

    _state = [_iterate_read_data(read_data), None]

    handle.write.return_value = None
    handle.read.return_value = None
    handle.readline.return_value = None
    handle.readlines.return_value = None

    handle.read.side_effect = _read_side_effect
    _state[1] = _readline_side_effect()
    handle.readline.side_effect = _state[1]
    handle.readlines.side_effect = _readlines_side_effect
    handle.__iter__.side_effect = _iter_side_effect

    def reset_data(*args, **kwargs):
        _state[0] = _iterate_read_data(read_data)
        if handle.readline.side_effect == _state[1]:
            # Only reset the side effect if the user hasn't overridden it.
            _state[1] = _readline_side_effect()
            handle.readline.side_effect = _state[1]
        return DEFAULT

    mock.side_effect = reset_data
    mock.return_value = handle
    return mock

###########################################
# ===== End of backport of mock_open ==== #
###########################################
