
def get_personalization_prompt(instruction, txt):
    prompt = "### Important Information ###\n"
    prompt += f"""
    Please understand and evaluate the instructions I have given you to determine if they contain personalized elements.\n
    If the instruction contains words that need to be clarified by asking the user, or if certain words have different meanings for different people or devices, it can be determined that the instruction contains personalized elements, and these words are personalized elements. You need to strictly follow the following rules:\n
    Rule 1: If certain words have unique executable meanings, such as app names like QQ and WeChat, they are not personalized elements.\n
    Rule 2: When you think something is not a personalized element, directly determine that it is not a personalized element. \n”
    Rule 3: Strictly prohibit treating specific names as personalized elements, whether they are Chinese or English names. But abstract names are still personalized elements, such as friends.\n
    Rule 4:This personalized information has already been processed and no longer needs to be exported, and the processed information is as follows:\n{txt}\n
    If you think is not a personalized instruction, please answer 'No'. \n”
    If you think this is a personalized instruction, you need to determine which part of the instruction is the personalized element \n
    f"Then your answer should follow this format: 'Yes|First personalized element (i.e., the first part you consider personalized)|Second personalized element|Third personalized element (and so on, output all personalized elements,The same element only needs to be output once)', please note that your answer should not include any additional information outside the format I provided.\n"
    The current instruction is as follows:\n{instruction}
    """
    return prompt


def personalization_solve_prompt(txt):
    prompt = "### Important Information ###\n"
    prompt += (
        f"Now I will give you a table of personalized elements and their precise information. Each line in the table contains a personalized element and its corresponding precise information, in the format 'Personalized element part|Corresponding precise information'. The table is as follows (please note that the personalized elements in the table may not be exactly the same as the ones you found, but if they convey the same meaning, they can be considered the same):\n{txt}, "
        f"Please check each of the personalized elements you found previously in the table, and then perform one of the following two processes (please note that you must not omit any and must not add any others, you can only choose one process)\n")
    prompt += (
        f"First process: If you cannot find the precise information for any or all of the personalized elements, output 'No|First personalized element (i.e., the first personalized element part for which you cannot find precise information, no need to output the ones you can find, "
        f"no need to explain why it is a personalized element, only the most concise personalized element part)|Second personalized element (and so on, output all personalized elements you cannot find precise information for)\n")
    prompt += (
        f"Second process: If you can find the precise information for all personalized elements, replace the personalized elements in the original instruction with their corresponding precise information, and then generate a smooth and coherent instruction  and output it (only output the replaced instruction,do not output any content outside the instruction)\n")
    return prompt


def get_personalization_message_prompt(txt):
    prompt = f"### Important Information ###\n"
    prompt += f"After supplementation, the current table of personalized elements and their precise information is as follows: {txt}. Please use this information and the previous information to replace the personalized elements in the personalized instruction and output a smooth instruction (do not output any additional information).\n"
    return prompt


def get_explore_prompt(search_element, instruction):
    prompt = f"### Important Information ###\n"
    prompt += f"You need to assist me in completing an information exploration task. The specific task information is as follows:\n"
    prompt += f"""You are currently controlling the user's phone to complete the personalized instruction '{instruction}', but those personalized information: ({search_element})(You only need to deal with the personalized elements in parentheses) in the instruction is missing. I am now trying to obtain the precise information for these personalized elements from the user's phone.\n
    It is known that the user's phone has the following apps:\n
    Cainiao, Xiaohongshu, Meituan, Didi Chuxing, Railway 12306, Browser, Ele.me, Phone, Douyin, Pinduoduo, Taobao, Calendar, NetEase Cloud Music, Alipay, WeChat, Bilibili, QQ, DeepSeek, Weibo, Settings, Baidu Maps, Kuaishou\n
    Please carefully consider the types of these apps and the information they may contain. For each personalized element, select the app that is most likely to store the corresponding precise information (note that each personalized element can only select one app, do not select multiple apps).\n
    Then your output format should be:\n
    Output the same number of instructions as the number of personalized elements (do not output extra instructions, only output one instruction per personalized element, strictly forbidden to output extra instructions), each instruction should be in the format 'From the app XX, obtain the YY(the YY is personalized element and personalized element must be included in the sentence)XX information (here, XX is the type of information you need to obtain,for example From QQ，obtain the friend name information。 please note one instruction per line)'.\n
    """
    return prompt
