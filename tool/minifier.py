import jsmin
import os
import re

def minify_js_file(input_path, output_path=None):
    # 如果没有指定输出路径，则覆盖原文件
    if output_path is None:
        output_path = input_path
    
    # 读取原文件内容
    with open(input_path, 'r', encoding='utf-8') as js_file:
        js_content = js_file.read()
    
    # 使用jsmin压缩JS代码
    minified_js = jsmin.jsmin(js_content)
    
    # 写入压缩后的文件（覆盖原文件）
    with open(output_path, 'w', encoding='utf-8') as min_file:
        min_file.write(minified_js)
    
    return output_path

def minify_css_file(input_path, output_path=None):
    # 如果没有指定输出路径，则覆盖原文件
    if output_path is None:
        output_path = input_path
    
    # 读取原文件内容
    with open(input_path, 'r', encoding='utf-8') as css_file:
        css_content = css_file.read()
    
    # 简单的CSS压缩：移除注释、多余的空格和换行符
    # 移除CSS注释
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    # 移除多余的空格和换行符
    css_content = re.sub(r'\s+', ' ', css_content)
    # 移除多余的空格（在特定字符周围）
    css_content = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css_content)
    # 移除最后一个分号
    css_content = re.sub(r';}', r'}', css_content)
    # 去除首尾空格
    css_content = css_content.strip()
    
    # 写入压缩后的文件（覆盖原文件）
    with open(output_path, 'w', encoding='utf-8') as min_file:
        min_file.write(css_content)
    
    return output_path

def minify_html_file(input_path, output_path=None):
    # 如果没有指定输出路径，则覆盖原文件
    if output_path is None:
        output_path = input_path
    
    # 读取原文件内容
    with open(input_path, 'r', encoding='utf-8') as html_file:
        html_content = html_file.read()
    
    # 简单的HTML压缩：移除注释、多余的空格和换行符
    # 移除HTML注释
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    # 移除多余的空格和换行符
    html_content = re.sub(r'\s+', ' ', html_content)
    # 去除首尾空格
    html_content = html_content.strip()
    
    # 写入压缩后的文件（覆盖原文件）
    with open(output_path, 'w', encoding='utf-8') as min_file:
        min_file.write(html_content)
    
    return output_path

def minify_directory(input_dir, output_dir=None):
    # 如果没有指定输出目录，则使用原目录（覆盖原文件）
    if output_dir is None:
        output_dir = input_dir
    
    # 存储压缩后的文件路径
    minified_files = []
    
    # 递归遍历输入目录下的所有文件
    for root, dirs, files in os.walk(input_dir):
        # 计算相对路径
        rel_path = os.path.relpath(root, input_dir)
        # 构建目标目录路径
        target_dir = output_dir if rel_path == '.' else os.path.join(output_dir, rel_path)
        
        # 创建目标目录
        os.makedirs(target_dir, exist_ok=True)
        
        # 遍历文件
        for filename in files:
            input_path = os.path.join(root, filename)
            output_path = os.path.join(target_dir, filename)
            
            # 根据文件扩展名选择压缩方法
            if filename.endswith('.js') and not filename.endswith('.min.js'):
                minified_file = minify_js_file(input_path, output_path)
                minified_files.append(minified_file)
            elif filename.endswith('.css'):
                minified_file = minify_css_file(input_path, output_path)
                minified_files.append(minified_file)
            elif filename.endswith('.html'):
                minified_file = minify_html_file(input_path, output_path)
                minified_files.append(minified_file)
    
    return minified_files