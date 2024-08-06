from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import *
from PySide2.QtGui import *
from filemark import Files
import os
import re
import numpy as np

#重定义label，添加点击事件和气泡
class markLabel(QLabel):
    leftclick=Signal(str)
    def __init__(self,parent=None):
        super().__init__(parent)
    
    def mousePressEvent(self,QMouseEvent):
         if QMouseEvent.buttons() == Qt.LeftButton:   ##判断是否鼠标左键点击
             self.leftclick.emit(self.text())

    def enterEvent(self, QMouseEvent):   ##鼠标停留
        self.setToolTip(self.text())

class pictureLabel(QLabel):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        filePathList = e.mimeData().text()
        filePath = filePathList.split('\n')[0] #拖拽多文件只取第一个地址
        filePath = filePath.replace('file:///', '', 1) #去除文件地址前缀的特定字符
        self.setText(filePath)
    
        
class Stats:

    def __init__(self):
        # 从文件中加载UI定义

        # 从 UI 定义中动态 创建一个相应的窗口对象
        
        #初始化各项属性
        qfile_stats=QFile('./mainwindow.ui')
        qfile_stats.open(QFile.ReadOnly)
        qfile_stats.close()
        self.ui = QUiLoader().load(qfile_stats)
        self.item_filename=[]
        self.now_files=[]
        self.now_mark=[]
        self.filters=[]
        self.inters=[]
        self.bulk_filters=[]
        self.bulk_inters=[]
        self.SelectSave=''
        self.SelectDirectory=''
        self.files=None
        self.SelectSave='./savedata.npy'
        # self.ui.text_label.setAcceptDrops(True)
        # self.ui.text_label.dragEnterEvent=self.dragEnterEvent_ui
        # self.ui.text_label.dropEvent=lambda e :self.dropEvent_ui(e)
        #按钮添加icon
        self.addsign_path='./pictures/+.png'
        self.subsign_path='./pictures/-.png'
        self.opensign_path='./pictures/open.png'
        self.sifliesign_path='./pictures/singlefile.png'
        self.datafile_path='./pictures/datafile.png'
        self.ui.setWindowIcon(QIcon("./pictures/title.png"))
        self.ui.open_Button.setIcon(QIcon(self.opensign_path))
        self.ui.bulk_Button.setIcon(QIcon(self.datafile_path))
        self.ui.return_Button.setIcon(QIcon(self.sifliesign_path))
        self.ui.addfilter_Button.setIcon(QIcon(self.addsign_path))
        self.ui.add_Button.setIcon(QIcon(self.addsign_path))
        self.ui.bulkadd_Button.setIcon(QIcon(self.addsign_path))
        self.ui.bulk_add_match_Button.setIcon(QIcon(self.addsign_path))
        self.ui.bulk_add_inter_Button.setIcon(QIcon(self.addsign_path))
        self.ui.add_inter_Button.setIcon(QIcon(self.addsign_path))
        self.ui.add_Button.setIcon(QIcon(self.addsign_path))
        self.ui.delfilter_Button.setIcon(QIcon(self.subsign_path))
        self.ui.del_Button.setIcon(QIcon(self.subsign_path))
        self.ui.bulkdel_Button.setIcon(QIcon(self.subsign_path))
        self.ui.bulk_del_match_Button.setIcon(QIcon(self.subsign_path))
        self.ui.bulk_del_inter_Button.setIcon(QIcon(self.subsign_path))
        self.ui.del_inter_Button.setIcon(QIcon(self.subsign_path))
        #第一面顶部layou插入两个初始标题标签
        label=QLabel("匹配标签")
        label.setFont(QFont("Roman times",13,QFont.Bold))
        self.ui.filter_gridLayout.addWidget(label,0,0)
        label1=QLabel("过滤标签")
        label1.setFont(QFont("Roman times",13,QFont.Bold))
        self.ui.inter_gridLayout.addWidget(label1,0,0)
        #第二面两个标题标签设置字体
        self.ui.bulk_matchrule_label.setFont(QFont("Roman times",13,QFont.Bold))
        self.ui.bulk_interrule_label.setFont(QFont("Roman times",13,QFont.Bold))

        #tableview的初始化
        self.ui.bulk_tableView.horizontalHeader().hide()
        self.ui.bulk_tableView.verticalHeader().hide()
        self.ui.bulk_tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableView.horizontalHeader().hide()
        self.ui.tableView.verticalHeader().hide()
        self.ui.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        #设置背景
        pix=QPixmap("./pictures/background.jpg")
        palette=QPalette()
        palette.setBrush(QPalette.Background,QBrush(pix))
        self.ui.setPalette(palette)
        self.ui.setAutoFillBackground(True)

        #设置菜单和菜单动作
        self.ui.SelectDirectory=QAction(self.ui)
        self.ui.SelectDirectory.setCheckable(False)
        self.ui.SelectDirectory.triggered.connect(self.selectdir)
        self.ui.SelectDirectory.setText('选择文件夹')
        self.ui.menubar.addAction(self.ui.SelectDirectory)

        self.ui.save=self.ui.menubar.addMenu('存储文件')
        self.ui.SelectSave=QAction(self.ui)
        self.ui.SelectSave.setCheckable(False)
        self.ui.SelectSave.triggered.connect(self.selectsave)
        self.ui.SelectSave.setText('选择存储文件')
        self.ui.save.addAction(self.ui.SelectSave)        
        self.ui.CreateSave=QAction(self.ui)
        self.ui.CreateSave.setCheckable(False)
        self.ui.CreateSave.triggered.connect(self.createsave)
        self.ui.CreateSave.setText('创建存储文件')
        self.ui.save.addAction(self.ui.CreateSave)      
        self.ui.ClearSave=QAction(self.ui)
        self.ui.ClearSave.setCheckable(False)
        self.ui.ClearSave.triggered.connect(self.clearsave)
        self.ui.ClearSave.setText('清空存储文件')
        self.ui.save.addAction(self.ui.ClearSave)

        self.ui.saveSave=QAction(self.ui)
        self.ui.saveSave.setCheckable(False)
        self.ui.saveSave.triggered.connect(self.save_save)
        self.ui.saveSave.setText('保存存储文件')
        self.ui.save.addAction(self.ui.saveSave)
                
        
        self.ui.refresh=QAction(self.ui)
        self.ui.refresh.setCheckable(False)
        self.ui.refresh.triggered.connect(self.refresh)
        self.ui.refresh.setText('重置')
        self.ui.menubar.addAction(self.ui.refresh)
        self.ui.movefile=QAction(self.ui)
        self.ui.movefile.setCheckable(False)
        self.ui.movefile.triggered.connect(self.movefile)
        self.ui.movefile.setText('移动文件')
        self.ui.menubar.addAction(self.ui.movefile)

        #继承重定义标签，添加点击事件和停留气泡
        self.ui.bulk_path_label=markLabel(self.ui.bulk_path_label)
        #self.ui.text_label=pictureLabel(self.ui.text_label)

        #绑定各项槽和信号
        self.ui.bulk_tableView.clicked.connect(self.bulk_table_left_click)
        self.ui.tableView.clicked.connect(self.table_left_click)
        
        self.ui.add_Button.clicked.connect(self.add_marks)
        self.ui.del_Button.clicked.connect(self.del_marks)
        self.ui.addfilter_Button.clicked.connect(self.add_filter)
        self.ui.delfilter_Button.clicked.connect(self.del_filter)
        self.ui.add_inter_Button.clicked.connect(self.add_inter)
        self.ui.del_inter_Button.clicked.connect(self.del_inter)
        self.ui.open_Button.clicked.connect(self.open_files)
        self.ui.bulk_Button.clicked.connect(self.swtichpage)
        self.ui.return_Button.clicked.connect(self.swtichpage)
        self.ui.bulk_add_match_Button.clicked.connect(self.bulk_add_filter)
        self.ui.bulk_del_match_Button.clicked.connect(self.bulk_del_filter)
        self.ui.bulk_add_inter_Button.clicked.connect(self.bulk_add_inter)
        self.ui.bulk_del_inter_Button.clicked.connect(self.bulk_del_inter)
        self.ui.bulkadd_Button.clicked.connect(self.bulk_addmark)
        self.ui.bulkdel_Button.clicked.connect(self.bulk_delmark)
        self.ui.bulk_path_label.leftclick.connect(self.bulk_getpath)
        self.ui.filter_lineEdit.returnPressed.connect(self.add_filter)
        self.ui.mark_lineEdit.returnPressed.connect(self.add_marks)
        self.ui.bulk_lineEdit.returnPressed.connect(self.bulk_add_filter)
        self.ui.bulkmark_lineEdit.returnPressed.connect(self.bulk_addmark)
    #选择存储文件
    def selectsave(self):
        self.SelectSave = QFileDialog.getOpenFileName(
            self.ui,  # 父窗口对象
            "选择存储文件",  # 标题
            "./",
            "存储文件(*.npy)"
        )
        if self.SelectSave == '':
            return
        self.SelectSave=self.SelectSave[0]
        if self.SelectDirectory != '':
            self.files=Files(self.SelectDirectory,self.SelectSave)
            self.update_nowfiles()
            self.update_tableview()
            self.update_marklayout()

    #保存存储文件
    def save_save(self):
        if self.SelectSave == '':
            return
        if self.files == None:
            return
        np.save(self.SelectSave,self.files.filesmark)

    #清空存储文件
    def clearsave(self):
        self.SelectSave = QFileDialog.getOpenFileName(
            self.ui,  # 父窗口对象
            "选择存储文件",  # 标题
            "./",
            "存储文件(*.npy)"
        )
        if self.SelectSave == '':
            return
        self.SelectSave=self.SelectSave[0]
        np.save(self.SelectSave,{})
        if self.SelectDirectory == '':
            return
        self.files=Files(self.SelectDirectory,self.SelectSave)
        self.update_marklayout()

    #创建存储文件
    def createsave(self):
        self.createsave = QFileDialog.getSaveFileName(
            self.ui,  # 父窗口对象
            "创建存储文件",  # 标题
            "./",
            "存储文件(*.npy)"
        )
        if self.createsave == '':
            return
        if not os.path.exists(self.createsave[0]):
            np.save(self.createsave[0], {})
        self.SelectSave=self.createsave[0]

    #选择存储文件夹
    def selectdir(self):
        self.SelectDirectory = QFileDialog.getExistingDirectory(
            self.ui,  # 父窗口对象
            "选择文件夹",  # 标题
        )
        if self.SelectDirectory == '':
            return
        if self.files != None:
            self.files.over_save()
        self.files=Files(self.SelectDirectory,self.SelectSave)
        self.now_files=[i for i in self.files.total_files]
        self.ui.model=QStandardItemModel(len(self.files.total_files),1)
        self.ui.tableView.setModel(self.ui.model)
        self.update_tableview()

    #第一个页面点击表格响应事件将点击单元格内容发给右侧
    def table_left_click(self, item):
        self.item_filename=self.now_files[item.row()]
        self.update_rightitem()

    #更新右侧项目栏
    def update_rightitem(self):
        item_filename=self.item_filename
        fileInfo = QFileInfo(item_filename)
        self.ui.icon_label.setPixmap(QIcon(QFileIconProvider().icon(fileInfo)).pixmap(100,100))
        self.ui.icon_label.setScaledContents(True)
        self.ui.text_label.setText(self.files.getname(item_filename))
        self.ui.text_label.setFont(QFont("Roman times",20,QFont.Bold))
        #self.ui.text_label.resize(len(self.files.getname(item_filename))*18,30)

        self.ui.bulk_icon_label.setPixmap(QIcon(QFileIconProvider().icon(fileInfo)).pixmap(100,100))
        self.ui.bulk_icon_label.setScaledContents(True)
        self.ui.bulk_path_label.setText(self.files.getpath(item_filename))
        self.ui.bulk_path_label.setFont(QFont("Roman times",10,QFont.Bold))
        self.ui.bulk_path_label.resize(len(item_filename)*18,30)
        self.ui.filter_lineEdit.setText(self.files.getname(item_filename))
        self.ui.bulk_lineEdit.setText(self.files.getname(item_filename))
        self.update_marklayout()

    #第二个页面点击表格响应事件将点击单元格内容发给右侧
    def bulk_table_left_click(self, item):
        if item.row()*4+item.column() >= len(self.now_files):
            return
        self.item_filename=self.now_files[item.row()*4+item.column()]
        self.update_rightitem()

    #第一个页面过滤标签添加
    def add_filter(self):
        if self.ui.filter_lineEdit.text() in self.filters:
            return
        if [self.ui.filter_lineEdit.text()] == ['']:
            return
        self.filters+=[str(self.ui.filter_lineEdit.text())]
        self.update_filter()

    #第一个页面过滤标签删除
    def del_filter(self):
        if self.ui.filter_lineEdit.text() in self.filters:
            self.filters.remove(self.ui.filter_lineEdit.text())
        self.update_filter()

    #第一个页面拦截标签添加
    def add_inter(self):
        if self.ui.filter_lineEdit.text() in self.inters:
            return
        if [self.ui.filter_lineEdit.text()] == ['']:
            return
        self.inters+=[str(self.ui.filter_lineEdit.text())]
        self.update_filter()

    #第一个页面拦截标签拦截
    def del_inter(self):
        if self.ui.filter_lineEdit.text() in self.inters:
            self.inters.remove(self.ui.filter_lineEdit.text())
        self.update_filter()
        
    #第二个页面过滤规则添加
    def bulk_add_filter(self):
        if [self.ui.bulk_lineEdit.text()] == ['']:
            return
        if self.ui.bulk_lineEdit.text() in self.bulk_filters:
            return
        self.bulk_filters+=[self.ui.bulk_lineEdit.text()]
        self.update_bulk_layout()
        self.update_nowfiles()
        self.update_tableview()

    #第二个页面过滤规则删除
    def bulk_del_filter(self):
        if self.ui.bulk_lineEdit.text() in self.bulk_filters:
            self.bulk_filters.remove(self.ui.bulk_lineEdit.text())
        self.update_bulk_layout()
        self.update_nowfiles()
        self.update_tableview()

    #第二个页面拦截规则添加
    def bulk_add_inter(self):
        if [self.ui.bulk_lineEdit.text()] == ['']:
            return
        if self.ui.bulk_lineEdit.text() in self.bulk_inters:
            return
        self.bulk_inters+=[self.ui.bulk_lineEdit.text()]
        self.update_bulk_layout()
        self.update_nowfiles()
        self.update_tableview()

    #第二个页面拦截规则删除
    def bulk_del_inter(self):
        if self.ui.bulk_lineEdit.text() in self.bulk_inters:
            self.bulk_inters.remove(self.ui.bulk_lineEdit.text())
        self.update_bulk_layout()
        self.update_nowfiles()
        self.update_tableview()

    #给右侧项目添加标签
    def add_marks(self):
        if [self.ui.mark_lineEdit.text()] == ['']:
            return
        self.files.add_mark(self.item_filename,
                                self.ui.mark_lineEdit.text())
        self.update_marklayout()
        self.update_nowfiles()
        self.update_tableview()

    #给右侧项目删除标签
    def del_marks(self):
        if [self.ui.mark_lineEdit.text()] == ['']:
            return
        self.files.delete_mark(self.item_filename,
                                self.ui.mark_lineEdit.text())
        self.update_marklayout()
        self.update_nowfiles()
        self.update_tableview()
    
    #将点击内容发送到第一面的过滤文本框中
    def add_marktomarkLayout(self,s):
        self.ui.filter_lineEdit.setText(s)

    #将点击内容发送到第二面的过滤文本框中
    def add_to_bulkLayout(self,s):
        self.ui.bulk_lineEdit.setText(s)

    #更新第二面上方的过滤显示
    def update_bulk_layout(self):
        if self.files==None:
            return
        item_list = list(range(self.ui.bulk_matchrule_Layout.count()))
        item_list.reverse()# 倒序删除，避免影响布局顺序s
        for i in item_list:
            if i == 0:
                continue
            item = self.ui.bulk_matchrule_Layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            self.ui.bulk_matchrule_Layout.removeItem(item)
        item_list = list(range(self.ui.bulk_interrule_Layout.count()))
        item_list.reverse()# 倒序删除，避免影响布局顺序s
        for i in item_list:
            if i == 0:
                continue
            item = self.ui.bulk_interrule_Layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            self.ui.bulk_interrule_Layout.removeItem(item)
        col=1
        for i in self.bulk_filters:
            label=QLabel()
            self.ui.bulk_matchrule_Layout.addWidget(label,0,col)
            label=markLabel(label)
            label.setText(i)
            label.setFont(QFont("Roman times",8,QFont.Bold))
            label.resize(self.cal_biglen(i),35)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet('''
            QLabel {
            background-color:rgba(130,236,255,150);
            color:black;
            border-radius: 4px; 
            border-top:1px solid #6699cc;
            border-bottom:1px solid #6699cc;
            border-left:1px solid #6699cc;
            border-right:1px solid #6699cc;
            }
            QLabel:hover {background-color:orange;
            border-top:3px solid #6699cc;
            border-bottom:3px solid #6699cc;
            border-left:3px solid #6699cc;
            border-right:3px solid #6699cc;}
            ''')
            label.leftclick.connect(self.add_to_bulkLayout)
            col+=1

        col=1
        for i in self.bulk_inters:
            label=QLabel()
            self.ui.bulk_interrule_Layout.addWidget(label,0,col)
            label=markLabel(label)
            label.setText(i)
            label.setFont(QFont("Roman times",8,QFont.Bold))
            label.resize(self.cal_biglen(i),35)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet('''
            QLabel {
            background-color:rgba(130,236,255,150);
            color:black;
            border-radius: 4px; 
            border-top:1px solid #6699cc;
            border-bottom:1px solid #6699cc;
            border-left:1px solid #6699cc;
            border-right:1px solid #6699cc;
            }
            QLabel:hover {background-color:orange;
            border-top:3px solid #6699cc;
            border-bottom:3px solid #6699cc;
            border-left:3px solid #6699cc;
            border-right:3px solid #6699cc;}
            ''')
            label.leftclick.connect(self.add_to_bulkLayout)
            col+=1

    #更新右侧的标签显示
    def update_marklayout(self):
        if self.item_filename==[]:
            return
        item_list = list(range(self.ui.mark_Layout.count()))
        item_list.reverse()# 倒序删除，避免影响布局顺序s
        for i in item_list:
            item = self.ui.mark_Layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            self.ui.mark_Layout.removeItem(item)
        item_list = list(range(self.ui.bulk_mark_Layout.count()))
        item_list.reverse()# 倒序删除，避免影响布局顺序s
        for i in item_list:
            item = self.ui.bulk_mark_Layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            self.ui.bulk_mark_Layout.removeItem(item)    
        row=0
        col=0
        if (self.files.filesmark[self.item_filename]==[]):
            return
        
        for i in self.files.filesmark[self.item_filename]:
            label=QLabel()
            bulk_label=QLabel()
            self.ui.mark_Layout.addWidget(label,row,col)
            self.ui.bulk_mark_Layout.addWidget(bulk_label,row,col)
            label=markLabel(label)
            bulk_label=markLabel(bulk_label)
            label.setText(i)
            bulk_label.setText(i)
            bulk_label.resize(self.cal_len(i),28)
            label.resize(self.cal_len(i),28)
            label.setFont(QFont("Roman times",10))
            bulk_label.setFont(QFont("Roman times",10))
            label.setAlignment(Qt.AlignCenter)
            bulk_label.setAlignment(Qt.AlignCenter)
            bulk_label.setStyleSheet('''
            QLabel {
            background-color:rgba(130,236,255,150);
            color:black;
            border-radius: 4px; 
            border-top:1px solid #6699cc;
            border-bottom:1px solid #6699cc;
            border-left:1px solid #6699cc;
            border-right:1px solid #6699cc;
            }
            QLabel:hover {background-color:orange;
            border-top:3px solid #6699cc;
            border-bottom:3px solid #6699cc;
            border-left:3px solid #6699cc;
            border-right:3px solid #6699cc;}
            ''')
            label.setStyleSheet('''
            QLabel {
            background-color:rgba(130,236,255,150);
            color:black;
            border-radius: 4px; 
            border-top:1px solid #6699cc;
            border-bottom:1px solid #6699cc;
            border-left:1px solid #6699cc;
            border-right:1px solid #6699cc;
            }
            QLabel:hover {background-color:orange;
            border-top:3px solid #6699cc;
            border-bottom:3px solid #6699cc;
            border-left:3px solid #6699cc;
            border-right:3px solid #6699cc;}
            ''')
            label.leftclick.connect(self.add_marktomarkLayout)            
            bulk_label.leftclick.connect(self.add_marktomarkLayout)
            if col < 3 :
                col+=1
            else:
                row+=1
                col=0
   
    #更新第一面上方的过滤显示
    def update_filter(self):
        if self.files==None:
            return            
        item_list = list(range(self.ui.filter_gridLayout.count()))
        item_list.reverse()# 倒序删除，避免影响布局顺序s
        for i in item_list:
            if i == 0:
                break
            item = self.ui.filter_gridLayout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            self.ui.filter_gridLayout.removeItem(item)

        item_list = list(range(self.ui.inter_gridLayout.count()))
        item_list.reverse()# 倒序删除，避免影响布局顺序s
        for i in item_list:
            if i == 0:
                continue
            item = self.ui.inter_gridLayout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            self.ui.inter_gridLayout.removeItem(item)
        
        col=1
        for i in self.filters:
            label=QLabel()
            self.ui.filter_gridLayout.addWidget(label,0,col)
            label=markLabel(label)
            label.setText(i)
            label.setFont(QFont("Roman times",13,QFont.Bold))
            label.resize(self.cal_biglen(i),35)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet('''
            QLabel {
            background-color:rgba(130,236,255,150);
            color:black;
            border-radius: 4px; 
            border-top:1px solid #6699cc;
            border-bottom:1px solid #6699cc;
            border-left:1px solid #6699cc;
            border-right:1px solid #6699cc;
            }
            QLabel:hover {background-color:orange;
            border-top:3px solid #6699cc;
            border-bottom:3px solid #6699cc;
            border-left:3px solid #6699cc;
            border-right:3px solid #6699cc;}
            ''')
            label.leftclick.connect(self.add_marktomarkLayout)
            col+=1

        col=1
        for i in self.inters:
            label=QLabel()
            self.ui.inter_gridLayout.addWidget(label,0,col)
            label=markLabel(label)
            label.setText(i)
            label.setFont(QFont("Roman times",13,QFont.Bold))
            label.resize(self.cal_biglen(i),35)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet('''
            QLabel {
            background-color:rgba(130,236,255,150);
            color:black;
            border-radius: 4px; 
            border-top:1px solid #6699cc;
            border-bottom:1px solid #6699cc;
            border-left:1px solid #6699cc;
            border-right:1px solid #6699cc;
            }
            QLabel:hover {background-color:orange;
            border-top:3px solid #6699cc;
            border-bottom:3px solid #6699cc;
            border-left:3px solid #6699cc;
            border-right:3px solid #6699cc;}
            ''')
            label.leftclick.connect(self.add_marktomarkLayout)
            col+=1
        self.update_nowfiles()
        self.update_tableview()

    #更新当前文件
    def update_nowfiles(self):
        if self.files==None:
            return
        self.now_files.clear()
        tempfiles=[]
        tempfiles1=[]
        tempfiles2=[]
        flag=0
        for filename in self.files.total_files:
            for fil in self.filters:
                if fil == ' ' and self.files.filesmark[filename] == []:
                    break
                if fil not in self.files.filesmark[filename]:
                    flag = 1
                    break
            if flag == 0:
                tempfiles+=[filename]
            flag=0
            
        for filename in tempfiles:
            for patte in self.bulk_filters:
                if re.search(re.compile(str(patte)),filename) == None:
                    flag=1
                    break
            if flag == 0:
                tempfiles1+=[filename]
            flag=0

        for filename in tempfiles1:
            for inter in self.inters:
                if inter in self.files.filesmark[filename]:
                    flag=1
                    break
            if flag==0:
                tempfiles2+=[filename]
            flag=0
        
        for filename in tempfiles2:
            for patte in self.bulk_inters:
                if re.search(re.compile(str(patte)),filename) != None:
                    flag=1
                    break
            if flag == 0:
                self.now_files+=[filename]
            flag=0

    #更新左侧表格
    def update_tableview(self):
        if self.files==None:
            return
        self.ui.tableView.clearSpans()
        i=0
        row=0
        col=0
        self.ui.model=QStandardItemModel(len(self.now_files),1)
        self.ui.tableView.setModel(self.ui.model)
        
        self.ui.bulk_model=QStandardItemModel(len(self.now_files)//4+1,4)
        self.ui.bulk_tableView.setModel(self.ui.bulk_model)
        for filename in self.now_files:
            fileInfo = QFileInfo(filename)
            item=QStandardItem(QIcon(QFileIconProvider().icon(fileInfo)),str(self.files.getname(filename)))
            bulk_item=QStandardItem(QIcon(QFileIconProvider().icon(fileInfo)),str(self.files.getname(filename)))
            self.ui.model.setItem(i,0,item)
            self.ui.bulk_model.setItem(row,col,bulk_item)
            if col == 3:
                col=0
                row+=1
            else:
                col+=1
            i+=1

        self.ui.model.itemChanged.connect(self.renamefile)

    #切换界面
    def swtichpage(self):
        i = (self.ui.stackedWidget.currentIndex()+1)%2
        self.ui.stackedWidget.setCurrentIndex(i)

    #第二面的批量添加标签
    def bulk_addmark(self):
        if [self.ui.bulkmark_lineEdit.text()] == ['']:
            return
        for file in self.now_files:
            self.files.add_mark(file,
                                self.ui.bulkmark_lineEdit.text())
        self.update_marklayout()
        self.update_nowfiles()
        self.update_tableview()

    #第二面的批量删除标签
    def bulk_delmark(self):
        if [self.ui.bulkmark_lineEdit.text()] == ['']:
            return
        for file in self.now_files:
            self.files.delete_mark(file,
                                self.ui.bulkmark_lineEdit.text())
        self.update_marklayout()
        self.update_nowfiles()
        self.update_tableview()

    #第二面获取文件路径
    def bulk_getpath(self,s):
        self.ui.bulk_lineEdit.setText(s)

    #重置当前页面过滤规则，并刷新页面和内容
    def refresh(self):
        if self.ui.stackedWidget.currentIndex()==0:
            self.filters=[]
            self.inters=[]
            self.update_filter()
        else:
            self.bulk_filters=[]
            self.bulk_inters=[]
            self.update_bulk_layout()
            self.update_nowfiles()
            self.update_tableview()
        self.update_marklayout()

    #打开文件
    def open_files(self):
        if self.item_filename ==[]:
            return
        os.startfile(self.item_filename)

    #重命名文件
    def renamefile(self,item):
        new_filename=self.files.getpath(self.item_filename)+'/'+item.text()
        if os.path.exists(new_filename):
            self.update_tableview()
            return
        self.files.filesmark[new_filename]=self.files.filesmark.pop(self.item_filename)
        self.now_files.remove(self.item_filename)
        self.now_files+=[new_filename]
        self.files.total_files.remove(self.item_filename)
        self.files.total_files+=[new_filename]
        os.rename(self.item_filename,new_filename)
        self.update_tableview()
        self.item_filename=new_filename
        self.update_rightitem()

    #移动文件
    def movefile(self):
        self.MoveDirectory = QFileDialog.getExistingDirectory(
            self.ui,  # 父窗口对象
            "选择文件夹",  # 标题
        )
        if self.MoveDirectory == '':
            return
        if self.ui.stackedWidget.currentIndex()==0:
            new_filename=self.MoveDirectory+'/'+self.files.getname(self.item_filename)
            if new_filename ==self.item_filename or os.path.exists(new_filename):
                return
            self.files.filesmark[new_filename]=self.files.filesmark.pop(self.item_filename)
            self.now_files.remove(self.item_filename)
            self.now_files+=[new_filename]
            self.files.total_files.remove(self.item_filename)
            self.files.total_files+=[new_filename]
            os.rename(self.item_filename,new_filename)
            self.item_filename=new_filename
        else:
            if self.ui.stackedWidget.currentIndex()==1:
                temp_nowfiles=[]
                for i in self.now_files:
                    new_filename=self.MoveDirectory+'/'+self.files.getname(i)
                    if new_filename == i or os.path.exists(new_filename):
                        continue
                    self.files.filesmark[new_filename]=self.files.filesmark.pop(i)
                    self.files.total_files.remove(self.item_filename)
                    self.files.total_files+=[new_filename]
                    os.rename(i,new_filename)
                    temp_nowfiles+=[new_filename]
                self.now_files.clear()
                self.now_files=temp_nowfiles
        self.update_tableview()

    #计算字符串长度
    def cal_len(self,s):
        lens=6
        for i in s:
            if '\u4e00' <= i <= '\u9fff':
                lens+=30
            else:
                lens+=15
        return lens

    def cal_biglen(self,s):
        lens=8
        for i in s:
            if '\u4e00' <= i <= '\u9fff':
                lens+=40
            else:
                lens+=20
        return lens
        
    def dragEnterEvent_ui(self, e):
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent_ui(self,e):
        # filePathList = e.mimeData().text()
        # filePath = filePathList.split('\n')[0] #拖拽多文件只取第一个地址
        # filePath = filePath.replace('file:///', '', 1) #去除文件地址前缀的特定字符
        self.ui.filter_lineEdit.setText('1')

if __name__ == "__main__":
    app = QApplication([])
    stats = Stats()
    stats.ui.show()
    app.exec_()
    if(stats.files != None):
        stats.files.over_save()
