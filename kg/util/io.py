import os
import glob
import ntpath
import logging
from pathlib import Path, PurePath


def drop_file(path: str):
    if os.path.isfile(path):
        os.remove(path)


def file_drop_ext(file_name: str) -> str:
    return file_split_name_ext(file_name)[0]


def file_split_name_ext(file_name: str) -> (str, str):
    v = os.path.splitext(file_name)
    return v[0], v[1]


def to_file(txt: str, path: str):
    with open(path, 'w+') as file:
        file.write(txt)


def get_file_name_from_path(path) -> str:
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def slash(path):
    """
    Will add the trailing slash if it's not already there.
    :param path: path file name
    :return: slashed path file name
    """
    return os.path.join(path, '')


def pv(top: str, verbose: bool = True, nl: bool = True):
    if verbose:
        print(top, end='' if not nl else '\n')


def xst_file(path: str) -> bool:
    """
    Checks whether a file or directory exists or not.
    :param path:  the path to the dir or file
    :return: the result of the checking
    """
    return os.path.isdir(path) or os.path.isfile(path)


def get_files(root_dir: str, exclude: [] = None) -> (int, str, str, str):
    """
    Returns lazily and recursively each path file name, the file name, extension and an index number from
    inside the folders of a root folder
    :param root_dir: the initial folder with the directories and files
    :param exclude: list of files or directories to not get into
    :return: file absolute path, file name, extension, and its index number
    """
    exclude = [] if not exclude else exclude
    i: int = 0
    xst_file(root_dir)
    # For every file in the directory structure
    for path in glob.iglob(root_dir + '**/**', recursive=True):
        xpath = PurePath(path)
        if xpath.name not in exclude:
            if os.path.isfile(path) and Path(path).suffix:
                i += 1
                name, ext = file_split_name_ext(get_file_name_from_path(path))
                yield i, path, name, ext
