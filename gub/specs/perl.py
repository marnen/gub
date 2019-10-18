from gub import build_platform
from gub import tools

class Perl__tools(tools.AutoBuild):
    source = 'https://www.cpan.org/src/5.0/perl-5.28.1.tar.gz'
    srcdir_build_broken = True
    configure_binary = '%(autodir)s/configure.gnu'


    if 'darwin' in build_platform.machine():
        librt_flag = '-lSystem'
        target_arch_flag = '' # TODO: fix for cross-compilation
    else:
        librt_flag = '-lrt'
        target_arch_flag = '-Dtargetarch=%(target_architecture)s'

    configure_command = ' '.join([
        '%(configure_binary)s',
        '-Aldflags="%(rpath)s"',
        '-Alibs="-lm -ldl %(librt_flag)s"',
        '-Dcc="%(toolchain_prefix)sgcc %(target_gcc_flags)s"',
        '-Dcccdlflags=-fPIC',
        '-Dincpth=/',
        '-Dlibperl=libperl.so',
        '-Dlibpth=%(system_prefix)s/lib',
        '-Dlocallibpth=/',
        '-Dprefix=%(system_prefix)s',
        '-Dsitearch=%(system_prefix)s/lib/perl5/5.28.1',
        '-Dsitelib=%(system_prefix)s/lib/perl5/5.28.1',
        target_arch_flag,
        '-Dusedl',
        '-Duseshrplib',
        '-Dusrinc=%(system_prefix)s/include',
    ])

    def patch(self):
        tools.AutoBuild.patch(self)
        self.file_sub([('-c (/dev/null)', r'-e \1')], '%(srcdir)s/Configure')

    def configure(self):
        tools.AutoBuild.configure(self)
        if 'darwin' not in build_platform.machine():
            for i in ['%(builddir)s/makefile', '%(builddir)s/x2p/makefile']:
                # Ugh, missing some command?
                self.file_sub([('^0$','')], i)
