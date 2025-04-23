import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")


from llm.free import open_router_API, project_name, env, client_url

print(env)
print(open_router_API)
print(project_name)
print(client_url)