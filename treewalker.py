"""
Gets a directory or file path as input and visits each leaf (source file) prepending boilerplate comments to it.
Can be recursive.
"""

import os
import glob
import re
import datetime
from math import ceil

START_KEY = 'start'
FILLER_KEY = 'filler'
END_KEY = 'end'

CPP_NAME = 'C++'
CPP_STYLE = {
    'start': '/*',
    'filler': '*',
    'end': '*/'}
CPP_EXTENSIONS = ( 'cpp', 'cc', 'h', 'c' )

CSHARP_NAME = 'C#'
CSHARP_STYLE = {
    'start': '//',
    'filler' :'*',
    'end': '//'
}
CSHARP_EXTENSIONS = ('cs')

PYTHON_NAME = 'Python'
PYTHON_STYLE = {
    'start': '"""',
    'filler': '"',
    'end': '"""'}
PYTHON_EXTENSIONS = ('py')

JAVA_NAME = 'Java'
JAVA_STYLE = {
    'start': '/*',
    'filler': '*',
    'end': '*/'
}
JAVA_EXTENSIONS = ('java')

LISP_NAME = 'Lisp'
LISP_STYLE = {
    START_KEY: ';;;',
    FILLER_KEY: ';',
    END_KEY: ';;;'
}
LISP_EXTENSIONS = ('lisp', 'cl', 'lsp')

HEADER_DISTINCTIVE = '@' * 3

class Language:
    def __init__(self, name, extensions, style):
        self.name = name
        self.extensions = extensions
        self.style = style

class Heading:
    def __init__(self, author, licence, description='', remarks=''):
        self.author = author
        self.licence = licence
        self.description = description
        self.remarks = remarks

