# headergenerator
A portable multi-language source file header generator.

##Overview

The __headergenerator__ automates the process of source files heading generation for a variety of different languages.

The tool produces headings in the form of cleanly styled block comments at the beginning of a source file, containing the following elements

* File name: the name of the file the header is added to. This is generated automatically.
* Author: name of the author of the file.
* Licence: name of the licence the file is distributed under.
* File description: description of the file as provided by the author.
* Remarks: any other comments the author of the file wishes to make regarding the file. This field is optional.

The __headergenerator__ can insert headings into individual files, but it can also process entire project directory trees recursively,
  finding all the source files corresponding to the language selected and insert headings in them. When adding headings to multiple
  files at the same time, no descriptions or remarks are added.

At the moment, the entry point to the application is a simple, sober tkinter GUI frontend. However, a CLI interface is
scheduled to be added in the near future.

## Languages Supported

* C/C++
* Python
* C#

## Usage Instructions

Execute the *gui-main.py* script. A Tk window will appear.

If you want to generate a heading to a single file, provide the path to such file and fill out
all the fields below. The file description and remarks fields are optional. When you're ready, click on *Generate File Comments*.

Generating headings for an entire project is very similar. Just enter the path to the folder in the appropriate field, fill out
the *Author* field and click on *Generate Project Comments*. If you want to generate headings for a single folder, untick the
*Recurse* checbox. Otherwise, the application will traverse the entirety of the folder provided and its subfolders, finding
source files that correspond to the language you selected and will insert headings in all of them.

## Pending Features

* Command-line interface.
* Interface to other scripts to fully automate the project heading generation process.
* Update existing headers.
* Add header editing form validation.
* More source code comments and type annotations to improve code readability and maintainability.
* Support for the following languages:
	* Java
	* Bash
	* VB.NET
	* Lisp
	* Lua
	* Haskell
	* JavaScript

## Note to Developers

I'm planning on working actively on this project, adding new features, support for more languages, and obviously
addressing any bugs that might be uncovered during the lifetime of the tool.

However, you're more than welcome to fork this project and make pull requests to extend its functionality or add support for your favourite languages.
