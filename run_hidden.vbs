Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\PC\Desktop\티스토리 폴더"
WshShell.Run "cmd /c python run_web.py > bot_server.log 2>&1", 0, False