class HeadingGenerator:
    def __init__(self, path: str, language_str: str):
        """
        :param path: path to root of directory to walk through
        """
        self.path = path
        self.language = self.get_language(language_str)

    def get_language(self, language_string: str) -> Language:
        """
        Get language object based on its string representation.
        :param language_string:
        :return: Language object.
        """

        # Switch statement.
        return {
            CPP_NAME: Language(CPP_NAME, CPP_EXTENSIONS, CPP_STYLE),
            PYTHON_NAME: Language(PYTHON_NAME, PYTHON_EXTENSIONS, PYTHON_STYLE),
            CSHARP_NAME: Language(CSHARP_NAME, CSHARP_EXTENSIONS, CSHARP_STYLE),
            JAVA_NAME: Language(JAVA_NAME, JAVA_EXTENSIONS, JAVA_STYLE),
            LISP_NAME: Language(LISP_NAME, LISP_EXTENSIONS, LISP_STYLE)
            .get(language_string, None)
        }

    def prepend_text(self, file, blocks):
        """
        :param file: open stream to file to edit
        :return: nothing
        """
        file_contents = file.read()
        file.seek(0, 0)
        file.write(blocks + file_contents)

    def insert_heading(self, file, heading):
        """
        Inserts a string of text at the beginning of a file formatted as a constant-width block.
        :param file:
        :param heading:
        :return:
        """
        max_columns = 70
        distinctive = self.language.style['start'] + HEADER_DISTINCTIVE + self.language.style['filler'] \
                                                                          * (self.get_filling_amount(HEADER_DISTINCTIVE, max_columns) - 1) + self.language.style['end']
        empty_line = self.get_filling_line(max_columns, ' ')
        filename_line = self.get_block_line(os.path.split(file.name)[1], max_columns, align='centre')
        author_line = self.get_block_line('Author: ' + heading.author, max_columns)
        copyright_line = self.get_block_line('Copyright (C) ' + str(datetime.datetime.now().year), max_columns)
        licence_line = self.get_block_line('Licence: ' + heading.licence, max_columns)
        description_block = self.get_block(heading.description, max_columns)
        remarks_block = self.get_block('Remarks: ' + heading.remarks if heading.remarks else '', max_columns)
        filled_line = self.get_filling_line(max_columns)

        lines =\
            [distinctive, empty_line, filename_line, empty_line, description_block, remarks_block, empty_line, author_line, copyright_line, licence_line, filled_line]
        block = os.linesep.join([line for line in lines if line]) + os.linesep * 2
        self.prepend_text(file, block)

    def get_filling_line(self, width, filler='') -> str:
        filling = filler if filler else self.language.style['filler']
        return self.get_block_line(filling * ceil(width - (len(self.language.style['start']) + len(self.language.style['end']) + 2) / len(filling)), width)

    def get_block(self, text, width, align='left') -> str:
        lines = self.split_string(text, width)
        line_separator = ' ' + self.language.style['end'] + os.linesep + self.language.style['start'] + ' '
        return os.linesep.join([self.get_block_line(ln, width, align) for ln in lines])

    def get_block_line(self, text, width, align='left') -> str:
        """
        :param text:
        :param width:
        :param align: Alignment of the line in the block, 'left', 'centre', 'right'
        :return:
        """
        # FIXME -- Since we calculate the amount of padding to insert as a result of a math.ceiling operation,
        # if the result is odd, we might not get constant-width lines.
        if not text:
            return ''

        line = ''
        filling_amount = self.get_filling_amount(text, width)
        if align == 'left':
            line = self.language.style['start'] + ' {0} '.format(text) + ' ' * filling_amount + self.language.style['end']
        elif align == 'right':
            line = self.language.style['start'] + ' ' * filling_amount + ' {0} '.format(text) + self.language.style['end']
        elif align == 'centre':
            line = self.language.style['start'] + ' ' * ceil((filling_amount / 2)) + ' {0} '.format(text) + ' ' * ceil((filling_amount / 2)) + self.language.style['end']
        return self.adjust_line_width(line, width)

    def split_string(self, text, width) -> list:
        max_txt_size_per_line = width - (len(self.language.style['start']) + len(self.language.style['end']) + 2)

        if len(text) > max_txt_size_per_line:
            # Split text string into multiple list elements and then join them in terms of filler and os.separator.
            # This is done to prevent line overflow and keep the width of the heading block consistent.
            text_lines = []
            endmarker = 0
            while endmarker < (len(text) - 1):
                startmarker = endmarker
                if (endmarker + max_txt_size_per_line) < len(text):
                    endmarker += max_txt_size_per_line
                else:
                    endmarker = len(text) - 1
                text_lines.append(text[startmarker:endmarker])

            # The last line will probably be shorter so pad it to make it the same width as the others.
            text_lines[-1] = text_lines[-1] + ' ' * self.get_filling_amount(text_lines[-1], width)
            return text_lines
        else:
            return [text]

    def adjust_line_width(self, line, width) -> str:
        line_list = list(line)
        if len(line_list) < width:
            # Insert padding characters until the width of the line is consistent with the rest of the block.
            line_list.insert(-(len(self.language.style['end'])), ' ' * (width - len(line_list)))
        elif len(line_list) > width:
            # Locate the slice containing the extra characters and remove them from the line.
            extrapadding_end = len(line_list) - ((len(line_list) - width) + len(self.language.style['end']) + 1)
            extrapadding_start = extrapadding_end - (len(line_list) - width)
            line_list[extrapadding_start:extrapadding_end + 1] = []
        return ''.join(line_list)

    def get_filling_amount(self, text, width) -> int:
        """
        Get amount of padding characters to use to get a line of the provided width.
        :param text:
        :return:
        """
        startlen = len(self.language.style['start'])
        fillinglen = len(self.language.style['filler'])
        endlen = len(self.language.style['end'])
        amount = abs(ceil((width - (startlen + endlen + len(text))) / fillinglen))
        return amount if amount < width else ceil((width - (startlen + endlen)) / fillinglen)

    def has_header(self, filestream) -> bool:
        """
        Check if file has already been processed by this application before (contains a header).
        :return:
        """
        if os.path.getsize(filestream.name) == 0:
            return False

        # The distinctive is @@@ in line 1 of a file, after the
        # file language's comment start tokens (e.g. in C++, /*@@@; in Python, #@@@).
        # If this is present, the file has been
        # processed by this tool.
        line = filestream.readline()
        # We just want to get the first line, which is the one containing the distinctive.
        # But we don't want to retrieve empty lines
        # i.e. the file has been padded at the top (don't know why someone would want to do this
        # but it's good defensive practice).

        # If file is completely empty, add comments and leave.
        while not line.strip():
            line = filestream.readline()
        # return all(map(lambda ln: ln.lstrip().startswith(self.language.style['start'] + HEADER_DISTINCTIVE), lines))
        filestream.seek(0,0)
        return line.lstrip().startswith(self.language.style['start'] + HEADER_DISTINCTIVE)

    def comment_file(self, heading) -> bool:
        if not os.path.isfile(self.path) or self.language.extensions.count(os.path.splitext(self.path)[1][1:]) == 0:
            return False
        with open(self.path, 'r+') as fs:
            if not self.has_header(fs):
                self.insert_heading(fs, heading)
        return True

    def comment_directory(self, heading, recurse=False) -> bool:
        if not os.path.isdir(self.path):
            return False

        # Eliminate file-specific information from the heading
        heading.description = ''
        heading.remarks = ''

        source_file_regex = r'[A-Za-z0-9-_]+\.(' + '|'.join(self.language.extensions) + ')'
        if recurse:
            for (dirname, subdirs, files) in os.walk(self.path):
                # Open the source files for the selected language, filtering out files without an extension.
                for match in [m for m in map(lambda f: re.match(source_file_regex, f), files) if m]:
                    with open(dirname + os.sep + match.string, 'r+') as fs:
                        if not self.has_header(fs):
                            self.insert_heading(fs, heading)
        else:
            # Get all files with matching extensions in the current directory and insert headings in them.
            for ext in self.language.extensions:
                for file in (glob.glob(self.path + os.sep + '*.' + ext)):
                    with open(file, 'r+') as fs:
                        if not self.has_header(fs):
                            self.insert_heading(fs, heading)
        return True