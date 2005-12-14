import os
import re

import gub

# FIXME: Want to share package_dict () and system () with gub.Package,
# add yet another base class?



class Installer (gub.Package):
	def __init__ (self, settings):
		gub.Package.__init__ (self, settings)
		self.version = settings.bundle_version
		self.strip_command = self.settings.target_architecture + "-strip"
		
        def name (self):
		return 'lilypond'


	def strip_unnecessary_files (self):
		"Remove unnecessary cruft."
	
		for i in (
			'bin/*-config',
			'bin/*gettext*',
			'bin/[cd]jpeg',
			'bin/envsubst*',
			'bin/glib-genmarshal*',
			'bin/gobject-query*',
			'bin/gspawn-win32-helper*',
			'bin/gspawn-win32-helper-console*',
			'bin/msg*',
			'bin/pango-querymodules*',
			'bin/python*',
			'bin/python2.4*',
			'bin/xmlwf',
			'doc'
			'include',
			'include',
			'info',
			'lib/gettext',
			'lib/gettext/hostname*',
			'lib/gettext/urlget*',
			'lib/pkgconfig',
			'lib/*~',
			'lib/*.la',
			'lib/*.a',
			'lib/python2.4/distutils/command/wininst-6*',
			'lib/python2.4/distutils/command/wininst-7.1*',
			'man',
			'share/doc',
			'share/gettext/intl',
			'share/ghostscript/8.15/Resource/',
			'share/ghostscript/8.15/doc/',
			'share/ghostscript/8.15/examples',
			'share/gs/8.15/Resource/',
			'share/gs/8.15/doc/',
			'share/gs/8.15/examples',
			'share/gtk-doc',
			'share/info',
			'share/man',
			'share/omf',
		):
			self.system ('cd %(installer_root)s && rm -rf %(i)s usr/%(i)s', locals ())

		# prune harder
		for i in (
			 'lib/python2.4/bsddb',
			 'lib/python2.4/compiler',
			 'lib/python2.4/curses',
			 'lib/python2.4/distutils',
			 'lib/python2.4/email',
			 'lib/python2.4/hotshot',
			 'lib/python2.4/idlelib',
			 'lib/python2.4/lib-old',
			 'lib/python2.4/lib-tk',
			 'lib/python2.4/logging',
			 'lib/python2.4/test',
			 'lib/python2.4/xml',
			 'share/lilypond/*/make',
			 'share/gettext',
			 'usr/share/aclocal',
			 'share/lilypond/*/python',
			 'share/lilypond/*/tex',
			 'share/lilypond/*/vim',
			 'share/lilypond/*/python',
			 'share/lilypond/*/fonts/source',
			 'share/lilypond/*/fonts/svg',
			 'share/lilypond/*/fonts/tfm',
			 'share/locale',
			 'share/omf',
			 'share/gs/fonts/[a-bd-z]*',
			 'share/gs/fonts/c[^0][^9][^5]*',
			 'share/gs/Resource',
			 ):
			self.system ('cd %(installer_root)s && rm -rf %(i)s' , locals ())

	def strip_binary_file (self, file):
		self.system ('%(strip_command)s %(file)s', locals (), ignore_error = True)

	def strip_binary_dir (self, dir):
		(root, dirs, files) = os.walk(dir).next ()
		for f in files:
			self.strip_binary_file (root + '/' + f)
			
	def strip (self):
		self.strip_unnecessary_files ()
		self.strip_binary_dir (self.settings.installer_root + '/usr/lib')
		self.strip_binary_dir (self.settings.installer_root + '/usr/bin')

		
	def create (self):
		self.strip ()
		
class Darwin_bundle (Installer):
	def rewire_mach_o_object (self, name):
		lib_str = self.read_pipe ("%(target_architecture)s-otool -L %(name)s", locals(), ignore_error=True)

		changes = ''
		for l in lib_str.split ('\n'):
			m = re.search ("\s+(/usr/lib/.*) \(.*\)", l)
			if not m:
				continue
			libpath = m.group (1)
			if self.ignore_libs.has_key (libpath):
				continue
			
			newpath = re.sub ('/usr/lib', '@executable_path/../lib/', libpath); 
			changes += (' -change %s %s ' % (libpath, newpath))
			
		if changes:
			self.system ("%(target_architecture)s-install_name_tool %(changes)s %(name)s ",
				     locals(), ignore_error=True)

class Nsis (Installer):
	def __init__ (self, settings):
		Installer.__init__ (self, settings)
		self.strip_command += ' -g '
		
	def create (self):
		Installer.create (self)
		
		# FIXME: build in separate nsis dir, copy or use symlink
		installer = os.path.basename (self.settings.installer_root)
		build = self.settings.build
		self.file_sub ([
			('@GUILE_VERSION@', '%(guile_version)s'),
			('@LILYPOND_BUILD@', '%(build)s'),
			('@LILYPOND_VERSION@', '%(bundle_version)s'),
			('@PYTHON_VERSION@', '%(python_version)s'),
			('@ROOT@', '%(installer)s'),
			],
			       '%(nsisdir)s/lilypond.nsi.in',
#			       to_name='%(targetdir)s/lilypond.nsi',
			       to_name='%(targetdir)s/lilypond.nsi',
			       env=locals ())
		# FIXME: move nsis cruft to nsis dir
		self.system ('cp %(nsisdir)s/*.nsh %(targetdir)s')
		self.system ('cp %(nsisdir)s/*.scm.in %(targetdir)s')
		self.system ('cp %(nsisdir)s/*.sh.in %(targetdir)s')
		self.system ('cd %(targetdir)s && makensis lilypond.nsi')
#		self.system ('cd %(targetdir)s && makensis -NOCD %(nsisdir)/lilypond.nsi')
		self.system ('mv %(targetdir)s/setup.exe %(installer_uploads)s/lilypond-%(version)s-%(build)s.exe', locals ())

class Linux_installer (Installer):
	def __init__ (self, settings):
		Installer.__init__ (self, settings)
		self.strip_command += ' -g '
		


class Tgz (Linux_installer):
	def create (self):
		build = self.settings.build
		self.system ('tar -C %(installer_root)s -zcf %(installer_uploads)s/%(name)s-%(version)s-%(package_arch)s-%(build)s.tgz .', locals ())

class Deb (Linux_installer):
	def create (self):
		build = self.settings.build
		self.system ('cd %(installer_uploads)s && fakeroot alien --keep-version --to-deb %(installer_uploads)s/%(name)s-%(version)s-%(package_arch)s-%(build)s.tgz', locals ())

class Rpm (Linux_installer):
	def create (self):
		build = self.settings.build
		self.system ('cd %(installer_uploads)s && fakeroot alien --keep-version --to-rpm %(installer_uploads)s/%(name)s-%(version)s-%(package_arch)s-%(build)s.tgz', locals ())


class Autopackage (Linux_installer):
	def create (self):
		self.system ('rm -rf %(build_autopackage)s')
		self.system ('mkdir -p %(build_autopackage)s/autopackage')
		self.file_sub ([('@VERSION@', '%(version)s')],
			       '%(specdir)s/lilypond.apspec.in',
			       to_name='%(build_autopackage)s/autopackage/default.apspec')
		# FIXME: just use symlink?
		self.system ('tar -C %(installer_root)s/usr -cf- . | tar -C %(build_autopackage)s -xvf-')
		self.system ('cd %(build_autopackage)s && makeinstaller')
		self.system ('mv %(build_autopackage)s/*.package %(installer_uploads)s')


