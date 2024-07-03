"""
this piece of code is for backward compatibility support
first the installation of respective tool utility shall be done here
if the tool utility library is not installed then it will be detected
and installation of tool utility library shall be done
"""
# un-used import flake issue ignored as this file is for installing latest available library
# flake8: noqa: F401
try:
    import contest_canoe
except ImportError:
    from uim.uim import install_contest_pkg_for_backward_compatibility_support

    install_contest_pkg_for_backward_compatibility_support("contest_canoe")
