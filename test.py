import os
import time
from projectlib import Project, Task

# 1. 初始化项目总管
print("初始化 Project...")
project = Project()
task = project.task # 这是 @task 装饰器的快捷方式

# --- 你的任务定义区 (这部分保持不变) ---

@task
def read_content(filename):
    """任务1：从磁盘读取文件内容。"""
    print(f"--- 正在执行 read_content({filename!r})...")
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

@task
def convert_to_html(filename):
    """任务2：将 Markdown 内容转换为 HTML。"""
    print(f"--- 正在执行 convert_to_html({filename!r})...")
    content = read_content(filename)
    
    title = content.splitlines()[0].replace('# ', '')
    body = '\n'.join(content.splitlines()[1:])
    
    html_content = f"<html>\n<head><title>{title}</title></head>\n<body>\n<h1>{title}</h1>\n<p>{body}</p>\n</body>\n</html>"
    return html_content

# --- 主程序入口 (这部分是全新的、正确的实现) ---
if __name__ == "__main__":
    
    source_file = "test.md"
    output_file = "test.html"

    # --- 步骤 A: 执行首次构建 ---
    print("\n>>> 开始首次构建...")
    html = convert_to_html(source_file)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f">>> 构建完成！结果已保存到 {output_file}")

    # --- 步骤 B: 启动我们自己的文件监视循环 ---
    print("\n>>> 进入监视模式，现在你可以去修改 test.md 文件了...")
    
    # 记录文件的上一次修改时间
    last_mtime = os.path.getmtime(source_file)

    try:
        while True:
            # 检查文件当前的修改时间
            current_mtime = os.path.getmtime(source_file)
            
            # 如果修改时间变了...
            if current_mtime != last_mtime:
                print(f"\n检测到文件变化: {source_file}")
                
                # 1. **通知 Project**：告诉它哪个任务的缓存失效了！
                #    这是最关键的一步！我们让 read_content('test.md') 这个任务失效。
                read_task = Task(read_content, (source_file,))
                project.invalidate(read_task)
                
                # 2. **命令 Project 重建**
                project.rebuild()
                
                # 3. 更新时间记录，并重新生成HTML文件
                last_mtime = current_mtime
                html = convert_to_html(source_file)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f">>> 文件已重新构建！")

            # 每隔1秒检查一次，避免CPU占用过高
            time.sleep(1)
            
    except KeyboardInterrupt:
        # 允许用户按 Ctrl+C 优雅地退出程序
        print("\n>>> 监视已停止。再见！")