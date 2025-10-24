explore_switch = True
prompt = ""
instruction = ""

if explore_switch:
    prompt += ("停止（Stop）：如果你认为用户指令的所有要求已完成，无需进一步操作，可以选择此操作终止操作流程。然后你的输出格式是 停止|信息(这个信息就是你找到的用户所需要的信息,"
               "请对找到的信息简写只保留其核心部分多余修饰词进行舍去)比如停止|西北工业大学,然后其余的东西都不要输出")
else:
    prompt += "停止（Stop）：如果你认为用户指令的所有要求已完成，无需进一步操作，可以选择此操作终止操作流程。"

if explore_switch:
    prompt += ("Stop: If you believe all the requirements of the user's instruction have been completed and no further action is needed, you can choose this operation to terminate the process. Then your output format is Stop|Information (this information is the core part of what the user needs,"
               "please keep only the essential part and remove any extra descriptive words) for example, Stop|西北工业大学, and do not output anything else.")
else:
    prompt += "Stop: If you believe all the requirements of the user's instruction have been completed and no further action is needed, you can choose this operation to terminate the process."


if explore_switch:
    prompt += f"""
    你需要根据用户的指令帮助用户从这个APP中找到这个信息的对应的信息。下面的这些提示可能会帮助你更好的完成任务\n
    提示一:用户所需要的信息是一些具有个性化元素的信息,这些信息对于不同人而言其含义不同比如家、朋友，所以不要直接查找这些信息。\n
    提示二:当你发现信息上面标有...即省略号时,你应该尝试获取信息的全部内容而不是直接将带有省略号的信息进行输出。\n
    提示三:用户原本的指令是{instruction}这个指令中的信息可能可以帮助你更好的寻找用户需要的信息。\n
    提示四:信息不需要找到特别详细的信息，当你认为找到任何可能是用户需要的信息时都可以进行提交。\n
    记住以上提示都只是一些辅助信息你需要结合自己的思考来判断是否可用。\n
    你需要做的是善用自己的思考能力,首先思考要找什么信息。\n
    请注意对于任务来说并不是信息越多越好反而是信息越精简越好(比如家一般你只需要找一个地址,好朋友一般你只需要找一个姓名.其他类型的信息请你自己思考需要找什么信息)\n
    然后找到这个APP中哪个信息最有可能代表这个信息。\n
    当你找到信息时你应该输出finish|信息(这个信息就是你找到的用户所需要的信息,请对找到的信息简写只保留其核心部分多余修饰词进行舍去)比如finish|西北工业大学,然后其余的东西都不要输出。\n
    """

if explore_switch:
    prompt += f"""
    You need to help the user find the corresponding information in this app based on their instructions. The following hints may help you better complete the task.\n
    Hint 1: The information the user needs contains personalized elements, which have different meanings for different people, such as home, friends. Therefore, do not directly search for these terms.\n
    Hint 2: When you find information marked with ... (ellipsis), you should try to obtain the full content of the information rather than directly outputting the information with ellipsis.\n
    Hint 3: The user's original instruction is {instruction}. The information in this instruction may help you better find the information the user needs.\n
    Remember that the above hints are only auxiliary information; you need to use your own judgment to determine if they are useful.\n
    You need to use your thinking ability to first determine what information to find.\n
    Note that for the task, more information is not necessarily better; rather, more concise information is better (for example, for home, you usually only need to find an address; for a good friend, you usually only need to find a name. For other types of information, think about what you need to find).\n
    Then find which information in this app is most likely to represent the information you need.\n
    """


