import os, sys
print("HOJ tool打包程序")
os.system("pause")
import minifier
print("\n\n正在压缩静态文件...")
minifier.minify_directory(".\\static")
print("压缩完成\n\n")

# 保存当前目录
original_cwd = os.getcwd()

try:
    # 切换到项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    print(f"当前工作目录: {os.getcwd()}")

    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['LC_ALL'] = 'C.UTF-8'

    # 构建命令
    command = f"{sys.executable} -m nuitka main.py --standalone --include-data-dir=static=static --lto=yes --product-name=\"HOJ tool\" --product-version=4.1 --windows-icon-from-ico=./main.ico --copyright=Hemean-MIT --enable-plugin=tk-inter --windows-disable-console --experimental=use_pefile --experimental=use_pefile_recurse --experimental=use_pefile_fullrecurse"

    print(f"正在打包程序...\n命令：{command}")

    result = os.system(f"set PYTHONIOENCODING=utf-8 && set LC_ALL=C.UTF-8 && {command}")
    
    if result != 0:
        print(f"打包失败，返回码: {result}")
        print("建议将项目移动到纯英文路径下再进行编译")
    else:
        print("打包完成！")

except Exception as e:
    print(f"打包过程中发生错误: {e}")
    print("建议将项目移动到纯英文路径下再进行编译")

finally:
    # 恢复原始工作目录
    os.chdir(original_cwd)
    print(f"恢复工作目录: {original_cwd}")