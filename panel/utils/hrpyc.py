"""
This module provides access to Houdini (via the hou module) from a separate
Python process.  It uses the RPyC library (rpyc.wikidot.com).

To start a server (in a new thread), run:
    hrpyc.start_server()
This function returns the thread that was created.

To attach to the server from a client, run:
    connection, hou = hrpyc.import_remote_module()
The connection will remain open for the lifetime of the connection object,
and you can treat hou just as though you imported the hou module.
"""

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    # future 模块不可用时忽略
    pass
import inspect
from optparse import OptionParser
import rpyc
from rpyc.core import SlaveService
from rpyc.utils.classic import DEFAULT_SERVER_PORT
from rpyc.utils.registry import REGISTRY_PORT
from rpyc.utils.server import ThreadedServer
import threading

def _serve_threaded(options):
    t = ThreadedServer(SlaveService, hostname = options.host, 
        port = options.port, reuse_addr = True, 
        authenticator = options.authenticator, registrar = options.registrar,
        auto_register = options.auto_register)
    t.logger.quiet = options.quiet
    if options.logfile:
        t.logger.console = open(options.logfile, "w")
    t.start()

def start_server(port=18811, use_thread=True, quiet=True):
    # Note that quiet=False only applies when use_thread=False.
    if use_thread:
        thread = threading.Thread(
            target=lambda: start_server(port, use_thread=False))
        thread.start()
        return thread

    args = []
    if quiet:
        args.append("-q")
    args.extend(("-p", str(port), "--dont-register"))

    parser = OptionParser()
    parser.add_option("-m", "--mode", action="store", dest="mode", metavar="MODE",
        default="threaded", type="string", help="mode can be 'threaded', 'forking', "
        "or 'stdio' to operate over the standard IO pipes (for inetd, etc.). "
        "Default is 'threaded'")
    parser.add_option("-p", "--port", action="store", dest="port", type="int", 
        metavar="PORT", default=DEFAULT_SERVER_PORT, help="specify a different "
        "TCP listener port. Default is 18812")
    parser.add_option("--host", action="store", dest="host", type="str", 
        metavar="HOST", default="0.0.0.0", help="specify a different "
        "host to bind to. Default is 0.0.0.0")
    parser.add_option("--logfile", action="store", dest="logfile", type="str", 
        metavar="FILE", default=None, help="specify the log file to use; the "
        "default is stderr")
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet", 
        default=False, help="quiet mode (no logging). in stdio mode, "
        "writes to /dev/null")
    parser.add_option("--vdb", action="store", dest="vdbfile", metavar="FILENAME",
        default=None, help="starts an TLS/SSL authenticated server (using tlslite);"
        "the credentials are loaded from the vdb file. if not given, the server"
        "is not secure (unauthenticated). use vdbconf.py to manage vdb files"
    )
    parser.add_option("--dont-register", action="store_false", dest="auto_register", 
        default=True, help="disables this server from registering at all. "
        "By default, the server will attempt to register")
    parser.add_option("--registry-type", action="store", dest="regtype", type="str", 
        default="udp", help="can be 'udp' or 'tcp', default is 'udp'")
    parser.add_option("--registry-port", action="store", dest="regport", type="int", 
        default=REGISTRY_PORT, help="the UDP/TCP port. default is %s" % (REGISTRY_PORT,))
    parser.add_option("--registry-host", action="store", dest="reghost", type="str", 
        default=None, help="the registry host machine. for UDP, the default is "
        "255.255.255.255; for TCP, a value is required")

    options, args = parser.parse_args(args)
    options.registrar = None
    options.authenticator = None
    _serve_threaded(options)

class _RemoteHouAttrWrapper(object):
    """This class wraps a given HOM attribute.

    If the attribute is called (i.e. method call), then this class first
    ensures that the global time in the remote helper thread is synchronized
    with the global time in the remote main thread.  This guarantees that calls
    like `hou.frame()` and `hou.time()` return the expected time.

    Additionally, after the attribute is called, this class ensures that the
    global time in the remote helper thread is pushed back into the remote main
    thread.  This guarantees that changes from `hou.setFrame()` and
    `hou.setTime()` are propogated to the main global time.
    """

    def __init__(self, remote_hou, attr):
        self._remote_hou = remote_hou

        # The wrapped attribute.
        self._attr = attr

    def __repr__(self):
        # __repr__ does not go through __getattribute__ so we need to implement
        # our own version that calls the wrapped attribute's __repr__.
        return object.__getattribute__(self, "_attr").__repr__()

    def __call__(self, *args, **kwargs):
        # The remote hou module.
        # We cannot do "self._remote_hou" as that will go through
        # __getattribute__().
        wrapped_remote_hou = object.__getattribute__(self, "_remote_hou")

        # Synchronize the global time from the main thread.
        wrapped_remote_hou._syncFromMainContext()

        # Call the underlying HOM method.
        # Note that we cannot do "self._attr" as that will go through
        # __getattribute__().
        result = object.__getattribute__(self, "_attr")(*args, **kwargs)

        # Synchronize the global time back to the main thread.
        wrapped_remote_hou._syncToMainContext()

        return result

    def __getattribute__(self, name):
        # The wrapped attribute.
        # Note that we cannot do "self._attr" as that will recursively
        # call __getattribute__().
        wrapped_attr = object.__getattribute__(self, "_attr")

        # The attribute on the wrapped attribute that is being requested.
        requested_attr = wrapped_attr.__getattribute__(name)

        # Return class/enum and private attributes as-is.  No wrapper.
        # HOM classes and enums appear as class attributes.
        if name.startswith("_") or inspect.isclass(requested_attr):
            return requested_attr

        # Return a wrapper around the requested attribute.
        # Note that we cannot do "self._remote_hou" as that will
        # recusively call __getattribute__.
        wrapped_remote_hou = object.__getattribute__(self, "_remote_hou")
        attr_wrapper = _RemoteHouAttrWrapper(wrapped_remote_hou, requested_attr)
        return attr_wrapper


def import_remote_module(server="127.0.0.1", port=18811, name="hou"):
    connection = rpyc.classic.connect(server, port)
    remote_module = connection.modules[name]

    if name == "hou":
        # Wrap the remote 'hou' module in a class that ensures
        # the worker thread's global time is synchronized with the main
        # thread's global time.
        remote_module = _RemoteHouAttrWrapper(remote_module, remote_module)

    return connection, remote_module

