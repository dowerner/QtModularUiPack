# QtModularUiPack
A module for quick and easy creation of PyQt5 applications. Creating sophisticated and versatile user interfaces is a task which often involves a lot of effort. While in science and engineering there is often a lack of resources to invest in the development of user interface applications.
This Python module aims to provide a very simple way of creating scale-able user interface applications. The module is based on the popular PyQt5 framework which is a Python wrapper based on the C++ library Qt5 (https://pypi.org/project/PyQt5/).

## Installation
To install the module you can use the pip package installer for Python. Type the following command on the command line of your operating system:

```console
pip install QtModularUiPack
```

## First Steps
To check if the module is working properly open a python command prompt and type the following commands:

```python
from QtModularUiPack.Widgets import ModularApplication
ModularApplication.standalone_application(title='MyApp', window_size=(640, 480))
```
This should produce a Qt user interface window with the title "MyApp" and the given size.

![modular_application](https://github.com/dowerner/QtModularUiPack/blob/master/doc/images/modular_application.png)

This empty window has a single button containing three dots. Clicking this button reveals a drop-down menu. Choose "View->Tool Command Line", this will change the window to a fully functional Python command prompt (ToolCommandFrame-widget).

![console_test](https://github.com/dowerner/QtModularUiPack/blob/master/doc/images/modular_application_console_test.png)

The real power of the ModularApplication-widget lies in its ability to be subdivided and display different widgets simultaneously. To illustrate this again click the menu and then choose "split horizontally".

![split](https://github.com/dowerner/QtModularUiPack/blob/master/doc/images/modular_application_split.png)

This will split the window and shows a new empty frame. In the new window choose "View->Hello World Frame". This will open the HelloWorldFrame-widget.

![hello_world_widget](https://github.com/dowerner/QtModularUiPack/blob/master/doc/images/modular_application_hello_world.png)

Some of the widgets in this module have the ability to access and change data in other widgets. One example of this is the ToolCommandFrame-widget on the left side of the window. Type the following in the command part of the widget:
```python
tools.help()
```
This should show two items: console, hello_world. Both entries represent one found data-context in the ModularApplication-widget. The first entry "console" is the variable containing the data-context of the ToolCommandFrame-widget and "hello_world" contains the data-context of the HelloWorldFrame-widget. To access the HelloWorldFrame-widget type the following in the console:
```python
tools.hello_world.switch()
```
Where "switch()" is a function provided by the data-context of the HelloWorldFrame-widget. Notice how the upper and lower text fields have swapped their contents.

![hello_world_switch](https://github.com/dowerner/QtModularUiPack/blob/master/doc/images/modular_application_hello_world_switch.png)

This simple example serves to illustrate how modular applications can greatly simplify the communication between independent parts of an application. Lab automation which is a common subject in experimental science, this can be utilized to control mandy different devices while keeping the code for each device completely seperate. The ModularApplication-widget handles adding and removal of other widgets dynamically and notifies so called "context-aware" widgets about changes.

## Advanced Topics
