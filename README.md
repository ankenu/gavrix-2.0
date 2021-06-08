<p align="center">
    <img src="https://github.com/fickmann/gavrix-2.0/blob/main/img/logo.png" width="300"/>
</p>

<p align="center">A full-fledged python text editor with a custom interface, based on tkinter.</p>

## Features
1. Create and edit text files.
2. Customizing the interface (changing the scale, setting the color theme).
3. Implementing search inside the file.
4. The ability to open images.
5. Implementation of opening folders (file explorer).
6. The ability to switch between open files via tabs.
## Interface Appearance
The Gavrix has 3 different windows - the main window, the search window, and the window with information about the development team. The main window has 3 widgets - the main menu on the top, the explorer on the left, and the text field on the right.

![Screenshot of the Gavrix](https://raw.githubusercontent.com/fickmann/gavrix-2.0/main/doc_src/_static/example.png)

## Main Menu
The Gavrix has the following sub-items:
1. Gavrix – a menu for interacting with files and folders.
2. Edit – menu for interactions with the text field.
3. Search – the function of finding the necessary text in the file and then replacing it, if necessary.
4. View – the menu of settings of the external view of the program (selection of the theme and the scale of the text).
5. About – function for displaying a pop-up window with the names of the developers.

## Pop-up Menu
When you right-click on the text field, a pop-up menu appears, whose items copy "Edit" from the main menu.

## Themes
The Gavrix supports user-configurable color schemes, which are stored in a special JSON file. You can customize the topic names, as well as four color fields - background color, text color, line number background color, and line number color.

## Installation Guide
Generating documentation:
```sh
doit docs
```
Localization generation: 
```sh
doit mo
```
Checking for flake8/pydocstyle: 
```sh
flake8 src, pydocstyle src
```
Package installations:
```sh
doit
python3 -m build
```

## Development Team
1. [fickmann](https://github.com/fickmann)
2. [warnachinka](https://github.com/warnachinka)
