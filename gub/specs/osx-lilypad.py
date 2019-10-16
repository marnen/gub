from gub import build

class Osx_lilypad (build.NullBuild):
    pass

class Osx_lilypad__darwin__ppc (build.NullBuild):
    # yes, we really need the old version here
    # later versions were built on OSX 10.7, which doesn't have pcc support
    source = 'http://lilypond.org/downloads/gub-sources/osx-lilypad-universal/osx-lilypad-universal-0.4.tar.gz'

class Osx_lilypad__darwin__x86 (build.NullBuild):
    source = 'http://lilypond.org/downloads/gub-sources/osx-lilypad-universal/osx-lilypad-universal-0.6.3.tar.gz'

class Osx_lilypad__darwin__64 (build.NullBuild):
    source = 'http://lilypond.org/downloads/gub-sources/osx-lilypad-universal/osx-lilypad-universal-0.6.3.tar.gz' # TODO: refactor
