from gub import build_platform
from gub import tools
import os

class File__tools (tools.AutoBuild):
    source = 'ftp://ftp.astron.com/pub/file/file-5.03.tar.gz'
    dependencies = [
            'libtool',
            'zlib',
            ]

    if 'darwin' in build_platform.machine():
        compile_command = 'DYLD_LIBRARY_PATH="%(system_prefix)s/lib" ' + tools.AutoBuild.compile_command
