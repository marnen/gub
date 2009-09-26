from gub.specs import guile

class Guile (guile.Guile):
    def category_dict (self):
        return {'': 'Interpreters'}
    # Using gub dependencies only would be nice, but
    # we need to a lot of gup.gub_to_distro_deps ().
    def GUB_get_dependency_dict (self): # cygwin
        d = guile.Guile.get_dependency_dict (self)
        d['runtime'].append ('cygwin')
        return d
    # Using gub dependencies only would be nice, but
    # we need to a lot of gup.gub_to_distro_deps ().
    def GUB_get_build_dependencies (self):
        return guile.Guile.dependencies + ['libiconv-devel']
    # FIXME: uses mixed gub/distro dependencies
    def get_dependency_dict (self): #cygwin
        d = guile.Guile.get_dependency_dict (self)
        d[''] += ['cygwin']
        d['devel'] += ['cygwin'] + ['bash']
        d['runtime'] += ['cygwin', 'crypt', 'libreadline6']
        return d
    # FIXME: uses mixed gub/distro dependencies
    def get_build_dependencies (self): # cygwin
        return ['crypt', 'libgmp-devel', 'gettext-devel', 'libiconv', 'libtool', 'readline']
    def config_cache_overrides (self, str):
        return str + '''
guile_cv_func_usleep_declared=${guile_cv_func_usleep_declared=yes}
guile_cv_exeext=${guile_cv_exeext=}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="%(system_prefix)s/lib"}
'''
    def configure (self):
        self.file_sub ([('''^#(LIBOBJS=".*fileblocks.*)''', r'\1')],
                       '%(srcdir)s/configure')
        guile.Guile.configure (self)
        if 0:  # should be fixed in w32.py already
            self.file_sub ([
                    ('^(allow_undefined_flag=.*)unsupported', r'\1')],
                           '%(builddir)s/libtool')
            self.file_sub ([
                    ('^(allow_undefined_flag=.*)unsupported', r'\1')],
                           '%(builddir)s/guile-readline/libtool')
    # C&P from guile.Guile__mingw
    def compile (self):
        ## Why the !?#@$ is .EXE only for guile_filter_doc_snarfage?
        self.system ('''cd %(builddir)s/libguile && make %(compile_flags_native)sCFLAGS='-DHAVE_CONFIG_H=1 -I%(builddir)s' gen-scmconfig guile_filter_doc_snarfage.exe''')
        self.system ('cd %(builddir)s/libguile && cp guile_filter_doc_snarfage.exe guile_filter_doc_snarfage')
        guile.Guile.compile (self)
    def description_dict (self):
        return {
            '': """The GNU extension language and Scheme interpreter - executables
Guile, the GNU Ubiquitous Intelligent Language for Extension, is a scheme
implementation designed for real world programming, supporting a
rich Unix interface, a module system, and undergoing rapid development.

`guile' is a scheme interpreter that can execute scheme scripts (with a
#! line at the top of the file), or run as an inferior scheme
process inside Emacs.
""",
            'runtime': '''The GNU extension language and Scheme interpreter - runtime
Guile shared object libraries and the ice-9 scheme module.  Guile is
the GNU Ubiquitous Intelligent Language for Extension.
''',
            'devel': """The GNU extension language and Scheme interpreter - development
`libguile.h' etc. C headers, aclocal macros, the `guile-snarf' and
`guile-config' utilities, and static `libguile.a' libraries for Guile,
the GNU Ubiquitous Intelligent Language for Extension.
""",
            'doc': """The GNU extension language and Scheme interpreter - documentation
This package contains the documentation for guile, including both
a reference manual (via `info guile'), and a tutorial (via `info
guile-tut').
""",
    }
