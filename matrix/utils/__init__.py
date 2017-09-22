import os
import sh

walle_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..'))


def humansize(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def make_parent_folder(path):
    dest_dir = os.path.dirname(path)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)


def md5_for_file(filename):
    md5 = sh.Command('/sbin/md5')
    r = md5('-q', filename)
    md5sum = r.stdout.strip()
    if type(md5sum) == bytes:
        md5sum = md5sum.decode("utf-8")
    return md5sum


