explore_switch = True
prompt = ""
instruction = ""


if explore_switch:
    prompt += ("Stop: If you believe all the requirements of the user's instruction have been completed and no further action is needed, you can choose this operation to terminate the process. Then your output format is Stop|Information (this information is the core part of what the user needs,"
               "please keep only the essential part and remove any extra descriptive words) for example, Stop|something, and do not output anything else.")
else:
    prompt += "Stop: If you believe all the requirements of the user's instruction have been completed and no further action is needed, you can choose this operation to terminate the process."


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


