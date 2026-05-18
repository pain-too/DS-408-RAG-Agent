from react_agent import ReactAgent

agent = ReactAgent()

print("✅ 408考研《数据结构》答疑助手已启动！输入 exit 退出")

while True:
    user_input = input("\n你：")
    if user_input.lower() == "exit":
        print("👋 再见！")
        break

    print("\n🤖 助手正在思考...\n")
    for content in agent.execute_stream(user_input):
        print(content, end="")