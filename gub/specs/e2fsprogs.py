from gub import mirrors
from gub import targetpackage

http://www.eecs.harvard.edu/~nr/noweb/dist/noweb-2.11b.tgz


class E2fsprogs (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.sf, version='1.38')
    def install_command (self):
        return (targetpackage.TargetBuild.install_command (self)
                + ' install-libs')
