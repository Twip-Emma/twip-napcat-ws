import os
import glob

def combine_and_deduplicate_txt_files():
    """
    合并当前目录下所有txt文件的内容，去重后生成新的txt文件
    """
    # 获取当前目录下所有的txt文件
    txt_files = glob.glob("*.txt")
    
    if not txt_files:
        print("当前目录下没有找到txt文件！")
        return
    
    print(f"找到 {len(txt_files)} 个txt文件：")
    for file in txt_files:
        print(f"  - {file}")
    
    # 用于存储所有词语的集合（自动去重）
    all_words = set()
    
    # 读取所有txt文件的内容
    for txt_file in txt_files:
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()  # 去除首尾空白字符
                    if word:  # 只添加非空行
                        all_words.add(word)
            print(f"已读取文件: {txt_file}")
        except Exception as e:
            print(f"读取文件 {txt_file} 时出错: {e}")
    
    # 将集合转换为排序后的列表（可选，按字母顺序排序）
    sorted_words = sorted(all_words)
    
    # 输出文件路径
    output_file = "combined_words.txt"
    
    # 写入新的txt文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for word in sorted_words:
                f.write(word + "\n")
        
        print(f"\n成功生成文件: {output_file}")
        print(f"总共合并了 {len(all_words)} 个不重复的词语/短语")
        
    except Exception as e:
        print(f"写入文件时出错: {e}")

if __name__ == "__main__":
    combine_and_deduplicate_txt_files()
    
    # 等待用户按键（在Windows命令行中保持窗口打开）
    input("\n按Enter键退出...")