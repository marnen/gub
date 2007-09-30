from gub import targetpackage
from gub import mirrors

class Psmisc (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_template (mirror=mirrors.sf, version='22.2')
    def get_subpackage_names (self):
        return ['']
    def get_build_dependencies (self):
        return ['ncurses']
