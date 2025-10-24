# PerPilot

## 📋 Project Overview

Large multi-model (LMM)-based mobile agents show great potential for assisting users in performing instruction-driven tasks. However, these agents typically struggle with **personalized instructions**—those containing ambiguous, user-specific context—a challenge that has been largely overlooked in previous research.

This repository presents **PerPilot**, an innovative framework designed to address the critical gap in personalized instruction handling for next-generation mobile agents.

## 🔍 Core Challenge

Modern mobile agents face significant limitations when processing:

* Ambiguous user requests requiring contextual understanding

* User-specific instructions depends on personal preferences or historical interactions

* Task execution in diverse mobile scenarios with minimal intervention

## 💡 Our Solution

We introduce two key innovations to address these challenges:

### 1. PerInstruct Dataset

A novel human-annotated dataset featuring:

* Diverse personalized instructions across various mobile scenarios

* Rich contextual information for training and evaluation

* Comprehensive coverage of real-world user interaction patterns

### 2. PerPilot Framework

A plug-and-play architecture powered by large language models (LLMs) that enables mobile agents to:

* Autonomously perceive personalized elements in user instructions

* Understand context-specific requirements

* Execute complex tasks with minimal user input

## 🚀 Key Features

PerPilot employs two complementary approaches for personalized task completion:

| Approach                        | Description                                                               |
| ------------------------------- | ------------------------------------------------------------------------- |
| **Memory-based Retrieval**      | Leverages historical user data to provide contextually relevant responses |
| **Reasoning-based Exploration** | Uses LLM-powered reasoning to handle novel or ambiguous instructions      |

Fully automatic execution and verification of instructions.

For users, it is easy to expand the instruction benchmark.

## 📊 Experimental Results

Our evaluations demonstrate that PerPilot:

* Effectively handles personalized tasks with minimal user intervention

* Progressively improves performance with continued use

* Outperforms existing mobile agents in context-aware task execution

* Establishes the importance of personalization-aware reasoning for next-generation agents

## 📱 Get Start
The project provides two operating environments: real mobile phones and mobile simulators.

1.real mobile phones
To run on a real phone, you first need to download the ADB Keyboard and then set the default input method to ADB Keyboard.
https://github.com/senzhk/ADBKeyBoard




2.mobile simulator
This project is implemented based on the MUMU emulator, which is an emulator compatible with Chinese apps.
To reproduce it, you need to download this emulator from the link now.
link is https://mumu.163.com/








## 📝 Conclusion

PerPilot represents a significant step forward in creating more intuitive and user-centric mobile agents. By combining memory-based retrieval with advanced reasoning capabilities, our framework paves the way for more natural human-machine interaction in mobile environments.



