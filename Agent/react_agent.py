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
        """真正的 Agent 流式执行 - 支持工具调用"""

        input_dict = {
            "messages": [
                {"role": "user", "content": query}
            ]
        }

        # 使用 stream 模式，会输出所有中间步骤
        for chunk in self.agent.stream(
                input_dict,
                stream_mode="values"
        ):
            messages = chunk.get('messages', [])
            if not messages:
                continue

            latest_message = messages[-1]

            # 判断消息类型并输出相应内容
            message_type = getattr(latest_message, 'type', None)

            # Agent 正在思考或调用工具
            if message_type == 'ai' and hasattr(latest_message, 'tool_calls') and latest_message.tool_calls:
                tool_names = [tc.get('name', 'unknown') for tc in latest_message.tool_calls]
                yield f"\n🔧 调用工具: {', '.join(tool_names)}\n"

            # 工具执行结果
            elif message_type == 'tool':
                tool_name = getattr(latest_message, 'name', 'unknown')
                yield f"✅ {tool_name} 执行完成\n"

            # LLM 的最终回答（有内容时输出）
            elif message_type == 'ai':
                content = latest_message.content
                if content and content.strip():
                    yield content

            # 用户消息（跳过，不输出）
            elif message_type == 'human':
                continue