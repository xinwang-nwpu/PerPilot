def get_action_prompt(instruction, clickable_infos, width, height, summary_history, action_history,
                      last_summary, last_action, add_info, error_flag, completed_content, memory, explore_switch, keyboard):
    prompt = "### Background Information ###\n"
    prompt += f"This is a screenshot of a phone screen, with a width of {width} pixels and a height of {height} pixels. The user's instruction is: {instruction}.\n\n"
    if explore_switch:
        prompt += f"""
        You need to help the user find the corresponding information for the personalized elements in this app based on the user's instruction.\n
        Hint 1: The information the user needs is some personalized elements, which have different meanings for different people, such as 'home' or 'friend'. Therefore, do not directly search for these elements.\n
        Hint 2: When you find information marked with ... (ellipsis), you should try to obtain the full content of the information instead of directly outputting the information with ellipsis.\n
        Hint 3: The original instruction from the user is {instruction}. The information in this instruction may help you better find the information the user needs.\n
        Remember that the above hints are only auxiliary information. You need to use your own judgment to determine if they are applicable.\n
        You need to use your thinking skills to first determine what information to find.\n
        Note that for the task, it is not better to have more information but rather to have more concise information (for example, for 'home', you generally only need to find an address; for 'good friend', you generally only need to find a name. For other types of information, you need to think about what information is needed).\n
        Then find which information in the app is most likely to represent the information you need.\n
        """
    prompt += "You need to carefully understand the content of this phone screen screenshot and help the phone user complete the above instruction.\n\n"

    prompt += "your output should not contain any coordinates.\n"
    prompt += "\n\n"

    if add_info != "":
        prompt += "### Hint Information ###\n"
        prompt += "There are some hints to help you complete the user's instruction, as follows:\n"
        prompt += add_info
        prompt += "\n\n"

    if len(action_history) > 0:
        prompt += "### Historical Actions ###\n"
        prompt += "Before reaching the current page, you have already completed some actions. You need to refer to these completed actions to decide the next action. These actions are as follows:\n"
        for i in range(len(action_history)):
            prompt += f"Step-{i + 1}: [Action Idea: " + summary_history[i].split(" to ")[0].strip() + "; Action: " + \
                      action_history[i] + "]\n"
        prompt += "\n"

    if completed_content != "":
        prompt += "### Progress Information ###\n"
        prompt += "After completing the historical actions, you have the following thoughts on the progress of the user's instruction:\n"
        prompt += "Completed content:\n" + completed_content + "\n\n"

    if memory != "":
        prompt += "### Memory Information ###\n"
        prompt += "During the operation process, you have recorded the following content on the screenshot for subsequent use:\n"
        prompt += "Memory content:\n" + memory + "\n"

    if error_flag:
        prompt += "### Last Action ###\n"
        prompt += f"You previously wanted to perform the action '{last_summary}' on the current page and executed '{last_action}'. However, you found that the action did not meet the expected result, and you need to reflect and correct it in this operation."
        prompt += "\n\n"

    prompt += "### Response Requirements ###\n"
    prompt += "Now you need to combine all the above information and perform only one action on the current page. You must choose one and only one action from the following seven actions (you can only choose one, not multiple, for example, you cannot choose to tap the search box and then search):\n"
    prompt += "tap: Tap on the current page.\n"
    prompt += "swipe: Swipe from one position to another. (please check carefully whether the sliding operation is effective.If you still don't get the desired result after swiping multiple times, please consider other methods.)\n"
    prompt += "long_press: Long press at a specified position. (Long press operations are commonly used for deleting, forwarding, copying, and other actions. When you want to copy or forward information from a social media app, you can try long pressing it to bring up the corresponding options. Note that only certain apps allow this, and you need to consider whether it was successful after performing the action. If it wasn’t successful, you need to try other methods to achieve your goal. When you need to paste copied content, you must long press in an already activated input box to bring up the paste option.)\n"
    if keyboard:
        prompt += "type: Input text in an input box.(if you need to use type, output type(content='input content'))\n"
    else:
        prompt +="Unable to type. You cannot use the action \"type\" because the keyboard has not been activated. If you want to type, you must click on the input box to activate it first\n"
    prompt += "home: Return to the phone home screen. (This is commonly used for multi-app collaboration to complete an instruction. When one app has completed its corresponding work, return to the home screen to open other apps to complete the remaining tasks.)\n"
    prompt += "back: Return to the previous page. (This is commonly used to return to the previous action after an incorrect action.)\n"
    prompt += "wait: Wait for a specified time. (This is commonly used to wait for the loading of the next page to complete. If you need to wait for a long time, you can set a long waiting time.)please only output 'wait' if you need to wait\n"
    if explore_switch:
        prompt += "Stop: If you believe all the requirements of the user's instruction have been completed and no further action is needed, you can choose this action to terminate the operation process. Then your output format is Stop|Information (this information is the information you found that the user needs, please abbreviate it to retain only the core part and discard any extra modifiers) for example, Stop|Northwestern Polytechnical University, and do not output any other information."
    else:
        prompt += "Stop: If you believe all the requirements of the user's instruction have been completed and no further action is needed, you can choose this action to terminate the operation process."
    prompt += "\n\n"
    prompt += "You must remember that every action you generate should be based on the operations that the current phone screen needs to perform, rather than generating whatever action you want to.\n"
    prompt += "### Output Format ###\n"
    prompt += "Your output consists of the following three parts:\n"
    prompt += "### Thought ### \nThink about the requirements that have been completed and the requirements that need to be completed in the next step.all your descriptions should be entirely based on the information in the picture.\n"
    prompt += "### Action ### \nDescribe your next action based on the historical action records, the current state, and the action you choose. Use concise and natural language such as 'swipe down to search box'.\n"
    return prompt


