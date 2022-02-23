import os
import shutil
import tempfile
import sh
import common_utils
import sys

logger = common_utils.getLogger()

def git_export(src_path, tag, dest_path):
    cwd = os.getcwd()
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)

    temp_path = tempfile.mkdtemp()

    sh.cd(src_path)
    git = sh.Command('/usr/bin/git')
    git('clean', '-f', '-x', '-d')
    git('fetch')
    git('fetch','-t')
    # sh.git('checkout', vms_tag)
    sh.tar(git('archive', tag), '-x', '-C', temp_path)
    sh.touch(os.path.join(temp_path, '.walle_checkout'))
    os.rename(temp_path, dest_path)
    sh.cd(cwd)

def git_update(path):
    sh.cd(path)
 
    def set_origin_head(line):
        global origin_head
        origin_head = line.strip()

    sh.git('rev-parse', '--short', 'HEAD', _out = set_origin_head, _err=sys.stdout)

    logger.info('git pull [{path}]'.format(path=path))
    ret = sh.git('pull', _out=sys.stdout, _err=sys.stdout)

    def set_current_head(line):
        global current_head
        current_head = line.strip()

    sh.git('rev-parse', '--short', 'HEAD', _out = set_current_head, _err=sys.stdout)

    return origin_head != current_head

def git_get_tags(src_path):
    git = sh.Command('/usr/bin/git')
    cwd = os.getcwd()
    sh.cd(src_path)
    ret = git('for-each-ref',
              '--sort', '*authordate',
              '--format', '%(tag),%(*authordate:iso8601)',
              'refs/tags')
    lines = ret.stdout.decode('utf8')

    tags = {}
    for line in lines.split('\n'):
        if line.find(',') == -1:
            continue
        tag, create_time = line.split(",")
        if len(tag) == 0 or len(create_time) == 0:
            continue
        tags[tag] = create_time
    sh.cd(cwd)
    return tags
