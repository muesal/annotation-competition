import click
import hashlib
import os
from acomp import app, db
from acomp.models import Image

BUF_SIZE = 65536  # 64KB


@app.cli.command("prefill")
@click.argument("dirname")
def prefill(dirname):
    target_dir = os.path.join(app.root_path, app.config['ACOMP_OBJ_DIR'])
    if not os.path.isdir(target_dir):
        app.logger.warning('Directory %s does not exist, creating now', target_dir)
        os.makedirs(target_dir)
    app.logger.debug('Scanning %s for files', dirname)
    for filename in os.listdir(dirname):
        path = os.path.abspath(os.path.join(dirname, filename))
        if not os.path.isfile(path):
            app.logger.warning('Skipping %s: not a file', path)
            continue
        try:
            new_ext = normalize_fileext(filename)
            new_name = calc_checksum(path)
            new_filename = new_name + new_ext
        except ValueError as err:
            app.logger.warning('Skipping file %s: %s', filename, str(err))
            continue
        try:
            os.link(path, os.path.join(target_dir, new_filename))
            new_image = Image(new_filename)
            db.session.add(new_image)
        except FileExistsError:
            app.logger.warning('Skipping file %s: Duplicate of %s', filename, new_filename)
            continue
        else:
            db.session.commit()


def calc_checksum(path) -> str:
    checksum = hashlib.sha3_256()
    with open(path, 'rb') as filereader:
        while True:
            data = filereader.read(BUF_SIZE)
            if not data:
                break
            checksum.update(data)

    checksum.update(app.secret_key.encode('utf-8'))
    return checksum.hexdigest().lower()


def normalize_fileext(filename) -> str:
    (name, ext) = os.path.splitext(filename)
    if not name:
        raise ValueError('Missing name before file extension')
    ext = ext.lower()
    if ext == '.jpeg':
        ext = '.jpg'
    if not any(ext in s for s in app.config['ACOMP_ALLOWED_FILE_EXT']):
        raise ValueError('File extension is not in the list of ' +
                'ACOMP_ALLOWED_FILE_EXT')
    return ext
