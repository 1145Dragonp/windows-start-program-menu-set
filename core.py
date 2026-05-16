"""
核心开始菜单管理功能
使用 Python 标准库 + PowerShell 管理开始菜单快捷方式和文件夹
"""

import subprocess
import os
import sys
from pathlib import Path


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return os.getuid() == 0
    except AttributeError:
        # Windows
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


def run_as_admin():
    """重新以管理员权限运行程序"""
    import ctypes
    import sys
    if not is_admin():
        # 重新启动程序并请求管理员权限
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()


class StartMenuManager:
    """开始菜单管理器"""
    
    def __init__(self):
        # 所有用户的开始菜单路径
        self.all_users_path = Path(os.environ.get('PROGRAMDATA', 'C:\\ProgramData')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs'
        # 当前用户的开始菜单路径
        self.current_user_path = Path(os.environ['APPDATA']) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs'
    
    def _run_powershell(self, command):
        """执行 PowerShell 命令"""
        try:
            result = subprocess.run(
                ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', command],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, '', str(e)
    
    def create_shortcut(self, name, target_path, description='', icon_path='', 
                       working_directory='', arguments='', folder_path='', for_all_users=False):
        """
        创建快捷方式到开始菜单
        
        参数:
            name: 快捷方式名称
            target_path: 目标程序路径
            description: 描述
            icon_path: 图标路径(可选)
            working_directory: 工作目录(可选)
            arguments: 启动参数(可选)
            folder_path: 文件夹路径(相对于开始菜单根目录)
            for_all_users: 是否为所有用户创建
        """
        # 如果是所有用户操作且没有管理员权限，提示用户
        if for_all_users and not is_admin():
            return False, "错误: 创建所有用户的快捷方式需要管理员权限。请以管理员身份运行程序。"
        
        # 确定保存路径
        base_path = self.all_users_path if for_all_users else self.current_user_path
        if folder_path:
            shortcut_path = base_path / folder_path / f"{name}.lnk"
            # 确保文件夹存在
            (base_path / folder_path).mkdir(parents=True, exist_ok=True)
        else:
            shortcut_path = base_path / f"{name}.lnk"
        
        # 确保目标文件存在
        if not Path(target_path).exists():
            return False, f"错误: 目标文件不存在: {target_path}"
        
        # 构建 PowerShell 命令
        ps_command = f"""
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{target_path}"
        """
        
        if description:
            ps_command += f'$Shortcut.Description = "{description}"\n'
        
        if icon_path and Path(icon_path).exists():
            ps_command += f'$Shortcut.IconLocation = "{icon_path}"\n'
        
        if working_directory:
            ps_command += f'$Shortcut.WorkingDirectory = "{working_directory}"\n'
        
        if arguments:
            ps_command += f'$Shortcut.Arguments = "{arguments}"\n'
        
        ps_command += '$Shortcut.Save()\n'
        
        success, stdout, stderr = self._run_powershell(ps_command)
        
        if success:
            scope = "所有用户" if for_all_users else "当前用户"
            return True, f"成功创建快捷方式: {name} ({scope})"
        else:
            return False, f"创建失败: {stderr}"
    
    def create_folder(self, folder_name, parent_path='', for_all_users=False):
        """
        在开始菜单中创建文件夹
        
        参数:
            folder_name: 文件夹名称
            parent_path: 父文件夹路径(相对于开始菜单根目录)
            for_all_users: 是否为所有用户创建
        """
        # 如果是所有用户操作且没有管理员权限，提示用户
        if for_all_users and not is_admin():
            return False, "错误: 创建所有用户的文件夹需要管理员权限。请以管理员身份运行程序。"
        
        base_path = self.all_users_path if for_all_users else self.current_user_path
        if parent_path:
            folder_path = base_path / parent_path / folder_name
        else:
            folder_path = base_path / folder_name
        
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            scope = "所有用户" if for_all_users else "当前用户"
            return True, f"成功创建文件夹: {folder_name} ({scope})"
        except PermissionError:
            return False, "错误: 权限不足。创建所有用户的项目需要管理员权限。"
        except Exception as e:
            return False, f"创建文件夹失败: {str(e)}"
    
    def remove_item(self, item_name, is_folder=False, folder_path='', for_all_users=False):
        """
        从开始菜单删除项目(快捷方式或文件夹)
        
        参数:
            item_name: 项目名称
            is_folder: 是否为文件夹
            folder_path: 项目所在文件夹路径
            for_all_users: 是否从所有用户删除
        """
        # 如果是所有用户操作且没有管理员权限，提示用户
        if for_all_users and not is_admin():
            return False, "错误: 删除所有用户的项目需要管理员权限。请以管理员身份运行程序。"
        
        base_path = self.all_users_path if for_all_users else self.current_user_path
        if folder_path:
            item_path = base_path / folder_path / (item_name if is_folder else f"{item_name}.lnk")
        else:
            item_path = base_path / (item_name if is_folder else f"{item_name}.lnk")
        
        if not item_path.exists():
            # 尝试模糊匹配
            search_pattern = f"{item_name}*"
            matches = list(base_path.rglob(search_pattern))
            if not matches:
                return False, f"未找到项目: {item_name}"
            item_path = matches[0]
        
        try:
            if item_path.is_dir():
                # 删除文件夹及其内容
                import shutil
                shutil.rmtree(item_path)
            else:
                # 删除文件
                item_path.unlink()
            
            scope = "所有用户" if for_all_users else "当前用户"
            item_type = "文件夹" if is_folder else "快捷方式"
            return True, f"成功删除{item_type}: {item_name} ({scope})"
        except PermissionError:
            return False, "错误: 权限不足。删除所有用户的项目需要管理员权限。"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def get_menu_structure(self, for_all_users=False):
        """
        获取开始菜单的完整结构
        
        返回: 字典格式的菜单结构
        """
        base_path = self.all_users_path if for_all_users else self.current_user_path
        
        if not base_path.exists():
            return {}
        
        def scan_directory(path, relative_path=""):
            """递归扫描目录结构"""
            structure = {
                'folders': {},
                'shortcuts': []
            }
            
            try:
                for item in path.iterdir():
                    if item.is_dir():
                        folder_relative = f"{relative_path}\\{item.name}".strip('\\')
                        structure['folders'][item.name] = scan_directory(item, folder_relative)
                    elif item.suffix.lower() == '.lnk':
                        structure['shortcuts'].append({
                            'name': item.stem,
                            'path': str(item.relative_to(base_path)),
                            'full_path': str(item)
                        })
            except PermissionError:
                pass  # 跳过无权限访问的目录
            
            return structure
        
        return scan_directory(base_path)
