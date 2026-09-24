#!/usr/bin/env python3
"""HCL Notes 公布函批次轉寄腳本"""
import pyautogui, pywinauto, time, sys
from pywinauto import Application
import win32gui, win32process

# Notes 視窗座標
WIN_X, WIN_Y = 780, 0
WIN_W, WIN_H = 1140, 1035
SCREEN_X = WIN_X  # 螢幕 X = 視窗 X + 780
ROW_H = 42
START_Y = 174

# 收件者群組
RECIPIENT = "工三碳化矽專案組-03-全組(21)"

def restore_notes():
    """恢復 Notes 視窗"""
    for proc in __import__('multiprocessing').process.active_children() or []:
        pass
    import subprocess
    result = subprocess.run(['powershell', '-Command', 
        'Add-Type -TypeDefinition "using System;using System.Runtime.InteropServices;public class R{[DllImport(\"user32.dll\")]public static extern bool ShowWindow(IntPtr h,int n);[DllImport(\"user32.dll\")]public static extern bool SetForegroundWindow(IntPtr h);public static void Run(){var p=System.Diagnostics.Process.GetProcessesByName(\"nlnotes\");foreach(var proc in p){if(proc.MainWindowHandle!=(IntPtr)0){ShowWindow(proc.MainWindowHandle,9);Thread.Sleep(300);SetForegroundWindow(proc.MainWindowHandle);Thread.Sleep(500);break;}}}"; [R]::Run()'],
        capture_output=True, text=True)
    time.sleep(1)

def find_unread_rows():
    """找出色標記（未讀）的列"""
    import subprocess
    result = subprocess.run(['powershell', '-Command', '''
        Add-Type -TypeDefinition @"
        using System;
        using System.Runtime.InteropServices;
        public class US {
            [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
            [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int n);
            [DllImport("user32.dll")] public static extern IntPtr FindWindow(string c,string w);
            public static void Run() {
                var p=System.Diagnostics.Process.GetProcessesByName("nlnotes");
                foreach(var proc in p) {
                    if(proc.MainWindowHandle!=(IntPtr)0) { ShowWindow(proc.MainWindowHandle,9); System.Threading.Thread.Sleep(300); SetForegroundWindow(proc.MainWindowHandle); System.Threading.Thread.Sleep(500); break; }
                }
            }
        }
        "@
        [US]::Run()
    '''], capture_output=True, text=True)
    time.sleep(1)
    
    # 使用截圖分析
    import subprocess
    subprocess.run(['powershell', '-File', 
        r'D:\80-Opnecode\.opencode\skills\hcl-notes-forward\scripts\capture_fullscreen.ps1',
        r'C:\Users\N000149839\.local\share\opencode\notes_scan.png'], capture_output=True)
    
    from PIL import Image
    img = Image.open(r'C:\Users\N000149839\.local\share\opencode\notes_scan.png').convert('RGB')
    
    unread = []
    y = 174
    idx = 0
    while y < 1035 and idx < 30:
        red = black = 0
        for x in range(304, 800, 2):
            for yy in range(y, y+42, 2):
                try:
                    r,g,b = img.getpixel((x, yy))
                    if r>150 and g<100 and b<100: red+=1
                    elif r<90 and g<100: black+=1
                except: pass
        if red > black and red > 20:
            unread.append({'y': y, 'idx': idx})
        y += 42
        idx += 1
    return unread

def click_screen(x, y):
    """螢幕座標點擊"""
    pyautogui.click(x, y)
    time.sleep(0.3)

def type_text(text, delay=0.05):
    """輸入文字"""
    pyautogui.typewrite(text, interval=delay)

def scroll_down(amount=3):
    """滾動"""
    pyautogui.scroll(-amount * 100)
    time.sleep(0.5)

def forward_email(row_y):
    """轉寄指定列的郵件"""
    screen_x = 350  # 點擊郵件列
    screen_y = row_y
    
    # 點擊郵件列
    click_screen(screen_x, screen_y)
    time.sleep(0.5)
    
    # 點擊轉寄按鈕 (工具列 y=117, x=580 from window = 780+580=1360 screen)
    click_screen(1360, 117)
    time.sleep(1.5)
    
    # 檢查是否開啟了 memo
    # 用 Escape 關閉可能存在的 dialog
    pyautogui.press('escape')
    time.sleep(0.3)
    
    # 如果 memo 沒開，嘗試用選單
    # Alt+F -> N (新訊息/轉寄)
    # 但我們用工具列的轉寄按鈕
    
    # 等待 memo 開啟
    time.sleep(1)
    
    # 檢查 memo 是否開啟
    import subprocess
    result = subprocess.run(['powershell', '-Command', 
        '$p=Get-Process nlnotes -ErrorAction SilentlyContinue | Select-Object -First 1; $p.MainWindowTitle'],
        capture_output=True, text=True)
    title = result.stdout.strip()
    
    if 'memo' in title.lower() or '轉寄' in title or 'N000' in title:
        print(f"  Memo opened: {title}")
        return True
    else:
        print(f"  Memo NOT opened, title: {title}")
        return False

def main():
    print("HCL Notes 公布函批次轉寄")
    print("=" * 40)
    
    # 恢復 Notes 視窗
    restore_notes()
    time.sleep(1)
    
    # 找未讀郵件
    print("掃描未讀郵件...")
    unread = find_unread_rows()
    print(f"找到 {len(unread)} 封未讀郵件")
    
    if not unread:
        print("沒有未讀郵件，結束。")
        return
    
    # 處理每封未讀郵件
    processed = 0
    for item in unread:
        y = item['y']
        print(f"\n處理第 {processed+1} 封 (y={y})...")
        
        # 點擊郵件
        click_screen(350, y)
        time.sleep(0.5)
        
        # 點擊轉寄
        click_screen(1360, 117)
        time.sleep(2)
        
        # 檢查是否成功開啟 memo
        import subprocess
        result = subprocess.run(['powershell', '-Command', 
            '$p=Get-Process nlnotes | Select-Object -First 1; $p.MainWindowTitle'],
            capture_output=True, text=True)
        title = result.stdout.strip()
        
        if '轉寄' in title or 'memo' in title.lower():
            print(f"  ✓ Memo 已開啟")
            processed += 1
            # 這裡需要繼續填寫收件者等
            # 但先完成基本流程
        else:
            print(f"  ✗ Memo 未開啟: {title}")
    
    print(f"\n完成: {processed} 封")

if __name__ == '__main__':
    main()
