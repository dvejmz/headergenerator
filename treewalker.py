"""
Gets a directory path as input and visits each leaf (source file) prepending boilerplate comments to it.
Can be recursive.
"""

import os
import glob
import re
import datetime
from math import ceil

CPP_NAME = 'C++'
CPP_STYLE = {
    'start' : '/*',
    'filler' : '*',
    'end' : '*/'}
CPP_EXTENSIONS = ( 'cpp', 'cc', 'h', 'c' )

CSHARP_NAME = 'C#'
CSHARP_STYLE = {
    'start' : '//',
    'filler' : '*',
    'end' : '//'
}
CSHARP_EXTENSIONS = ('cs')

PYTHON_NAME = 'Python'
PYTHON_STYLE = {
    'start' : '"""',
    'filler' : '"',
    'end' : '"""'}
PYTHON_EXTENSIONS = ('py')

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
    def __init__(self, path, language_str):
        """
        :param path: path to root of directory to walk through
        :return:
        """
        self.path = path
        self.language = self.get_language(language_str)

    def get_language(self, language_string):
        if language_string == CPP_NAME:
            return Language(CPP_NAME, CPP_EXTENSIONS, CPP_STYLE)
        elif language_string == PYTHON_NAME:
            return Language(PYTHON_NAME, PYTHON_EXTENSIONS, PYTHON_STYLE)
        elif language_string == CSHARP_NAME:
            return Language(CSHARP_NAME, CSHARP_EXTENSIONS, CSHARP_STYLE)

    def prepend_text(self, file, blocks):
        """
        :param file: open stream to file to edit
        :return: nothing
        """

        file_contents = file.read()
        file.seek(0, 0)
        file.write(blocks + file_contents)

    def insert_heading(self, file, heading, style):
        """
        Inserts a string of text at the beginning of a file formatted as a constant-width block.
        :param file:
        :param heading:
        :param style:
        :return:
        """
        MAX_COLUMNS = 70
        distinctive = style['start'] + HEADER_DISTINCTIVE + style['filler'] * (self.get_filling_amount(style, HEADER_DISTINCTIVE, MAX_COLUMNS) + 2) + style['end']
        empty_line = self.get_filling_line(style, MAX_COLUMNS, ' ')
        filename_line = self.get_block_line(style, os.path.split(file.name)[1], MAX_COLUMNS, align='centre')
        author_line = self.get_block_line(style, 'Author: ' + heading.author, MAX_COLUMNS)
        copyright_line = self.get_block_line(style, 'Copyright (C) ' + str(datetime.datetime.now().year), MAX_COLUMNS)
        licence_line = self.get_block_line(style, 'Licence: ' + heading.licence, MAX_COLUMNS)
        description_line = self.get_block_line(style, heading.description, MAX_COLUMNS)
        remarks_line = self.get_block_line(style, 'Remarks: ' + heading.remarks, MAX_COLUMNS)
        filled_line = self.get_filling_line(style, MAX_COLUMNS)

        lines =\
            [distinctive, empty_line, filename_line, empty_line, description_line, remarks_line, empty_line, author_line, copyright_line, licence_line, filled_line]
        block = os.linesep.join([line for line in lines if line]) + os.linesep * 2
        self.prepend_text(file, block)

    def get_filling_line(self, style, width, filler=''):
        filling = style['filler']
        if filler:
            filling = filler
        return self.get_block_line(style, filling * ceil(width - (len(style['start']) + len(style['end']))), width)

    def get_block_line(self, style, text, width, align='left'):
        """
        :param style:
        :param text:
        :param width:
        :param align: Alignment of the line in the block, 'left', 'centre', 'right'
        :return:
        """
        # FIXME -- Since we calculate the amount of padding to insert as a result of a math.ceiling operation,
        # if the result is odd, we might not get constant-width lines.
        if not text:
            return ''

        max_txt_size_per_line = width - (len(style['start']) + len(style['end']) + 2)
        formatted_text = text

        # TODO -- Refactor into separate method.
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

            line_separator = ' ' + style['end'] + os.linesep + style['start'] + ' '
            formatted_text = line_separator.join(text_lines)

        filling_amount = self.get_filling_amount(style, formatted_text, width)
        if align == 'left':
            line = style['start'] + ' {0} '.format(formatted_text) + ' ' * filling_amount + style['end']
            #if len(line) < width:
                # Insert width - len(line) whitespaces or filler characters.
                # TODO -- line.insert(-(len(style['end'])), ' ')
            return line
        elif align == 'right':
            return style['start'] + ' ' * filling_amount + ' {0} '.format(formatted_text) + style['end']
        elif align == 'centre':
            return style['start'] + ' ' * ceil((filling_amount / 2)) + ' {0} '.format(formatted_text) + ' ' * ceil((filling_amount / 2)) + style['end']

    def get_filling_amount(self, style, text, width):
        """
        Get amount of padding characters to use to get a line of the provided width.
        :param style:
        :param text:
        :return:
        """
        startlen = len(style['start'])
        fillinglen = len(style['filler'])
        endlen = len(style['end'])
        return ceil((width - (startlen + endlen + len(text))) / fillinglen)

    def sign_files(self, files, parent_dir):
        for file in files:
            with open(parent_dir + os.sep + file, 'r+') as fs:
                self.insert_heading(fs, self.language.style)

    def has_header(self, filestream, style):
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
        #return all(map(lambda ln: ln.lstrip().startswith(style['start'] + HEADER_DISTINCTIVE), lines))
        return line.lstrip().startswith(style['start'] + HEADER_DISTINCTIVE)

    def comment_file(self, heading):
        if not os.path.isfile(self.path) or self.language.extensions.count(os.path.splitext(self.path)[1][1:]) == 0:
            return False
        with open(self.path, 'r+') as fs:
            if not self.has_header(fs, self.language.style):
                self.insert_heading(fs, heading, self.language.style)
        return True

    def comment_directory(self, heading, recurse=False):
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
                        if not self.has_header(fs, self.language.style):
                            self.insert_heading(fs, heading, self.language.style)
        else:
            # Get all files with matching extensions in the current directory and insert headings in them.
            for ext in self.language.extensions:
                for file in (glob.glob(self.path + os.sep + '*.' + ext)):
                    with open(file, 'r+') as fs:
                        if not self.has_header(fs, self.language.style):
                            self.insert_heading(fs, heading, self.language.style)
        return True