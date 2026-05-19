# 第三方库
from langchain.agents import create_agent
# 项目模块
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from tools.agent_tools import ds_knowledge_search, ds_concept_compare, ds_chapter_summary


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[ds_knowledge_search, ds_concept_compare, ds_chapter_summary],
        )

    def execute_stream(self, query: str):
        """
        Agent 流式执行 - 支持工具调用
        LangChain标准消息格式：字典，且字典的值是列表套字典
        """
        input_dict = {
            "messages": [
                {"role": "user", "content": query}
            ]
        }

        # 使用 values 模式，会输出所有if,elif判断的结果
        for chunk in self.agent.stream(input_dict, stream_mode="values"):
            messages = chunk.get('messages', [])
            if not messages:
                continue

            latest_message = messages[-1]
            # 判断消息类型并输出，没有就返回None
            message_type = getattr(latest_message, 'type', None)

            # 判断 Agent 是否在思考或调用工具
            if message_type == 'ai' and hasattr(latest_message, 'tool_calls') and latest_message.tool_calls:
                # 获取所有AI调用的工具名，返回成列表并流式输出
                tool_names = [tc.get('name', 'unknown') for tc in latest_message.tool_calls]
                yield f"\n🔧  {', '.join(tool_names)} 正在被调用  \n"

            # 执行完工具后才会有tool类型的消息
            elif message_type == 'tool':
                tool_name = getattr(latest_message, 'name', 'unknown')
                yield f"✅ {tool_name} 执行完成  \n"

            # LLM 的最终回答（有内容时输出，兜底强制输出）
            elif message_type == 'ai':
                content = latest_message.content
                if content and content.strip():
                    yield content

            # 用户消息（跳过，不输出）
            elif message_type == 'human':
                continue