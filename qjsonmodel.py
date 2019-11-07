"""Python adaptation of https://github.com/dridk/QJsonModel

Supports Python 2 and 3 with PySide, PySide2, PyQt4 or PyQt5.
Requires https://github.com/mottosso/Qt.py

Usage:
    Use it like you would the C++ version.

    >>> import qjsonmodel
    >>> model = qjsonmodel.QJsonModel()
    >>> model.load({"key": "value"})

Test:
    Run the provided example to sanity check your Python,
    dependencies and Qt binding.

    $ python qjsonmodel.py

Changes:
    This module differs from the C++ version in the following ways.

    1. Setters and getters are replaced by Python properties
    2. Objects are sorted by default, disabled via load(sort=False)
    3. load() takes a Python dictionary as opposed to
       a string or file handle.

        - To load from a string, use built-in `json.loads()`
            >>> import json
            >>> document = json.loads("{'key': 'value'}")
            >>> model.load(document)

        - To load from a file, use `with open(fname)`
              >>> import json
              >>> with open("file.json") as f:
              ...    document = json.load(f)
              ...    model.load(document)

"""

import json

from Qt import QtWidgets, QtCore, __binding__

from PySide2.QtWidgets import QApplication, QPushButton, QWidget
from PySide2.QtGui import Qt


####vymazat
from PySide2 import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
#from Qt import *




JSON_FILE="/home/pou/pyside2_python_qml/QJsonModel/asf.json"




class QJsonTreeItem(object):
    def __init__(self, parent=None):
        self._parent = parent

        self._key = ""
        self._value = ""
        self._type = None
        self._children = list()

    def appendChild(self, item):
        self._children.append(item)

    def child(self, row):
        return self._children[row]

    def parent(self):
        return self._parent

    def childCount(self):
        return len(self._children)

    def row(self):
        return (
            self._parent._children.index(self)
            if self._parent else 0
        )

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        self._key = key

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, typ):
        self._type = typ

    @classmethod
    def load(self, value, parent=None, sort=True):
        rootItem = QJsonTreeItem(parent)
        rootItem.key = "root"

        if isinstance(value, dict):
            items = (
                sorted(value.items())
                if sort else value.items()
            )

            for key, value in items:
                child = self.load(value, rootItem)
                child.key = key
                child.type = type(value)
                rootItem.appendChild(child)

        elif isinstance(value, list):
            for index, value in enumerate(value):
                child = self.load(value, rootItem)
                child.key = str(index)
                child.type = type(value)
                rootItem.appendChild(child)

        else:
            rootItem.value = value
            rootItem.type = type(value)

        return rootItem

    def add_child(self,parent,muj_typ):
        child = QJsonTreeItem(parent)
        child.key = "x"
        child.value=1
        child.type = muj_typ
        parent.appendChild(child)


    def add_item(self,key,value,parent,muj_typ):

        #print("Pridavam, sibling type: "+str(sibling._type)+" value:"+str(sibling._value)+" key:"+str(sibling.key),flush=True)
        #print("Pridavam, parent type: "+str(parent._type)+" value:"+str(parent._value)+" key:"+str(parent.key),flush=True)
        #print("Typ je:"+str(muj_typ))

        child = QJsonTreeItem(parent)
        child.key = key
        child.value=value
        child.type = muj_typ
        parent.appendChild(child)


    def remove_item(self,item):
        parent=item.parent()
        parent._children.remove(item)


class QJsonModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None):
        super(QJsonModel, self).__init__(parent)

        self._rootItem = QJsonTreeItem()
        self._headers = ("key", "value","typ")

    def load(self, document):
        """Load from dictionary

        Arguments:
            document (dict): JSON-compatible dictionary

        """

        assert isinstance(document, (dict, list, tuple)), (
            "`document` must be of dict, list or tuple, "
            "not %s" % type(document)
        )

        self.beginResetModel()

        self._rootItem = QJsonTreeItem.load(document,sort=False)
        self._rootItem.type = type(document)

        self.endResetModel()

        return True

    def json(self, root=None):
        """Serialise model as JSON-compliant dictionary

        Arguments:
            root (QJsonTreeItem, optional): Serialise from here
                defaults to the the top-level item

        Returns:
            model as dict

        """

        root = root or self._rootItem
        return self.genJson(root)

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                if isinstance(item.parent().type(),list):
                    return str(index.row())
                return item.key

            if index.column() == 1:
                return item.value

            if index.column() == 2:
                return str(item.type)

        elif role == QtCore.Qt.EditRole:
            if index.column() == 1:
                return item.value

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            if index.column() == 1:
                item = index.internalPointer()

                if isinstance(item.type(), int):
                    try:
                        item.value=int(value)
                    except ValueError:
                        return False
                else:
                    item.value = str(value)


                if __binding__ in ("PySide", "PyQt4"):
                    self.dataChanged.emit(index, index)
                else:
                    self.dataChanged.emit(index, index, [QtCore.Qt.EditRole])
                return True
            if index.column() ==0 : #editace klice
                item = index.internalPointer()
                if isinstance(item.parent().type(),list): ##tady nemuzu menit kdy, je to index
                    return False
                if not self.validateKey(item,value):
                    return False
                item.key = str(value)
                if __binding__ in ("PySide", "PyQt4"):
                    self.dataChanged.emit(index, index)
                else:
                    self.dataChanged.emit(index, index, [QtCore.Qt.EditRole])
                return True
        return False

    def validateKey(self,item,new_key):
        parent=item.parent()
        for i in range(parent.childCount()):
            if parent.child(i).key == new_key:
                return False
        return True


    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return None

        if orientation == QtCore.Qt.Horizontal:
            return self._headers[section]

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self._rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 3


    def dropMimeData(self, data, action, row, column, parent):
        print("DROPING r:"+str(row)+" c:"+str(column)+" text:"+str(parent.internalPointer().value),flush=True)
        if action == QtCore.Qt.IgnoreAction:
            return True

        return False

    def supportedDropActions(self):
        return Qt.MoveAction;

    def flags(self, index):
        flags = super(QJsonModel, self).flags(index)
        #flags=flags | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
        if index.column() == 1:
            return QtCore.Qt.ItemIsEditable | flags
        elif index.column() == 0:
            return QtCore.Qt.ItemIsEditable | flags
        else:
            return flags

    def genJson(self, item):
        nchild = item.childCount()

        if item.type is dict:
            document = {}
            for i in range(nchild):
                ch = item.child(i)
                document[ch.key] = self.genJson(ch)
            return document

        elif item.type == list:
            document = []
            for i in range(nchild):
                ch = item.child(i)
                document.append(self.genJson(ch))
            return document

        else:
            return item.value

    def appendChild(self,parent):
        self._rootItem.add_child(parent,int)
        self.refresh();

    def appendItem(self,parent,type,key="",value="novy_klic"):
        self._rootItem.add_item(key,value,parent,type)
        self.refresh();


    def removeItem(self,item):
        self.beginRemoveRows(item.parent(),item.row(),item.row()+1)
        self._rootItem.remove_item(item.internalPointer())
        self.endRemoveRows()


    def refresh(self):
        if __binding__ in ("PySide", "PyQt4"):
            self.layoutChanged.emit()
        else:
            self.layoutChanged.emit()
            #self.dataChanged.emit(index, index, [QtCore.Qt.EditRole])

class JsonWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.button = QtWidgets.QPushButton("Save")
        self.treeView = QtWidgets.QTreeView()
        self.model = QJsonModel()
        self.treeView.setModel(self.model)


        ##DRAG and DROP neni implementovano v modelu
        #self.treeView.setDragDropMode(QAbstractItemView.InternalMove);
        #self.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection);
        #self.treeView.setDragEnabled(True);
        #self.treeView.setAcceptDrops(True);
        #self.treeView.setDropIndicatorShown(True);



        header = self.treeView.header()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)


        with open(JSON_FILE) as f:
            document = json.load(f)
            self.model.load(document)

        self.button.clicked.connect(self.Save_to_file)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.treeView)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        #self.treeView.doubleClicked.connect(self.on_doubleClicked)
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.openMenu)


    def Save_to_file(self):
        data=self.model.json()
        print("Saving....",flush=True)
        #print(data,flush=True)
        with open(JSON_FILE, 'w') as f:
            json.dump(data, f)



    @QtCore.Slot("QModelIndex")
    def on_doubleClicked(self, ix):
            #print(ix.data())
            print("Double clicked",flush=True)

    def openMenu(self, position):
        #print("menu:"+str(position),flush=True)

        selected_item = self.treeView.indexAt(position)
        if not selected_item.isValid():
            print("no selected",flush=True)
            return


        selected_type=selected_item.internalPointer().type()

        menu = QMenu()
        menu.addAction(self.tr("Add int"),self.add_int_item)
        menu.addAction(self.tr("Add str"),self.add_str_item)
        menu.addAction(self.tr("Add list"),self.add_list_item)
        menu.addAction(self.tr("Add dict"),self.add_dict_item)
        if isinstance(selected_type,list) or isinstance(selected_type,dict):
            menu.addAction(self.tr("Add child"),self.add_child_item)
        menu.addAction(self.tr("Remove item"),self.remove_item)

        menu.exec_(self.treeView.viewport().mapToGlobal(position))


    def get_item_level(self,model_inex):
        level=0
        parent=model_inex.parent()
        while parent.isValid() :
            parent=parent.parent()
            level=level+1
        return level

    def add_item(self,type,key="",value="",child=False):
        selected_index=self.treeView.selectedIndexes()
        if len(selected_index) <= 0:
            raise Exception('Row not selected')
        item=selected_index[0].internalPointer()
        if child:
            item=item.parent()
        self.model.appendItem(item,type,key,value)


    def remove_item(self):
        selected_index=self.treeView.selectedIndexes()
        if len(selected_index) <= 0:
            raise Exception('Row not selected')
        self.model.removeItem(selected_index[0])


    def add_int_item(self):
        self.add_item(int)

    def add_str_item(self):
        self.add_item(str)

    def add_list_item(self):
        self.add_item(list)

    def add_dict_item(self):
        self.add_item(dict)


    def add_child_int_item(self):
         self.add_item(int,child=True)

    def add_child_str_item(self):
        self.add_item(str,child=True)

    def add_child_list_item(self):
        self.add_item(list,child=True)

    def add_child_dict_item(self):
        self.add_item(dict,child=True)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = QWidget()

    #model.load(document)
    #model.clear()
    #model.load(document)

    # Sanity check
    #assert (
    #    json.dumps(model.json(), sort_keys=True) ==
    #    json.dumps(document, sort_keys=True)
    #)

    layout = QtWidgets.QVBoxLayout()
    jsonwidget= JsonWidget();

    layout.addWidget(jsonwidget)
    window.setLayout(layout)
    window.show()
    window.resize(500, 300)
    app.exec_()
