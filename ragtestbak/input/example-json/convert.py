import os

cur_dir = os.getcwd()

# for source in os.listdir(cur_dir):
#     name, suffix = os.path.splitext(source)
#     if suffix == '.json':
#         with open(source, 'r', encoding="utf-8") as f:
#             data = f.read()
#             data = '```json\n' + data + "\n```"
#             converted = name + '.txt'
#             with open(converted, 'w', encoding="utf-8") as nf:
#                 nf.write(data)
#             nf.close()
#         f.close()

for source in os.listdir(cur_dir):
    name, suffix = os.path.splitext(source)
    if suffix == '.json':
        os.remove(source)
        
