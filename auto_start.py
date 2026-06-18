# auto_start.py — Windows 开机自启动管理（通过注册表）
import sys
import os


APP_REG_NAME = "HotAllAutoStart"
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _get_exe_path():
    """获取当前可执行文件路径"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后
        return f'"{sys.executable}"'
    else:
        # 开发环境：python main.py
        python = f'"{sys.executable}"'
        script = f'"{os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))}"'
        return f'{python} {script}'


def is_auto_start_enabled():
    """检查是否已设置开机自启"""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, APP_REG_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False


def set_auto_start(enable):
    """启用或禁用开机自启"""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        if enable:
            winreg.SetValueEx(key, APP_REG_NAME, 0, winreg.REG_SZ, _get_exe_path())
        else:
            try:
                winreg.DeleteValue(key, APP_REG_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"设置开机自启失败: {e}")
        return False


def toggle_auto_start():
    """切换开机自启状态，返回新状态"""
    new_state = not is_auto_start_enabled()
    set_auto_start(new_state)
    return new_state
