from gub import mirrors
from gub import targetpackage

class Faac (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.sf, version='1.24')
