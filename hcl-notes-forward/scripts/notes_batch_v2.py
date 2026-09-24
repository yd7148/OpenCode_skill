#!/usr/bin/env python3
"""HCL Notes 公布函批次轉寄 - 使用 Windows API"""
import ctypes
import time
import subprocess
from ctypes import wintypes

user32 = ctypes.windll.user32

# Notes 視窗位置
SCREEN_OFFSET_X = 780
SCREEN_OFFSET_Y = 0

# 工具列按鈕座標 (相對於視窗左邊)
FORWARD_BTN_X = 580
FORWARD_BTN_Y = 117

# 收件者群組
GROUP_NAME = "工三碳化矽專案組-03-全組(21)"

def set_foreground(hwnd):
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.3)

def show_window(hwnd, cmd):
    user32.ShowWindow(hwnd, cmd)
    time.sleep(0.3)

def mouse_click(screen_x, screen_y):
    user32.SetCursorPos(screen_x, screen_y)
    time.sleep(0.2)
    user32.mouse_event(0x0002 | 0x0004, 0, 0, 0, 0)
    time.sleep(0.5)

def type_keys(text):
    for c in text:
        user32.keybd_event(ord(c), 0, 0, 0)
        time.sleep(0.03)
        user32.keybd_event(ord(c), 0, 2, 0)
        time.sleep(0.03)

def get_notes_hwnd():
    for proc in subprocess.Popen(['powershell', '-Command', 
        'Get-Process nlnotes | Select-Object -First 1 | Format-List MainWindowHandle'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout:
        pass
    # Use .NET to get handle
    result = subprocess.run(['powershell', '-Command', 
        '$p=Get-Process nlnotes | Select-Object -First 1; $p.MainWindowHandle'],
        capture_output=True, text=True)
    try:
        return int(result.stdout.strip(), 16) if result.stdout.strip() else 0
    except:
        return 0

def get_notes_title():
    result = subprocess.run(['powershell', '-Command',
        '$p=Get-Process nlnotes | Select-Object -First 1; $p.MainWindowTitle'],
        capture_output=True, text=True)
    return result.stdout.strip()

def find_unread_rows():
    """找未讀郵件行"""
    # Capture screenshot
    subprocess.run(['powershell', '-File',
        r'D:\80-Opnecode\.opencode\skills\hcl-notes-forward\scripts\capture_win.ps1',
        'nlnotes',
        r'C:\Users\N000149839\.local\share\opencode\notes_temp.png'],
        capture_output=True)
    
    from PIL import Image
    img = Image.open(r'C:\Users\N000149839\.local\share\opencode\notes_temp.png').convert('RGB')
    
    unread = []
    y = 174
    idx = 0
    while y < 1035 and idx < 30:
        red = black = 0
        for x in range(304, 800, 2):
            for yy in range(y, min(y+42, img.height), 2):
                try:
                    r,g,b = img.getpixel((x, yy))
                    if r>150 and g<100 and b<100: red+=1
                    elif r<90 and g<100: black+=1
                except: pass
        if red > black and red > 20:
            unread.append({'y': y, 'screen_y': y + SCREEN_OFFSET_Y, 'idx': idx})
        y += 42
        idx += 1
    return unread

def click_email_row(unread_item):
    """點擊未讀郵件列"""
    screen_x = 350
    screen_y = unread_item['screen_y']
    mouse_click(screen_x, screen_y)
    time.sleep(0.8)

def click_forward():
    """點擊轉寄按鈕"""
    screen_x = FORWARD_BTN_X + SCREEN_OFFSET_X
    screen_y = FORWARD_BTN_Y + SCREEN_OFFSET_Y
    mouse_click(screen_x, screen_y)
    time.sleep(2)

def close_memo():
    """關閉 memo (Ctrl+W)"""
    user32.keybd_event(0x11, 0, 0, 0)  # Ctrl
    user32.keybd_event(0x57, 0, 0, 0)  # W
    time.sleep(0.1)
    user32.keybd_event(0x57, 0, 2, 0)
    user32.keybd_event(0x11, 0, 2, 0)
    time.sleep(1)
    # 可能需按兩次
    user32.keybd_event(0x11, 0, 0, 0)
    user32.keybd_event(0x57, 0, 0, 0)
    time.sleep(0.1)
    user32.keybd_event(0x57, 0, 2, 0)
    user32.keybd_event(0x11, 0, 2, 0)
    time.sleep(1)

def delete_current():
    """刪除當前郵件"""
    user32.keybd_event(0x2E, 0, 0, 0)
    time.sleep(0.1)
    user32.keybd_event(0x2E, 0, 2, 0)
    time.sleep(0.5)

def restore_notes():
    """恢復 Notes 視窗"""
    hwnd = get_notes_hwnd()
    if hwnd:
        show_window(hwnd, 9)  # SW_RESTORE
        set_foreground(hwnd)
        time.sleep(0.5)

def navigate_by_sender():
    """導航到 $BySender 視圖"""
    # Ctrl+Shift+F5 + type $BySender
    user32.keybd_event(0x11, 0, 0, 0)  # Ctrl
    user32.keybd_event(0x10, 0, 0, 0)  # Shift
    user32.keybd_event(0x74, 0, 0, 0)  # F5
    time.sleep(0.1)
    user32.keybd_event(0x74, 0, 2, 0)
    user32.keybd_event(0x10, 0, 2, 0)
    user32.keybd_event(0x11, 0, 2, 0)
    time.sleep(2)
    
    type_keys('$BySender')
    time.sleep(0.3)
    user32.keybd_event(0x0D, 0, 0, 0)
    time.sleep(0.1)
    user32.keybd_event(0x0D, 0, 2, 0)
    time.sleep(3)

def main():
    print("=" * 50)
    print("HCL Notes 公布函批次轉寄")
    print("=" * 50)
    
    # 恢復 Notes
    restore_notes()
    time.sleep(1)
    
    # 導航到 $BySender
    print("導航到 $BySender 視圖...")
    navigate_by_sender()
    
    # 找未讀郵件
    print("掃描未讀郵件...")
    unread = find_unread_rows()
    print(f"找到 {len(unread)} 封未讀郵件")
    
    for i, item in enumerate(unread):
        print(f"\n處理第 {i+1}/{len(unread)} 封 (y={item['y']})...")
        
        # 點擊郵件
        click_email_row(item)
        
        # 點擊轉寄
        click_forward()
        
        # 檢查 memo 是否開啟
        title = get_notes_title()
        if '轉寄' in title or 'memo' in title.lower() or 'N000' in title:
            print(f"  ✓ Memo 已開啟: {title[:50]}")
            
            # 填寫收件者
            # 這裡需要更多邏輯來填寫收件者
            
            # 關閉 memo
            close_memo()
            
            # 刪除原信
            delete_current()
        else:
            print(f"  ✗ Memo 未開啟: {title}")
        
        time.sleep(1)
    
    print(f"\n完成! 共處理 {len(unread)} 封")

if __name__ == '__main__':
    main()
