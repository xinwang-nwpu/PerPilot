import base64


def get_personalization_prompt(instruction, txt):
    prompt = "### Important Information ###\n"
    prompt += f"""
    Please understand and evaluate the instructions I have given you to determine if they contain personalized elements.\n
    If the instruction contains words that need to be clarified by asking the user, or if certain words have different meanings for different people or devices, it can be determined that the instruction contains personalized elements, and these words are personalized elements. You need to strictly follow the following rules:\n
    Rule 1: If certain words have unique executable meanings, such as app names like QQ and WeChat, they are not personalized elements.\n
    Rule 2: When you think something is not a personalized element, directly determine that it is not a personalized element. \n”
    Rule 3: Strictly prohibit treating specific names as personalized elements, whether they are Chinese or English names. But abstract names are still personalized elements, such as friends.\n
    Rule 4:This personalized information has already been processed and no longer needs to be exported, and the processed information is as follows:\n{txt}\n
    Rule 5: If the instruction produces the same result regardless of whether personalized elements are processed, then it is not a personalized instruction.\n
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
    Rednote, Didi Chuxing, Browser, Contacts, Douyin, Pinduoduo, JD.com, Calendar, NetEase Cloud Music, Alipay, Bilibili, QQ, DeepSeek, Weibo, Settings, Baidu Maps, Appmarket\n
    Please carefully consider the types of these apps and the information they may contain. For each personalized element, select the app that is most likely to store the corresponding precise information (note that each personalized element can only select one app, do not select multiple apps).\n
    Then your output format should be:\n
    Output the same number of instructions as the number of personalized elements (do not output extra instructions, only output one instruction per personalized element, strictly forbidden to output extra instructions), each instruction should be in the format 'From the app XX, obtain the YY(the YY is personalized element and personalized element must be included in the sentence)XX information (here, XX is the type of information you need to obtain,such as for a person or place(friend,brother,mom,school,etc.) to obtain his name information)‘,for example From QQ，obtain the friend name information.please note one instruction per line.\n
    """
    return prompt



def encode_image(image_path):
    """将图片编码为base64格式，以便发送给API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def create_message_prompt(command):
    prompt = """
        You are a Senior Mobile Phone User with rich experience in operating various mobile devices and accurately identifying changes in mobile interfaces. 
        Your core task is to judge whether a given Mobile Phone Command has been successfully executed, based on two provided images: 
        the Initial State Image (showing the mobile phone's interface/status before the command is run) and the Post-Command State Image 
        (showing the mobile phone's interface/status after attempting to execute the command).

        To complete this judgment, follow these steps strictly:
        1. First, carefully observe the Initial State Image to fully grasp the phone's starting condition.
        2. Then, clearly understand the specific requirement of the Mobile Phone Command.
        3. Next, thoroughly examine the Post-Command State Image and compare it with the Initial State Image. 
           Focus on whether the changes required by the Mobile Phone Command have actually occurred.

        If the Post-Command State Image clearly shows that the exact requirement of the Mobile Phone Command has been fulfilled, 
        output "Success". Otherwise, output "Failed" 然后用中文阐述失败的原因。

        Mobile Phone Command: {command}
        """.format(command=command)
    return prompt


def create_all_message_prompt(command):
    prompt = """
        You are a Senior Mobile Phone User with rich experience in operating various mobile devices 
        and accurately identifying changes in mobile interfaces. Your core task is to judge whether 
        a given Mobile Phone Command has been successfully executed, based on **all provided images** 
        (including but not limited to the Initial State Image showing the mobile phone's interface/status 
        before the command is run, the Post-Command State Image showing the interface/status after 
        attempting to execute the command, and any intermediate state images if available).

        To complete this judgment, follow these steps strictly:
        1. First, from all provided images, accurately identify and carefully observe the **Initial State Image** 
           to fully grasp the phone's interface/status before the command is executed.
        2. Then, clearly understand the specific requirement and expected effect of the given Mobile Phone Command.
        3. Next, systematically examine all other images (focusing on the Post-Command State Image first, 
           and using intermediate state images as auxiliary references if any), and conduct a detailed 
           comparison with the Initial State Image. The key focus is to confirm whether the exact changes 
           required by the Mobile Phone Command have actually occurred in the final state.

        Output format requirements:
        - First, output "Success" or "Failed" on the first line
        - Then, start a new line and provide the reason in English
        - Regardless of success or failure, you must specify which images were compared to reach the conclusion
        - For text input commands, it is only necessary to determine whether the text is the specified character symbol; for example,It doesn't matter if there are missing spaces.

        Example for success:
        "Success
        from the initial state image and post-command state image, it is clear that the command requirement of 'enable bluetooth' has been fulfilled, and the bluetooth icon has changed to a blue enabled state."

        Example for failure:
        "Failed
        from the initial state image and post-command state image, it is clear that the command requirement of 'enable bluetooth' has not been fulfilled, and the bluetooth icon remains in a gray disabled state."

        Mobile Phone Command: {command}
    """.format(command=command)
    return prompt


def verify_per_prompt(txt):
    with open("pre.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()
        prompt = f"""
           Please do the following text matching task:
           1. Task
           The user will give you two things:
           1.1 target text in "X|Y" format (e.g., "friend|Li Ming"; "X" = relationship/category, "Y" = specific name/object).
           2.Content from multiple txt files (each has "a|b" lines; ignore non-"a|b" content).
           Your job: Check if any "a|b" from the txts is consistent in meaning with "X|Y". Return "yes" if there is, "no" if not.

           2. "Consistent in Meaning" Rule
           Both must be true:
           "a" has the same meaning as "X" (e.g., "friend" = "pal", "teacher" = "lǎoshī").
           "b" refers to the same thing/person as "Y" (e.g., "Li Ming" = "Xiao Li", "Peking University" = "Beida").

           3. Output
           Only return "yes" or "no" (lowercase, no extra words/punctuation).

           The required data is as follows:
           1. The target text is: {txt}
           2. The content from multiple txt files is as follows:
           {lines}
           """
    return prompt
