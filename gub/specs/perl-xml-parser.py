from gub import tools

class Perl_xml_parser (tools.CpanBuild):
    source = 'https://cpan.metacpan.org/authors/id/T/TO/TODDR/XML-Parser-2.44.tar.gz'
    dependencies = [
        'expat',
    ]
