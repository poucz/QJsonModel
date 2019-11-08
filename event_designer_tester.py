from qjsonmodel import *


from PySide2.QtWidgets import *
import copy


class MYJsonModel(QJsonModel):
    def find_type(self,index,atribut="Typ"):
        item=index.internalPointer()
        for i in range(0,item.childCount()):
            if item.child(i).key == atribut:
                typ=item.child(i).value
                return typ

    def data(self, index, role):
        level=self.get_item_level(index)
        if role == QtCore.Qt.DecorationRole:
            if index.column()==0:
                typ=self.find_type(index)
                if typ=="db_set":
                    return QtGui.QColor(0,255,255);
                if typ=="set":
                    return QtGui.QColor(235,149,10);
                if typ=="test":
                    return QtGui.QColor(130,10,235);

        if role == QtCore.Qt.DisplayRole:
            if index.column() == 1:
                if isinstance(index.internalPointer().parent().type(),list):
                    return self.find_type(index,"Name")

        return super(MYJsonModel,self).data(index,role)

    def dropMimeData(self, data, action, row, column, parent):
        item_src=self._dragFrom.internalPointer()
        item_parent_src=item_src.parent()
        item_parent=parent.internalPointer()

        if action == QtCore.Qt.IgnoreAction:
            return True

        if id(item_parent_src) == id(item_parent): #pokud kopiruju ze stejnych parentu udelam operaci MOVE
            print("DROP: from:"+str(item_parent_src._children.index(item_src))+" to:"+str(row),flush=True)
            if item_parent_src._children.index(item_src)  ==row : #dropnuti na stejne misto!
                return False
            self.beginMoveRows(parent, self._dragFrom.row(), self._dragFrom.row(), parent, row);
            item_parent._children.insert(row,item_parent_src._children.pop(item_parent_src._children.index(item_src)))
            self.endMoveRows()
            return True

        else: #pokud se jedna o jine parenty, potom KOPIRUJ data, ale pouze pokud jsou parenti ze stejneho levelu
            level_src=self.get_item_level(self._dragFrom)
            level=self.get_item_level(parent)
            if level_src == level :
                grand_parent=item_parent.parent()
                self.beginInsertRows(parent.parent(),grand_parent.childCount(),grand_parent.childCount()+1)
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
                val=self.getChoice(items,"Type:")
                print("Pridavam "+val,flush=True)
                super(Event_Tester,self).add_item(type,key="Typ",value=val)
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
                find_type=self.model.find_type(selected_item)
                if find_type=="db_set":
                    menu.addAction(self.tr("Add DB string"),self.input_set_db_set)
                elif find_type=="set":
                    menu.addAction(self.tr("Add property GPS delta"),self.input_set_GPS_delta)
                    menu.addAction(self.tr("Add property GPS valid"),self.input_set_GPS_valid)
                    menu.addAction(self.tr("Add property GPS lat"),self.input_set_GPS_lat)
                    menu.addAction(self.tr("Add property GPS lon"),self.input_set_GPS_lon)
                    menu.addAction(self.tr("Add property Tacho abs"),self.input_set_Tacho_abs)
                    menu.addAction(self.tr("Add property Tacho plus"),self.input_set_Tacho)
                    menu.addAction(self.tr("Add property Door"),self.input_set_Door)
                    menu.addAction(self.tr("Add property Sleep"),self.input_set_Sleep)
                    menu.addAction(self.tr("Add property Variable"),self.input_set_Variable)
                    menu.addAction(self.tr("Add property clean ride log"),self.input_set_Clean_ride_log)
                elif find_type=="test":
                    menu.addAction(self.tr("Add propertyxxxxxxx"),self.input_set_GPS_delta)

                menu.addAction(self.tr("Add property Name"),self.input_set_Name)

        menu.addAction(self.tr("Remove item"),self.remove_item)
        menu.exec_(self.treeView.viewport().mapToGlobal(position))




    def input_set_Name(self):
        val=self.getText("Name of unit:")
        if val is not None:
            self.add_item(type=int,key="Name",value=val,child=True)


#####################UNIT TEST - DB_SET##############################################
    def input_set_db_set(self):
        val=self.getText("DB string:")
        if val is not None:
            self.add_item(type=int,key="Value",value=val,child=True)
