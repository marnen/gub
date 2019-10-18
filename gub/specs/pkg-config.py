from gub import build_platform
from gub import tools

class Pkg_config__tools (tools.AutoBuild):
    dependencies = [
            'libtool',
            'system::g++',
            ]

    def __init__ (self, settings, source):
        tools.AutoBuild.__init__ (self, settings, source)
        if 'darwin' in build_platform.machine():
            self.configure_variables += 'CFLAGS="-I%(system_prefix)s/include -std=gnu89"'
