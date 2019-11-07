from qjsonmodel import *


from PySide2.QtWidgets import *



class Event_Tester(JsonWidget):

    def __init__(self):
        super(Event_Tester,self).__init__()
        self.test_btn = QtWidgets.QPushButton("test")
        self.layout.addWidget(self.test_btn)




    def add_item(self,type):
        selected_index=self.treeView.selectedIndexes()
        if len(selected_index) <= 0:
            raise Exception('Row not selected: '+str(len(selected_index)))

        level=self.get_item_level(selected_index[0])
        item=selected_index[0].internalPointer()


        #level 0 musí byt vzdy tests
        if level == 0 :
            return


        #LEVEL 1 je pouze LIST -seznam testu
        if level==1:
            if type != list:
                print("v levelu "+str(level)+" muzu pridat pouzel list nikoliv "+str(type),flush=True)
                return
            else:
                key=self.getText()
                print("Pridavam "+key,flush=True)
                super(Event_Tester,self).add_item(type,key=key)




        #LEVEL 2 je pouze DICT -seznam prikazu pro test
        if level==2:
            if type != dict:
                print("v levelu "+str(level)+" muzu pridat pouzel dict nikoliv "+str(type),flush=True)
                return
            else:
                super(Event_Tester,self).add_item(type)


        #LEVEL 3 jsou testy - typ testu je povinny parametr
        if level==3:
            items = ("set","dbset","test")
            val=self.getChoice(items,"type")
            print("Pridavam "+val,flush=True)
            super(Event_Tester,self).add_item(type,key="typ",value=val)



        print("addd at level:"+str(level),flush=True)


    def openMenu(self, position):
       #print("menu:"+str(position),flush=True)

       selected_item = self.treeView.indexAt(position)
       if not selected_item.isValid():
           print("no selected",flush=True)
           return


       selected_type=selected_item.internalPointer().type()
       level=self.get_item_level(selected_item)


       menu = QMenu()

       if level==0:
           return

       if level==1:
           menu.addAction(self.tr("Add new test"),self.add_list_item)
           menu.addAction(self.tr("Add tests unit"),self.add_child_item)

       if level==2:
           menu.addAction(self.tr("Add dict"),self.add_dict_item)
           menu.addAction(self.tr("Add child"),self.add_child_item)


       if level==3:
           menu.addAction(self.tr("Add int"),self.add_int_item)
           menu.addAction(self.tr("Add str"),self.add_str_item)
           menu.addAction(self.tr("Add list"),self.add_list_item)
           menu.addAction(self.tr("Add dict"),self.add_dict_item)
           if isinstance(selected_type,list) or isinstance(selected_type,dict):
               menu.addAction(self.tr("Add child"),self.add_child_item)


       menu.addAction(self.tr("Remove item"),self.remove_item)

       menu.exec_(self.treeView.viewport().mapToGlobal(position))


    def getText(self):
        text, okPressed = QInputDialog.getText(self, "Get text","Your name:", QLineEdit.Normal, "")
        if okPressed and text != '':
            return text
        return ""

    def getChoice(self,items,prompt_name=""):
        item, okPressed = QInputDialog.getItem(self, "Get item",prompt_name, items, 0, False)
        return item



if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = QWidget()

    layout = QtWidgets.QVBoxLayout()
    jsonwidget= Event_Tester();

    layout.addWidget(jsonwidget)
    window.setLayout(layout)
    window.show()
    window.resize(600, 400)
    app.exec_()