def get_process_prompt(instruction, thought_history, summary_history, action_history, completed_content, add_info):
    prompt = "### Background Information ###\n"
    prompt += f"The user has an instruction: {instruction}. You are the phone operation assistant, currently operating the user's phone.\n\n"

    if add_info != "":
        prompt += "### Hint Information ###\n"
        prompt += "There are some hints to help you complete the user's instruction, as follows:\n"
        prompt += add_info
        prompt += "\n\n"

    if len(thought_history) > 1:
        prompt += "### Historical Actions ###\n"
        prompt += "To complete the user's instruction, you have already performed a series of actions. These actions are as follows:\n"
        for i in range(len(summary_history)):
            operation = summary_history[i].split(" to ")[0].strip()
            prompt += f"Step-{i + 1}: [Action Idea: " + operation + "; Action: " + action_history[
                i] + "]\n"
        prompt += "\n"

        prompt += "### Progress Thinking ###\n"
        prompt += "After completing the historical actions, you have the following thoughts on the progress of the user's instruction:\n"
        prompt += "Completed content:\n" + completed_content + "\n\n"

        prompt += "### Response Requirements ###\n"
        prompt += "Now you need to update the 'Completed content'. The completed content is a summary of the current completed content based on the ### Historical Actions ###.\n\n"

        prompt += "### Output Format ###\n"
        prompt += "Your output format is:\n"
        prompt += "### Completed contents ###\nUpdated completed content. Do not include any purpose of the actions, only summarize the actual completed content in the ### Historical Actions ### and record some important data you think is useful for subsequent tasks.\n"

    else:
        prompt += "### Current Action ###\n"
        prompt += "To complete the user's instruction, you have already performed one action. The idea and action are as follows:\n"
        prompt += f"Action Idea: {thought_history[-1]}\n"
        operation = summary_history[-1].split(" to ")[0].strip()
        prompt += f"Action: {operation}\n\n"

        prompt += "### Response Requirements ###\n"
        prompt += "Now you need to combine all the above information to generate the 'Completed content'.\n"
        prompt += "The completed content is a summary of the current completed content. You need to focus on the requirements of the user's instruction and then summarize the completed content.\n\n"

        prompt += "### Output Format ###\n"
        prompt += "Your output format is:\n"
        prompt += "### Completed contents ###\nGenerated completed content. Do not include any purpose of the actions, only summarize the actual completed content in the ### Current Action ###.\n"

    return prompt


def solve_action_prompt():
    prompt = r"""You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task. 
    ## Output Format
    ```\nThought: ...
    Action: ...\n```
    
    ## Action Space
    click(start_box='<|box_start|>(x1,y1)<|box_end|>')
    long_press(start_box='<|box_start|>(x1,y1)<|box_end|>')
    type(content='')
    scroll(start_box='<|box_start|>(x1,y1)<|box_end|>', end_box='<|box_start|>(x3,y3)<|box_end|>')
    press_home()
    press_back()
    finished(content='') # Submit the task when you think you finish this task.
    
    ## Note
    - Use English in `Thought` part.
    
    - Write a small plan and finally summarize your next action (with its target element) in one sentence in `Thought` part.
    
    ## User Instruction
    """
    return prompt


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
    Rednote, Didi Chuxing, Browser, Contacts, Douyin, Pinduoduo, JD.com, Calendar, NetEase Cloud Music, Alipay, Bilibili, QQ, DeepSeek, Weibo, Settings, Baidu Maps, Appmarket\n
    Please carefully consider the types of these apps and the information they may contain. For each personalized element, select the app that is most likely to store the corresponding precise information (note that each personalized element can only select one app, do not select multiple apps).\n
    Then your output format should be:\n
    Output the same number of instructions as the number of personalized elements (do not output extra instructions, only output one instruction per personalized element, strictly forbidden to output extra instructions), each instruction should be in the format 'From the app XX, obtain the YY(the YY is personalized element and personalized element must be included in the sentence)XX information (here, XX is the type of information you need to obtain,such as for a person(friend,brother,mom etc.) to obtain his name information)‘,for example From QQ，obtain the friend name information.please note one instruction per line.\n
    """
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

