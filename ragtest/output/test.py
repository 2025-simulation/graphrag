import lancedb

# 🚨 确保路径正确：替换 'agtest/output/lancedb' 为您的实际绝对路径
DB_PATH = "./lancedb" 

try:
    db = lancedb.connect(DB_PATH)
    
    # 🎯 目标表：存储所有原始文本块/Text Units
    table_name = "default-text_unit-text"
    text_unit_table = db.open_table(table_name)
    
    # 💡 假设 Text Unit ID 对应于您引用的 Sources ID (65)
    source_id = 65
    
    # 执行查询
    # 注意：GraphRAG 内部的 ID 列名可能因版本而异，通常是 'id', 'text_unit_id', 或 'chunk_id'
    # 我们先尝试 GraphRAG 文档中常见的列名：'text_unit_id' 或 'id'
    
    print(f"尝试查询表 '{table_name}' 中 ID 为 {source_id} 的记录...")
    
    # 尝试使用 'id' 列名查询
    result_df = text_unit_table.search(query_vector=None).where(f"id = {source_id}").limit(1).to_pandas()
    
    if result_df.empty:
        # 如果 'id' 不行，尝试使用 'text_unit_id' (如果 GraphRAG 使用了该命名)
        result_df = text_unit_table.search(query_vector=None).where(f"text_unit_id = {source_id}").limit(1).to_pandas()

    if not result_df.empty:
        print("\n✅ 成功找到 Sources (65) 对应的原始文本：")
        # 原始文本通常存储在 'text' 或 'content' 列
        print("-" * 50)
        print("文本内容 (Text/Content 列):")
        # 尝试打印最可能是内容的列
        if 'text' in result_df.columns:
            print(result_df['text'].iloc[0])
        elif 'content' in result_df.columns:
            print(result_df['content'].iloc[0])
        else:
            print("找到记录，但无法确定包含内容的列名。请检查以下 DataFrame:")
            print(result_df)
        print("-" * 50)
    else:
        print(f"❌ 未能找到 ID 为 {source_id} 的原始文本（Sources）。请检查 ID 是否为 'text_unit_id' 或 'id'。")

except Exception as e:
    print(f"发生错误：{e}")
    print("请确保您已安装 'lancedb' 和 'pyarrow' 库，并且数据库路径正确。")
