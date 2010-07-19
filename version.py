version='1.0'
release=False

import commands, glob, os
def get_version():
    version_string = ''
    if not release:
        status,output = commands.getstatusoutput("hg tip --template '{node|short}'")
        if status != 0:
            pkginfo = os.path.join(glob.glob('*.egg-info')[0],
                                   'PKG-INFO')
            if os.path.exists(pkginfo):
                for line in file(pkginfo):
                    if line.find('Version: ') == 0:
                        version_string = line.strip().split('Version: ')[1].strip()
            if not version_string:
                version_string = '%s-dev' % version
        else:
            version_string += '%s-%s' % (version, output)
    
    return version_string