#####################UNIT TEST - SET##############################################

    def input_set_GPS_delta(self):
        val=self.getInteger("GPS delta:")
        if val is not None:
            self.add_item(type=int,key="GPS_delta",value=val,child=True)

    def input_set_GPS_valid(self):
        val=self.getBool("GPS valid:")
        if val is not None:
            self.add_item(type=int,key="GPS_valid",value=val,child=True)

    def input_set_GPS_lat(self):
        val=self.getInteger("GPS lat:",0)
        if val is not None:
            self.add_item(type=int,key="GPS_lat",value=val,child=True)

    def input_set_GPS_lon(self):
        val=self.getInteger("GPS lon:",0)
        if val is not None:
            self.add_item(type=int,key="GPS_lon",value=val,child=True)

    def input_set_Tacho_abs(self):
        val=self.getInteger("Tacho_abs:",min=0)
        if val is not None:
            self.add_item(type=int,key="Tacho_abs",value=val,child=True)

    def input_set_Tacho(self):
        val=self.getInteger("Tacho delta:")
        if val is not None:
            self.add_item(type=int,key="Tacho",value=val,child=True)

    def input_set_Door(self):
        val=self.getBool("Door")
        if val is not None:
            self.add_item(type=int,key="Door",value=val,child=True)

    def input_set_Sleep(self):
        val=self.getDouble("Sleep [s] (double):",min=0,max=30)
        if val is not None:
            self.add_item(type=int,key="GPS_delta",value=val,child=True)

    def input_set_Variable(self):
        var_name, var_id,var_val=self.getVariable()
        if var_val is not None:
            selected_index=self.treeView.selectedIndexes()
            if len(selected_index) <= 0:
                raise Exception('Row not selected: '+str(len(selected_index)))
            index=selected_index[0]
            item=index.internalPointer()

            new_item=QJsonTreeItem(item)

            new_item.key="Variable"
            new_item.type=dict

            if var_name != "" :
                new_item.appendChild(self.create_qjson_item(new_item,"name",var_name))
            else:
                new_item.appendChild(self.create_qjson_item(new_item,"id",var_id))
            new_item.appendChild(self.create_qjson_item(new_item,"value",var_val))

            self.model.appendItem2(index,new_item)

    def input_set_Clean_ride_log(self):
        val=self.getBool("Clear ride log:")
        if val is not None:
            self.add_item(type=int,key="Clean_ride_log",value=val,child=True)




#####################UNIT TEST - TEST ##############################################
    def input_test_Variable(self):
        print("Not implement",flush=True)





#####################INPUT FUNCTION##############################################

    def getText(self,prompt_name="text:"):
        text, okPressed = QInputDialog.getText(self, "Get text",prompt_name, QLineEdit.Normal, "")
        if okPressed and text != '':
            return text
        return None

    def getChoice(self,items,prompt_name=""):
        item, okPressed = QInputDialog.getItem(self, "Get item",prompt_name, items, 0, False)
        if okPressed:
            return item
        return None

    def getInteger(self,prompt_name="",min=-9999999,max=99999999):
        i, okPressed = QInputDialog.getInt(self, "Get integer",prompt_name, 0,min,max, 1)
        if okPressed:
            return i
        return None

    def getDouble(self,prompt_name="",min=0,max=999):
        d, okPressed = QInputDialog.getDouble(self, "Get double",prompt_name, 0, min,max , 10)#The last parameter (10) is the number of decimals behind the comma.
        if okPressed:
            return d;
        return None

    def getBool(self,prompt_name=""):
        return self.getInteger(prompt_name,min=0,max=1)

    def getVariable(self):
        dialog=QDialog(self)

        button=QDialogButtonBox(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)

        label1=QLabel("Variable id")
        label2=QLabel("Variable name")
        label3=QLabel("Variable value")

        text_var_id=QtWidgets.QSpinBox()
        text_var_val=QtWidgets.QSpinBox()
        text_var_val.setMinimum(-99999999)
        text_var_val.setMaximum(999999999)
        text_var_name=QtWidgets.QLineEdit()

        layoutVertical = QGridLayout(dialog)
        layoutVertical.addWidget(label1,0,0)
        layoutVertical.addWidget(text_var_id,0,1)
        layoutVertical.addWidget(label2,1,0)
        layoutVertical.addWidget(text_var_name,1,1)
        layoutVertical.addWidget(label3,2,0)
        layoutVertical.addWidget(text_var_val,2,1)

        layoutVertical.addWidget(button,3,1)

        #connect(buttonBox, &QDialogButtonBox::accepted, this, &QDialog::accept);
        #connect(buttonBox, &QDialogButtonBox::rejected, this, &QDialog::reject);
        button.accepted.connect(dialog.accept)
        button.rejected.connect(dialog.reject)


        ret=dialog.exec()
        if ret == QDialog.Accepted:
            print("AKCEPTOVANO",flush=True)
            return text_var_name.text(),text_var_id.value(),text_var_val.value()

        return None

    def create_qjson_item(self,parent,key,value):
        new_item=QJsonTreeItem(parent)
        new_item.key=key
        new_item.value=value
        new_item.type=type(value)
        return new_item



if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = QWidget()

    layout = QtWidgets.QVBoxLayout()
    jsonwidget= Event_Tester();

    layout.addWidget(jsonwidget)
    window.setLayout(layout)
    window.show()
    window.resize(800, 600)
    app.exec_()
