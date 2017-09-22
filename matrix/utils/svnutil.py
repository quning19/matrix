import sh
import common_utils
import tempfile
import xml.etree.ElementTree as ET
import os
import sys

logger = common_utils.getLogger()

def get_current_version_use_pip(src_path):
    from pip.vcs.subversion import Subversion
    svn = Subversion()
    rev = svn.get_revision(src_path)
    return rev


def get_current_version(path):
    _, tmp = tempfile.mkstemp()
    sh.svn('info', '--xml', path, _out=tmp)
    tree = ET.parse(tmp)
    os.remove(tmp)
    root = tree.getroot()
    current_revision = root.find('entry').get('revision')
    return int(current_revision)


def update(path, revision=None):
    version = get_current_version(path)
    logger.info('svn update [{path}] current_version = [{version}]' \
                .format(path=path, version=version))

    if revision == None:
        sh.svn('update', '--no-auth-cache', '--non-interactive', path, _out=sys.stdout, _err=sys.stdout)
    else:
        sh.svn('update', '--no-auth-cache', '--non-interactive', '-r', revision, path, _out=sys.stdout, _err=sys.stdout)

    current_version = get_current_version(path)

    logger.info('svn update finish [{path}] current_version = [{version}]' \
                .format(path=path, version=get_current_version(path)))
    return version != current_version


def export_folder(source_url, revision, target_path, username, password):
    svn = sh.Command('/usr/bin/svn')
    svn('export', '--force', '--no-auth-cache', '--non-interactive',
        '--username', username, '--password', password,
        '-r', revision, source_url + '@' + revision, target_path,
        _out=sys.stdout.buffer, _err=sys.stderr.buffer)
