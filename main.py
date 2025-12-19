import sys
from os import path as pt
from lib.port_utils import get_port

def main():
    import webview
    import server
    from threading import Thread

    # 获取可用端口
    port = get_port()

    # 启动服务器线程，传递端口参数
    server_thread = Thread(target=server.start_server, args=(port,))
    server_thread.daemon = True
    server_thread.start()

    def on_closing():
        import os
        os._exit(0)

    try:
        window = webview.create_window('HOJ tool', f'http://127.0.0.1:{port}', maximized=True)
        window.events.closing += on_closing
        webview.start()
    except Exception as e:
        import tkinter
        import tkinter.messagebox
        root = tkinter.Tk()
        root.withdraw()
        tkinter.messagebox.showerror("HOJ tool Error", f"打开浏览页面发生错误:{e}\n请确认是否安装WebView2或IE COM组件，Win7/8需自行安装组件。如无法解决，请向HOJ tool反馈")
        root.destroy()

if __name__ == '__main__':
    main()