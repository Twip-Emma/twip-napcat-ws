import os

def remove_stopwords_from_dictionary():
    """
    从分词词库中去除停用词库中出现的词语
    """
    # 定义文件名
    dictionary_file = "分词词库.txt"
    stopwords_file = "停用词库.txt"
    output_file = "净化词库.txt"
    
    # 检查文件是否存在
    if not os.path.exists(dictionary_file):
        print(f"错误：找不到文件 {dictionary_file}")
        return
    
    if not os.path.exists(stopwords_file):
        print(f"错误：找不到文件 {stopwords_file}")
        return
    
    try:
        # 读取停用词库
        stopwords = set()
        with open(stopwords_file, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word:  # 只添加非空行
                    stopwords.add(word)
        
        print(f"停用词库已读取，共有 {len(stopwords)} 个停用词")
        
        # 读取分词词库并过滤
        filtered_words = []
        total_count = 0
        removed_count = 0
        
        with open(dictionary_file, 'r', encoding='utf-8') as f:
            for line in f:
                total_count += 1
                word = line.strip()
                
                if word and word not in stopwords:
                    filtered_words.append(word)
                elif word:
                    removed_count += 1
        
        # 写入新文件
        with open(output_file, 'w', encoding='utf-8') as f:
            for word in filtered_words:
                f.write(word + "\n")
        
        # 输出统计信息
        print(f"\n处理完成！")
        print(f"原始分词词库词数: {total_count}")
        print(f"去除的停用词数量: {removed_count}")
        print(f"净化后词库词数: {len(filtered_words)}")
        print(f"已保存到: {output_file}")
        
        # 显示部分被去除的词语示例（如果有的话）
        if removed_count > 0:
            print("\n提示：你可以检查输出文件确认过滤效果")
    
    except Exception as e:
        print(f"处理过程中出现错误: {e}")

def main():
    """
    主函数
    """
    print("=" * 50)
    print("分词词库净化工具")
    print("功能：从分词词库中去除停用词")
    print("=" * 50)
    
    # 显示当前目录下的txt文件
    txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]
    if txt_files:
        print(f"\n当前目录下的txt文件:")
        for file in txt_files:
            print(f"  - {file}")
    
    print(f"\n要求文件:")
    print(f"  1. 分词词库.txt - 需要处理的原始词库")
    print(f"  2. 停用词库.txt - 包含需要去除的词语")
    print(f"\n将生成:")
    print(f"  净化词库.txt - 处理后的词库")
    
    # 执行处理
    remove_stopwords_from_dictionary()

if __name__ == "__main__":
    main()
    
    # 等待用户按键（在Windows命令行中保持窗口打开）
    input("\n按Enter键退出...")