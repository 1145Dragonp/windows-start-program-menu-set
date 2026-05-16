"""
开始菜单管理工具主程序
使用 PyQt6 图形界面管理 Windows 开始菜单
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from core import StartMenuManager
from ui import StartMenuUI


def resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # 开发环境下的正常路径
        return os.path.join(os.path.dirname(__file__), relative_path)


def main():
    """主函数"""
    # 创建 Qt 应用
    app = QApplication(sys.argv)
    
    # 设置应用程序图标 - 使用 .ico 文件
    icon_path = resource_path('icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 创建管理器和 UI
    manager = StartMenuManager()
    window = StartMenuUI(manager)
    
    # 如果图标文件存在，也设置窗口图标
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    
    # 显示窗口
    window.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == '__main__':
    main()