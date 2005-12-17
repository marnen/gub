#!/usr/bin/python

import __main__
import optparse
import os
import re
import string
import sys

sys.path.insert (0, 'specs/')

import cpm
import gub
import framework

class Settings:
	def __init__ (self, arch):
		self.target_gcc_flags = '' 
		self.topdir = os.getcwd ()
		self.downloaddir = self.topdir + '/downloads'
		self.patchdir = self.topdir + '/patches'
		self.build_architecture = gub.read_pipe ('gcc -dumpmachine')[:-1]
		self.specdir = self.topdir + '/specs'
		self.nsisdir = self.topdir + '/nsis'
		self.gtk_version = '2.8'

		self.target_architecture = arch
		self.tool_prefix = arch + '-'
		self.targetdir = self.topdir + '/target/%s' % self.target_architecture

		## Patches are architecture dependent, 
		## so to ensure reproducibility, we unpack for each
		## architecture separately.
		self.allsrcdir = os.path.join (self.targetdir, 'src')
		
		self.builddir = self.targetdir + '/build'
		self.garbagedir = self.targetdir + '/garbage'
		self.statusdir = self.targetdir + '/status'

		## Safe uploads, so that we can rm -rf target/*
		## and still cheaply construct a (partly) system root
		## from .gub packages.
		## self.gub_uploads = self.targetdir + '/uploads/gub'
		self.uploads = self.topdir + '/uploads'
		self.gub_uploads = self.uploads + '/gub'

		# FIXME: rename to target_root?
		self.system_root = self.targetdir + '/system'
		self.installdir = self.targetdir + '/install'
		self.tooldir = self.targetdir + '/tools'

		# INSTALLERS
		self.installer_root = self.targetdir + '/installer'
		##self.installer_uploads = self.targetdir + '/uploads'
		self.installer_uploads = self.uploads
		self.bundle_version = None
		self.bundle_build = None
		self.package_arch = re.sub ('-.*', '', self.build_architecture)

		self.python_version = '2.4'

	def get_substitution_dict (self):
		d = {}
		for (k,v) in self.__dict__.items ():
			if type (v) <> type (''):
				continue

			d[k] = v

		d.update({
			'build_autopackage': self.builddir + '/autopackage',
			})
		
		return d
			
	def create_dirs (self): 
		for a in (
			'downloaddir',
			'garbagedir',
			'gub_uploads',
			'installer_uploads',
			'specdir',
			'allsrcdir',
			'statusdir',
			'system_root',
			'targetdir',
			'tooldir',
			'topdir',
			):
			dir = self.__dict__[a]
			if os.path.isdir (dir):
				continue

			gub.system ('mkdir -p %s' % dir)

def process_package (package):
	gub.log_command (' ** Package: %s\n' % package.name ())
	for stage in ('untar', 'patch', 'configure', 'compile', 'install',
		      'package', 'sysinstall', 'clean'):
        	if not package.is_done (stage):
			gub.log_command (' *** Stage: %s (%s)\n' % (stage, package.name ()))

			## UGH. fixme, need parameterize.
                	if stage == 'untar':
                        	package.untar ()
			elif stage == 'patch':
                        	package.patch ()
			elif stage == 'configure':
                        	package.configure ()
			elif stage == 'compile':
                        	package.compile ()
			elif stage == 'install':
                        	package.install ()
			elif stage == 'package':
                        	package.package ()
			elif stage == 'sysinstall':
                        	package.sysinstall ()
			elif stage == 'clean':
				package.clean ()

			package.set_done (stage)


def build_packages (settings, packages):
	def skip (p):
		# FIXME: next step might be to download/install using
		# system_gpm unless --rebuild is set, or somesuch.
		"""Return true if package P is installed by system_gpm.
		"""
		return p.system_gpm.is_installed (p.name()) \
			   and p.system_gpm.version (p.name ()) \
			   == cpm.string_to_version (p.full_version ())

	for i in packages:
		# skip download for installed package
		if not (skip (i) or settings.offline):
			i.download ()

	d = []
	for i in packages:
		# skip stages for installed package
		if not skip (i):
			if not i.__dict__.has_key ('depends'):
				i.depends = d
			process_package (i)
		d = [i.name ()]

