from gub import tools
from gub import target
from gub import build_platform

class Bzip2 (target.MakeBuild):
    source = 'http://http.debian.net/debian/pool/main/b/bzip2/bzip2_1.0.6.orig.tar.bz2'
    compile_flags = ''' -f Makefile-libbz2_so CC='%(toolchain_prefix)sgcc %(target_gcc_flags)s -fno-stack-protector' '''
    install_flags = (target.MakeBuild.install_flags
                     + ' PREFIX=%(install_prefix)s')
    def install (self):
        target.MakeBuild.install (self)
        self.system ('cp -pv %(builddir)s/libbz2.so* %(install_prefix)s/lib')
        # junk broken symlinks
        self.system ('cd %(install_prefix)s/bin && rm -f bzless bzfgrep bzegrep bzcmp')

class Bzip2__tools (tools.MakeBuild):
    source = 'http://http.debian.net/debian/pool/main/b/bzip2/bzip2_1.0.6.orig.tar.bz2'
    patches = []
    compile_flags = ' -f Makefile-libbz2_so'
    install_flags = (tools.MakeBuild.install_flags
                     + ' PREFIX=%(install_prefix)s')

    # On darwin hosts, we need to substitute 'soname' for 'install_name'
    if 'darwin' in build_platform.machine():
        patches = patches + [
            'bzip2-1.0.6-darwin-soname.patch',
        ]

    def install (self):
        tools.MakeBuild.install (self)
        self.system ('cp -pv %(builddir)s/libbz2.so* %(install_prefix)s/lib')
        # junk broken symlinks
        self.system ('cd %(install_prefix)s/bin && rm -f bzless bzfgrep bzegrep bzcmp')
