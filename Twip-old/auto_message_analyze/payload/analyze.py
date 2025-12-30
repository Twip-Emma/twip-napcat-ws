import os

async def remove_keyword_from_dictionary(keyword, dictionary_file):
    """
    从分词词库中删除指定关键词对应的行
    
    参数:
        keyword: 要删除的关键词/短语
    """
    # 定义文件名
    backup_file = "分词词库_备份.txt"
    
    # 检查文件是否存在
    if not os.path.exists(dictionary_file):
        print(f"错误：找不到文件 {dictionary_file}")
        return False
    
    try:
        # 读取原始文件内容
        lines = []
        found_keywords = []
        
        with open(dictionary_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                word = line.strip()
                if word == keyword:
                    found_keywords.append((line_num, word))
                else:
                    lines.append(line)  # 保留原始行（包括换行符）
        
        # 如果没有找到关键词
        if not found_keywords:
            print(f"未找到关键词: '{keyword}'")
            return False
        
        # 创建备份文件
        import shutil
        shutil.copy2(dictionary_file, backup_file)
        print(f"已创建备份文件: {backup_file}")
        
        # 写入更新后的内容
        with open(dictionary_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # 输出结果
        print(f"已从分词词库中删除关键词: '{keyword}'")
        print(f"找到并删除了 {len(found_keywords)} 处匹配项:")
        for line_num, word in found_keywords:
            print(f"  第 {line_num} 行: {word}")
        print(f"原始文件已更新，原始内容已备份到 {backup_file}")
        
        return True
    
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        return False

async def remove_multiple_keywords(keywords_list, dictionary_file):
    """
    批量删除多个关键词
    
    参数:
        keywords_list: 要删除的关键词列表
    """
    backup_file = "分词词库_备份.txt"
    
    if not os.path.exists(dictionary_file):
        print(f"错误：找不到文件 {dictionary_file}")
        return False
    
    try:
        # 将关键词列表转换为集合以便快速查找
        keywords_to_remove = set(keywords_list)
        
        # 读取原始文件内容
        lines = []
        removed_counts = {keyword: 0 for keyword in keywords_list}
        
        with open(dictionary_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                word = line.strip()
                if word in keywords_to_remove:
                    removed_counts[word] += 1
                else:
                    lines.append(line)
        
        # 统计总共删除了多少行
        total_removed = sum(removed_counts.values())
        
        if total_removed == 0:
            print("未找到任何要删除的关键词")
            return False
        
        # 创建备份
        import shutil
        shutil.copy2(dictionary_file, backup_file)
        print(f"已创建备份文件: {backup_file}")
        
        # 写入更新后的内容
        with open(dictionary_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # 输出结果
        print(f"批量删除完成:")
        print(f"总共删除了 {total_removed} 个关键词")
        for keyword, count in removed_counts.items():
            if count > 0:
                print(f"  '{keyword}': 删除了 {count} 处")
        print(f"原始文件已更新，原始内容已备份到 {backup_file}")
        
        return True
    
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        return False