"""
PyQt6 UI 界面模块
开始菜单管理工具的图形用户界面 - 标签页分离版
"""

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QTreeWidget, QTreeWidgetItem, QLabel, QLineEdit, 
                            QGroupBox, QRadioButton, QFileDialog, QMessageBox, QTabWidget,
                            QComboBox, QTextEdit, QSplitter, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
import os
from pathlib import Path


class StartMenuUI(QMainWindow):
    """开始菜单管理工具主窗口"""
    
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.current_user_scope = False  # 默认所有用户
        self.selected_item_path = ""    # 当前选中的项目路径
        self.selected_item_type = ""    # 当前选中的项目类型
        self.init_ui()
        self.refresh_menu_tree()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('Windows 开始菜单管理工具')
        self.setMinimumSize(900, 500)  # 减小窗口高度
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 范围选择
        scope_group = QGroupBox("应用范围")
        scope_layout = QHBoxLayout()
        self.current_user_radio = QRadioButton("当前用户")
        self.all_users_radio = QRadioButton("所有用户")
        self.all_users_radio.setChecked(True)  # 默认选择所有用户
        self.all_users_radio.toggled.connect(self.on_scope_changed)
        scope_layout.addWidget(self.current_user_radio)
        scope_layout.addWidget(self.all_users_radio)
        scope_layout.addStretch()
        scope_group.setLayout(scope_layout)
        main_layout.addWidget(scope_group)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 浏览标签页
        tab_widget.addTab(self.create_browse_tab(), "浏览菜单")
        # 创建快捷方式标签页
        tab_widget.addTab(self.create_shortcut_tab(), "创建快捷方式")
        # 创建文件夹标签页
        tab_widget.addTab(self.create_folder_tab(), "创建文件夹")
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def create_browse_tab(self):
        """创建浏览菜单标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 菜单树
        tree_label = QLabel("开始菜单结构:")
        layout.addWidget(tree_label)
        
        self.menu_tree = QTreeWidget()
        self.menu_tree.setHeaderLabels(["名称", "类型"])
        self.menu_tree.setColumnWidth(0, 250)
        self.menu_tree.setColumnWidth(1, 80)
        self.menu_tree.itemSelectionChanged.connect(self.on_tree_selection_changed)
        layout.addWidget(self.menu_tree)
        
        # 删除操作组
        delete_group = QGroupBox("删除选中项目")
        delete_layout = QVBoxLayout()
        
        self.delete_info_label = QLabel("未选择任何项目")
        self.delete_info_label.setWordWrap(True)
        delete_layout.addWidget(self.delete_info_label)
        
        self.delete_btn = QPushButton("删除选中项目")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.remove_selected_item)
        delete_layout.addWidget(self.delete_btn)
        
        delete_group.setLayout(delete_layout)
        layout.addWidget(delete_group)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新菜单")
        refresh_btn.clicked.connect(self.refresh_menu_tree)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        return widget
    
    def create_shortcut_tab(self):
        """创建快捷方式标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 快捷方式信息组
        shortcut_group = QGroupBox("快捷方式信息")
        shortcut_layout = QVBoxLayout()
        
        # 名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("名称:"))
        self.shortcut_name = QLineEdit()
        name_layout.addWidget(self.shortcut_name)
        shortcut_layout.addLayout(name_layout)
        
        # 目标路径
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("目标程序:"))
        self.target_path = QLineEdit()
        target_browse_btn = QPushButton("浏览")
        target_browse_btn.setFixedWidth(60)
        target_browse_btn.clicked.connect(self.browse_target)
        target_layout.addWidget(self.target_path)
        target_layout.addWidget(target_browse_btn)
        shortcut_layout.addLayout(target_layout)
        
        # 文件夹选择
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("放入文件夹:"))
        self.shortcut_folder_combo = QComboBox()
        self.shortcut_folder_combo.setEditable(True)
        folder_layout.addWidget(self.shortcut_folder_combo)
        shortcut_layout.addLayout(folder_layout)
        
        shortcut_group.setLayout(shortcut_layout)
        layout.addWidget(shortcut_group)
        
        # 创建按钮
        create_btn = QPushButton("创建快捷方式")
        create_btn.clicked.connect(self.create_shortcut)
        layout.addWidget(create_btn)
        
        layout.addStretch()
        return widget
    
    def create_folder_tab(self):
        """创建文件夹标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 文件夹信息组
        folder_group = QGroupBox("文件夹信息")
        folder_layout = QVBoxLayout()
        
        # 文件夹名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("文件夹名称:"))
        self.folder_name_input = QLineEdit()
        name_layout.addWidget(self.folder_name_input)
        folder_layout.addLayout(name_layout)
        
        # 父文件夹选择
        parent_layout = QHBoxLayout()
        parent_layout.addWidget(QLabel("父文件夹:"))
        self.parent_folder_combo = QComboBox()
        self.parent_folder_combo.setEditable(True)
        parent_layout.addWidget(self.parent_folder_combo)
        folder_layout.addLayout(parent_layout)
        
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)
        
        # 创建按钮
        create_btn = QPushButton("创建文件夹")
        create_btn.clicked.connect(self.create_folder)
        layout.addWidget(create_btn)
        
        layout.addStretch()
        return widget
    
    def on_scope_changed(self):
        """范围选择改变时刷新树"""
        self.current_user_scope = self.current_user_radio.isChecked()
        self.refresh_menu_tree()
    
    def refresh_menu_tree(self):
        """刷新菜单树显示"""
        self.menu_tree.clear()
        structure = self.manager.get_menu_structure(for_all_users=not self.current_user_scope)
        self.build_tree_items(self.menu_tree, structure, "")
        self.update_folder_combos()
        self.clear_selection()
    
    def build_tree_items(self, parent, structure, current_path):
        """递归构建树形结构"""
        # 添加快捷方式
        for shortcut in structure['shortcuts']:
            item = QTreeWidgetItem(parent)
            item.setText(0, shortcut['name'])
            item.setText(1, "快捷方式")
            item.setData(0, Qt.ItemDataRole.UserRole, {
                'type': 'shortcut',
                'path': shortcut['path'],
                'full_path': shortcut['full_path']
            })
            item.setIcon(0, QIcon.fromTheme("application-x-executable"))
        
        # 添加文件夹
        for folder_name, folder_content in structure['folders'].items():
            folder_item = QTreeWidgetItem(parent)
            folder_item.setText(0, folder_name)
            folder_item.setText(1, "文件夹")
            folder_path = f"{current_path}\\{folder_name}".strip('\\')
            folder_item.setData(0, Qt.ItemDataRole.UserRole, {
                'type': 'folder',
                'path': folder_path
            })
            folder_item.setIcon(0, QIcon.fromTheme("folder"))
            # 递归添加子内容
            self.build_tree_items(folder_item, folder_content, folder_path)
    
    def update_folder_combos(self):
        """更新文件夹下拉列表"""
        structure = self.manager.get_menu_structure(for_all_users=not self.current_user_scope)
        folders = self.extract_all_folders(structure, "")
        
        # 更新快捷方式标签页的文件夹下拉列表
        self.shortcut_folder_combo.clear()
        self.shortcut_folder_combo.addItem("")  # 空选项表示根目录
        self.shortcut_folder_combo.addItems(folders)
        
        # 更新文件夹标签页的父文件夹下拉列表
        self.parent_folder_combo.clear()
        self.parent_folder_combo.addItem("")  # 空选项表示根目录
        self.parent_folder_combo.addItems(folders)
    
    def extract_all_folders(self, structure, current_path):
        """提取所有文件夹路径"""
        folders = []
        if current_path:
            folders.append(current_path)
        
        for folder_name, folder_content in structure['folders'].items():
            folder_path = f"{current_path}\\{folder_name}".strip('\\')
            folders.extend(self.extract_all_folders(folder_content, folder_path))
        
        return folders
    
    def on_tree_selection_changed(self):
        """树形选择改变时更新删除信息"""
        selected_items = self.menu_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if item_data:
                self.selected_item_path = item_data['path']
                self.selected_item_type = item_data['type']
                type_text = "文件夹" if item_data['type'] == 'folder' else "快捷方式"
                self.delete_info_label.setText(f"选中: {item.text(0)} ({type_text})\n路径: {item_data['path']}")
                self.delete_btn.setEnabled(True)
            else:
                self.clear_selection()
        else:
            self.clear_selection()
    
    def clear_selection(self):
        """清除选择状态"""
        self.selected_item_path = ""
        self.selected_item_type = ""
        self.delete_info_label.setText("未选择任何项目")
        self.delete_btn.setEnabled(False)
    
    def browse_target(self):
        """浏览目标程序，默认从桌面开始"""
        desktop_path = os.path.expanduser("~/Desktop")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择目标程序", desktop_path, "可执行文件 (*.exe *.bat *.cmd);;所有文件 (*)"
        )
        if file_path:
            self.target_path.setText(file_path)
    
    def create_shortcut(self):
        """创建快捷方式"""
        name = self.shortcut_name.text().strip()
        target = self.target_path.text().strip()
        
        if not name or not target:
            QMessageBox.warning(self, "输入错误", "请填写名称和目标程序路径")
            return
        
        # 验证目标文件是否存在
        if not os.path.exists(target):
            QMessageBox.warning(self, "文件不存在", "目标程序文件不存在，请检查路径")
            return
        
        folder_path = self.shortcut_folder_combo.currentText().strip()
        for_all_users = not self.current_user_scope  # 注意：current_user_scope=False 表示所有用户
        
        success, message = self.manager.create_shortcut(
            name=name,
            target_path=target,
            folder_path=folder_path,
            for_all_users=for_all_users
        )
        
        if success:
            QMessageBox.information(self, "成功", message)
            self.refresh_menu_tree()
            # 清空输入
            self.shortcut_name.clear()
            self.target_path.clear()
            self.shortcut_folder_combo.setCurrentIndex(0)
        else:
            QMessageBox.critical(self, "错误", message)
    
    def create_folder(self):
        """创建文件夹"""
        folder_name = self.folder_name_input.text().strip()
        if not folder_name:
            QMessageBox.warning(self, "输入错误", "请填写文件夹名称")
            return
        
        parent_path = self.parent_folder_combo.currentText().strip()
        for_all_users = not self.current_user_scope  # 注意：current_user_scope=False 表示所有用户
        
        success, message = self.manager.create_folder(
            folder_name=folder_name,
            parent_path=parent_path,
            for_all_users=for_all_users
        )
        
        if success:
            QMessageBox.information(self, "成功", message)
            self.refresh_menu_tree()
            self.folder_name_input.clear()
            self.parent_folder_combo.setCurrentIndex(0)
        else:
            QMessageBox.critical(self, "错误", message)
    
    def remove_selected_item(self):
        """删除选中的项目"""
        if not self.selected_item_path:
            return
        
        item_name = self.selected_item_path.split('\\')[-1] if '\\' in self.selected_item_path else self.selected_item_path
        is_folder = self.selected_item_type == 'folder'
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除{'文件夹' if is_folder else '快捷方式'} '{item_name}' 吗？\n路径: {self.selected_item_path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 计算实际的文件夹路径（去掉最后的文件名/文件夹名）
            if '\\' in self.selected_item_path:
                folder_parts = self.selected_item_path.split('\\')
                actual_folder_path = '\\'.join(folder_parts[:-1])
                actual_item_name = folder_parts[-1]
            else:
                actual_folder_path = ""
                actual_item_name = self.selected_item_path
            
            for_all_users = not self.current_user_scope  # 注意：current_user_scope=False 表示所有用户
            
            success, message = self.manager.remove_item(
                item_name=actual_item_name,
                is_folder=is_folder,
                folder_path=actual_folder_path,
                for_all_users=for_all_users
            )
            
            if success:
                QMessageBox.information(self, "成功", message)
                self.refresh_menu_tree()
            else:
                QMessageBox.critical(self, "错误", message)