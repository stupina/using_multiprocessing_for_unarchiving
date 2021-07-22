from zipfile import ZipFile
import os
from argparse import ArgumentParser


def archive_files(dir_name):
    """
    Archive files: one archive for one file.
    It uses for preparing files to test multiprocessing unarchiving.
    """
    for root, _, files in os.walk(dir_name):
        for filename in files:
            path = '{}{}.zip'.format(
                dir_name,
                filename[:-3],
            )
            with ZipFile(path, 'w') as zipObj:
                file_path = os.path.join(root, filename)
                zipObj.write(file_path, filename)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-s', '--source', dest='dir_name', required=True)
    args = parser.parse_args()
    archive_files(args.dir_name)
