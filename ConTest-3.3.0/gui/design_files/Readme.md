# Converting design(*.ui) and resource (*.qrc) files to python(*.py) files

**pyuic5.exe** and  **pyrcc5.exe** tools are available in the python installation **scripts** folder. 
**e.g.** C:\LegacyApp\Python\Python39\Scripts. 
if not available then install with command "pip install pyqt5==5.15.1" or execute our [install_pip_user_dependencies.bat](..%2F..%2Finstall_pip_user_dependencies.bat)

# Design(*.ui) files conversion command 

    pyuic5.exe -x D:\mywork\ConTest\gui\design_files\common_gui.ui -o D:\mywork\ConTest\gui\design_files\common_gui.py 
    
# Resource(*.qrc) files conversion command 

    pyrcc5.exe D:\mywork\ConTest\gui\resource.qrc -o D:\mywork\ConTest\gui\resource_rc.py
    
# Import of resource_rc.py file in .py files(from generated *.ui files) 
    By default import of resource_rc.py available in the .py files(generated *.ui files) at the end of the file. These shall be removed and adding at the top as **from gui import resource_rc.py** in the files import area. 
