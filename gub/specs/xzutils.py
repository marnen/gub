#
from gub import tools

class Xzutils__tools (tools.AutoBuild):
    source = 'https://tukaani.org/xz/xz-5.0.7.tar.bz2'
    dependencies = ['tools::bzip2']
