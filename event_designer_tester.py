from qjsonmodel import *


from PySide2.QtWidgets import *
import copy


class MYJsonModel(QJsonModel):

    def dropMimeData(self, data, action, row, column, parent):
        item_src=parent_test=self._dragFrom.internalPointer()
        item_parent_src=item_src.parent()
        item_parent=parent.internalPointer()


        if action == QtCore.Qt.IgnoreAction:
            return True

        if id(item_parent_src) == id(item_parent): #pokud kopiruju ze stejnych parentu udelam operaci MOVE
            print("DROP: from:"+str(item_parent_src._children.index(item_src))+" to:"+str(row),flush=True)
            self.beginMoveRows(parent, self._dragFrom.row(), self._dragFrom.row(), parent, row);
            item_parent._children.insert(row,item_parent_src._children.pop(item_parent_src._children.index(item_src)))
            self.endMoveRows()
            return True

        else: #pokud se jedna o jine parenty, potom KOPIRUJ data, ale pouze pokud jsou parenti ze stejneho levelu
            level_src=self.get_item_level(self._dragFrom)
            level=self.get_item_level(parent)
            print("Level :"+str(level_src)+" do levelu:"+str(level),flush=True)

            if level_src == level:
                self.beginInsertRows(parent,parent.row(),parent.row()+1)
                grand_parent=item_parent.parent()
                clone=copy.deepcopy(item_src)
                clone._parent=grand_parent
                grand_parent.appendChild(clone)
                self.endInsertRows()
                return True

        return False


class Event_Tester(JsonWidget):

    def __init__(self):
        super(Event_Tester,self).__init__()
        self.test_btn = QtWidgets.QPushButton("test")
        self.layout.addWidget(self.test_btn)


        self.treeView.expandAll()


    def Init_data_model(self):
        return MYJsonModel()




    def add_item(self,type,key="",value="",child=False):
        selected_index=self.treeView.selectedIndexes()
        if len(selected_index) <= 0:
            raise Exception('Row not selected: '+str(len(selected_index)))

        level=self.model.get_item_level(selected_index[0])
        item=selected_index[0].internalPointer()


        if level==0:
            if type != list:
                print("v levelu "+str(level)+" muzu pridat pouzel list nikoliv "+str(type),flush=True)
                return
            else:
                key=self.getText()
                print("Pridavam "+key,flush=True)
                super(Event_Tester,self).add_item(type,key=key)


        #LEVEL 2 je pouze DICT -seznam prikazu pro test (pridavam potomkovi takze oznacen mam parent (to jelevel 1-) > se prida do levelu 2)
        if level==1:
            if type != dict:
                print("v levelu "+str(level)+" muzu pridat pouzel dict nikoliv "+str(type),flush=True)
                return
            else:
                super(Event_Tester,self).add_item(type)


        #LEVEL 3 jsou testy - typ testu je povinny parametr
        if level==2:
            if item.childCount() == 0:
                items = ("set","db_set","test")
                val=self.getChoice(items,"type")
                print("Pridavam "+val,flush=True)
                super(Event_Tester,self).add_item(type,key="typ",value=val)
            else:
                super(Event_Tester,self).add_item(type,key=key,value=value)

        print("addd at level:"+str(level),flush=True)


    def openMenu(self, position):
        #print("menu:"+str(position),flush=True)

        selected_item = self.treeView.indexAt(position)
        if not selected_item.isValid():
            print("no selected",flush=True)
            return


        selected_type=selected_item.internalPointer().type()
        level=self.model.get_item_level(selected_item)
        item=selected_item.internalPointer()


        menu = QMenu()

        if level==0:
           menu.addAction(self.tr("Add new test"),self.add_child_list_item)


        if level==1:
           menu.addAction(self.tr("Add tests unit"),self.add_child_dict_item)




        if level==2:
            if item.childCount() == 0:
                menu.addAction(self.tr("Add new type"),self.add_child_str_item)
            else:
                typ=""
                for i in range(0,item.childCount()):
                    if item.child(i).key == "typ":
                        typ=item.child(i).value
                if typ=="db_set":
                    menu.addAction(self.tr("Add DB string"),self.input_set_db_set)
                elif typ=="set":
                    menu.addAction(self.tr("Add property GPS delta"),self.input_set_GPS_delta)
                    menu.addAction(self.tr("Add property GPS valid"),self.input_set_GPS_valid)
                    menu.addAction(self.tr("Add property Tacho abs"),self.input_set_Tacho_abs)
                    menu.addAction(self.tr("Add property Tacho plus"),self.input_set_Tacho)
                    menu.addAction(self.tr("Add property Door"),self.input_set_Door)
                    menu.addAction(self.tr("Add property Sleep"),self.input_set_Sleep)
                    menu.addAction(self.tr("Add property Variable"),self.input_set_Variable)
                elif typ=="test":
                    menu.addAction(self.tr("Add propertyxxxxxxx"),self.input_set_GPS_delta)


        menu.addAction(self.tr("Remove item"),self.remove_item)
        menu.exec_(self.treeView.viewport().mapToGlobal(position))



#####################UNIT TEST - DB_SET##############################################
    def input_set_db_set(self):
        val=self.getText("DB string:")
        self.add_item(type=int,key="Value",value=val,child=True)
#####################UNIT TEST - SET##############################################

    def input_set_GPS_delta(self):
        val=self.getInteger("GPS delta:")
        self.add_item(type=int,key="GPS_delta",value=val,child=True)

    def input_set_GPS_valid(self):
        val=self.getBool("GPS valid:")
        self.add_item(type=int,key="GPS_valid",value=val,child=True)

    def input_set_Tacho_abs(self):
        val=self.getInteger("Tacho_abs:",min=0)
        self.add_item(type=int,key="Tacho_abs",value=val,child=True)

    def input_set_Tacho(self):
        val=self.getInteger("Tacho delta:")
        self.add_item(type=int,key="Tacho",value=val,child=True)

    def input_set_Door(self):
        val=self.getBool("Door")
        self.add_item(type=int,key="Door",value=val,child=True)

    def input_set_Sleep(self):
        val=self.getDouble("Sleep [s] (double):",min=0,max=30)
        self.add_item(type=int,key="GPS_delta",value=val,child=True)

    def input_set_Variable(self):
        val=self.getInteger("NOT JET IMPLEMENT:",min=0,max=1)
        self.add_item(type=int,key="GPS_delta",value=val,child=True)



#####################UNIT TEST - TEST ##############################################
    def input_test_Variable(self):
        print("Not implement",flush=True)





#####################INPUT FUNCTION##############################################

    def getText(self,prompt_name="text:"):
        text, okPressed = QInputDialog.getText(self, "Get text",prompt_name, QLineEdit.Normal, "")
        if okPressed and text != '':
            return text
        return ""

    def getChoice(self,items,prompt_name=""):
        item, okPressed = QInputDialog.getItem(self, "Get item",prompt_name, items, 0, False)
        return item

    def getInteger(self,prompt_name="",min=-9999999,max=99999999):
        i, okPressed = QInputDialog.getInt(self, "Get integer",prompt_name, 0,min,max, 1)
        if okPressed:
            return i
        return 0

    def getDouble(self,prompt_name="",min=0,max=999):
        d, okPressed = QInputDialog.getDouble(self, "Get double",prompt_name, 0, min,max , 10)#The last parameter (10) is the number of decimals behind the comma.
        if okPressed:
            return d;
        return 0

    def getBool(self,prompt_name=""):
        return self.getInteger(prompt_name,min=0,max=1)


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
