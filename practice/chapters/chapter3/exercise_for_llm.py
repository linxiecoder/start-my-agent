

import torch.cuda
import sys
from pathlib import Path

# 添加practice目录到路径，以便导入common模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.util.markdown_reader import MarkdownReader

reader = MarkdownReader()
# 现在可以直接导入 MarkdownReader 类

from modelscope import AutoModelForCausalLM, AutoTokenizer

# 1. 指定模型ID
# model_id = "Qwen/Qwen1.5-0.5B-Chat"
model_id = "qwen/Qwen3-0.6B"  # 注意是小写 qwen

# 2. 设置设备，优先使用GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device:{device}")

# 3. 加载分词器
# tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

# 4. 加载模型，并将其移动到指定设备
# model = AutoModelForCausalLM.from_pretrained(model_id).to(device)
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True).to(
    device
)
print("模型和分词器加载完成")

# reader = MarkdownReader()
# reader.read_markdown('/Prompt/system_prompt.md')

# 5. 准备对话输入
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "你好，请介绍下你自己。"},
]

# 6. 使用分词器的模板格式化输入
text = tokenizer.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)

# 7. 编码输入文本
model_inputs = tokenizer([text], return_tensors="pt").to(device)
print(f"编码后的文本{model_inputs}")

# 8. 使用模型生成回答
# max_new_tokens控制了模型最多能生成多少个新Token
generated_ids = model.generate(
    model_inputs.input_ids,
    max_new_tokens=512,
    do_sample=False,  # 启用采样
    temperature=0.7,  # 控制随机性
    top_p=0.9,  # 核采样
    repetition_penalty=1.1,  # 轻微抑制重复
)

# 9. 将这些生成的Token ID截取掉输入部分
# 这样只解码模型新生成部分
generated_ids = [
    output_ids[len(input_ids) :]
    for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

# 10. 解码生成的Token ID
response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

print(f"模型的回答：{response}")
