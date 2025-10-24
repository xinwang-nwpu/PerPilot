import chromadb


def semantic_analysis(message, knowledge):
    chroma_client = chromadb.Client()

    collection = chroma_client.get_or_create_collection(name="my_collection")

    # 处理知识库数据
    lines = knowledge
    lines =[x for x in lines if x != '\n']
    first_list = []
    for line in lines:
        stripped_line = line.strip()
        if stripped_line:
            parts = stripped_line.split('|')
            if parts:
                first_list.append(parts[0])

    # 创建检索列表
    second_list = [str(i) for i in range(1, len(first_list) + 1)]

    if first_list:
        collection.upsert(
            documents=first_list,
            ids=second_list
        )
    else:
        collection.upsert(
            documents="",
            ids="1"
        )

    # 执行查询
    results = collection.query(
        query_texts=message,
        n_results=10  # 增加查询结果数量以便筛选
    )

    result = []
    wrong_result = []

    # 处理查询结果
    for i in range(len(message)):
        query_message = message[i]
        query_results = results['ids'][i]
        query_distances = results['distances'][i]

        valid_results = []
        for j in range(len(query_results)):
            if query_distances[j] < 0.4:  # 阈值判断
                valid_results.append((int(query_results[j]), query_distances[j]))

        # 选择距离最小的结果
        if valid_results:
            min_result = min(valid_results, key=lambda x: x[1])
            result_id = min_result[0]
            result.append({
                "id": query_message.lower(),
                "ID": lines[result_id - 1].replace("\n", "").split("|")[-1]
            })
        else:
            wrong_result.append(query_message)

    return result, wrong_result