def make_installers (settings, packages):
	print 'make_installers'
	# FIXME: todo separate lilypond-framework, lilypond packages?
	packages = [p for p in packages if not isinstance (p, gub.Cross_package)]

	# set to false for debugging
	install_gubs = True
	if install_gubs:
		gub.system ('rm -rf %(installer_root)s' % settings.__dict__)
		for p in packages:
			gub.log_command (' *** Stage: %s (%s)\n' % ('install_gub', p.name()))
			p.install_gub ()

	for p in framework.get_installers (settings):
		print 'installer: ' + `p`
		gub.log_command (' *** Stage: %s (%s)\n' % ('create', p.name()))
		p.create ()

def get_settings (platform):
	init  = {
		'darwin': 'powerpc-apple-darwin7',
		'mingw': 'i686-mingw32',
		'linux': 'linux'
		}[platform]

	settings = Settings (init)
	settings.platform = platform
	
	if platform == 'darwin':
		settings.target_gcc_flags = '-D__ppc__'
	elif platform == 'mingw':
		settings.target_gcc_flags = '-mwindows -mms-bitfields'
	elif platform == 'linux':
		platform = 'linux'
		settings.target_architecture = settings.build_architecture
		# Use apgcc to avoid using too new GLIBC symbols
		# possibly gcc/g++ -Wl,--as-needed, ld --as-needed has
		# same effect?
		settings.gcc = 'apgcc'
		settings.gxx = 'apg++'
		settings.ld = 'ld --as-needed'
		settings.tool_prefix = ''
		settings.package_arch = 'i386'
		os.environ['CC'] = settings.gcc
		os.environ['CXX'] = settings.gxx
		# FIXME: some libraries, gettext eg, do not build with
		# gcc-4.0.
		os.environ['APBUILD_CC'] = 'gcc-3.4'
		# FIXME: CXX1 for < 3.4 abi, CXX2 for >= 3.4 abi
		# but APBUILD_CXX2 apg++ --version yields 4.0.3 :-(
		os.environ['APBUILD_CXX1'] = 'g++-3.4'
		os.environ['LD'] = settings.ld
	else:
		raise 'unknown platform', platform 
		
	return settings

def do_options ():
	p = optparse.OptionParser (usage="driver.py [options] platform",
				   description="Grand Unified Builder.  Specify --package-version to set build version")
        p.add_option ('-o', '--offline', action = 'store_true',
                      default=None,
                      dest='offline')
	p.add_option ('-V', '--verbose', action='store_true', 
		      dest="verbose")
	p.add_option ('', '--package-version', action='store',
		      dest="package_version")
	p.add_option ('', '--package-build', action='store',
		      dest="package_build")
	p.add_option ('-p', '--platform', action='store',
		      dest="platform",
		      type='choice',
		      default=None,
		      help='select platform',
		      choices=['linux', 'darwin', 'mingw', 'xmingw', 'xmingw-fedora'])
	p.add_option ('-s', '--setting', action='append',
		      dest="settings",
		      type='string',
		      default=[],
		      help='add a variable')

	(opts, commands)  = p.parse_args ()
	if not opts.platform:
		p.print_help()
		sys.exit (2)
	return opts

def main ():
	options = do_options ()
	settings = get_settings (options.platform)
        settings.offline = options.offline

	for o in options.settings:
		(key, val) = tuple (o.split ('='))
		settings.__dict__[key] = val
		
	gub.start_log (settings)
	settings.verbose = options.verbose
	settings.bundle_version = options.package_version
	settings.bundle_build = options.package_build
	settings.create_dirs ()

	os.environ["PATH"] = '%s/%s:%s' % (settings.tooldir, 'bin',
                                           os.environ["PATH"])

	packages = []
	if options.platform == 'darwin':
		import darwintools
		packages += darwintools.get_packages (settings)
	if options.platform.startswith ('mingw'):
		import mingw
		packages += mingw.get_packages (settings)

	packages += framework.get_packages (settings)

	build_packages (settings, packages)
	make_installers (settings, packages)

if __name__ == '__main__':
	main ()
