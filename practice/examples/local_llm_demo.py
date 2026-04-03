#!/usr/bin/env python3
"""


本地LLM使用示例

本示例演示如何使用第三章的本地LLM功能。
展示了不同模型、不同生成参数的配置和使用。

使用方法：
1. 安装依赖: pip install torch modelscope
2. 运行: python practice/examples/local_llm_demo.py

注意：首次运行会下载模型，可能需要较长时间和磁盘空间。
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_environment():
    """检查运行环境"""
    print("🔍 检查环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"❌ Python版本过低: {sys.version}")
        print("   需要Python 3.8或更高版本")
        return False
    
    print(f"   ✅ Python版本: {sys.version}")
    
    # 检查PyTorch
    try:
        import torch
        print(f"   ✅ PyTorch版本: {torch.__version__}")
        
        # 检查CUDA
        if torch.cuda.is_available():
            print(f"   🚀 CUDA可用: {torch.cuda.get_device_name(0)}")
            print(f"   💾 GPU内存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        else:
            print("   ℹ️  CUDA不可用，将使用CPU（推理速度较慢）")
            
    except ImportError:
        print("❌ PyTorch未安装")
        print("   请运行: pip install torch torchvision torchaudio")
        return False
    
    # 检查ModelScope
    try:
        import modelscope
        print(f"   ✅ ModelScope版本: {modelscope.__version__}")
    except ImportError:
        print("❌ ModelScope未安装")
        print("   请运行: pip install modelscope")
        return False
    
    return True

def basic_llm_demo():
    """基础LLM演示"""
    print("\n🚀 基础LLM演示")
    print("=" * 60)
    
    try:
        import torch
        from modelscope import AutoModelForCausalLM, AutoTokenizer
        
        # 1. 选择模型（轻量级，适合演示）
        model_id = "qwen/Qwen3-0.6B"  # 0.6B参数，相对较小
        print(f"📦 使用模型: {model_id}")
        print("   注意：首次运行会下载模型，请耐心等待...")
        
        # 2. 设置设备
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"💻 运行设备: {device}")
        
        # 3. 加载分词器
        print("🔤 加载分词器...")
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        
        # 4. 加载模型
        print("🧠 加载模型...")
        model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            trust_remote_code=True,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        ).to(device)
        
        print("✅ 模型加载完成!")
        
        # 5. 准备对话
        messages = [
            {"role": "system", "content": "你是一个有用的助手，用中文回答。"},
            {"role": "user", "content": "你好，请介绍一下你自己。"}
        ]
        
        # 6. 格式化输入
        text = tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        # 7. 编码输入
        model_inputs = tokenizer([text], return_tensors="pt").to(device)
        
        # 8. 生成回答
        print("\n🤖 生成回答中...")
        with torch.no_grad():
            generated_ids = model.generate(
                model_inputs.input_ids,
                max_new_tokens=200,  # 限制生成长度
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
        
        # 9. 解码输出
        generated_ids = [
            output_ids[len(input_ids):] 
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        print(f"💬 模型回答:\n{response}")
        
        return model, tokenizer
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def advanced_generation_demo(model, tokenizer):
    """进阶生成参数演示"""
    if model is None or tokenizer is None:
        print("❌ 模型未加载，跳过进阶演示")
        return
    
    print("\n🎛️  进阶生成参数演示")
    print("=" * 60)
    
    # 获取设备信息
    device = next(model.parameters()).device
    
    # 测试不同的生成参数
    test_cases = [
        {
            "name": "高温高随机性",
            "params": {
                "temperature": 1.0,
                "top_p": 1.0,
                "do_sample": True
            }
        },
        {
            "name": "低温低随机性",
            "params": {
                "temperature": 0.3,
                "top_p": 0.5,
                "do_sample": True
            }
        },
        {
            "name": "贪婪解码",
            "params": {
                "do_sample": False  # 贪婪解码
            }
        },
        {
            "name": "核采样",
            "params": {
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }
    ]
    
    prompt = "人工智能的未来发展方向是什么？"
    
    for i, test_case in enumerate(test_cases):
        print(f"\n📊 测试 {i+1}/{len(test_cases)}: {test_case['name']}")
        print(f"   参数: {test_case['params']}")
        
        # 准备输入
        messages = [
            {"role": "system", "content": "你是一个AI专家，请用中文简洁回答。"},
            {"role": "user", "content": prompt}
        ]
        
        text = tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        inputs = tokenizer([text], return_tensors="pt").to(device)
        
        # 生成
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=150,
                **test_case['params']
            )
        
        # 解码
        generated_ids = outputs[:, inputs.input_ids.shape[1]:]
        response = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        
        print(f"   💬 回答摘要: {response[:100]}...")
        
        # 显示token数
        input_tokens = inputs.input_ids.shape[1]
        output_tokens = generated_ids.shape[1]
        print(f"   📊 Token统计: 输入{input_tokens}个, 输出{output_tokens}个")

def model_comparison_demo():
    """模型对比演示（轻量级）"""
    print("\n📊 模型对比演示")
    print("=" * 60)
    
    # 注意：实际运行可能需要大量时间和资源
    # 这里只演示概念，不实际加载多个模型
    
    models = [
        {"id": "qwen/Qwen3-0.6B", "name": "Qwen3-0.6B", "size": "0.6B", "desc": "轻量快速"},
        {"id": "Qwen/Qwen1.5-0.5B-Chat", "name": "Qwen1.5-0.5B", "size": "0.5B", "desc": "更小更快"},
        {"id": "qwen/Qwen2.5-1.5B", "name": "Qwen2.5-1.5B", "size": "1.5B", "desc": "平衡性能"},
    ]
    
    print("可用模型对比:")
    for model in models:
        print(f"  🔸 {model['name']} ({model['size']}参数)")
        print(f"     描述: {model['desc']}")
        print(f"     Model ID: {model['id']}")
    
    print("\n💡 使用建议:")
    print("  1. 学习和测试: Qwen3-0.6B (本示例使用)")
    print("  2. 资源有限: Qwen1.5-0.5B (最小)")
    print("  3. 更好效果: Qwen2.5-1.5B (需要更多资源)")

def memory_management_tips():
    """内存管理技巧"""
    print("\n💾 内存管理技巧")
    print("=" * 60)
    
    tips = [
        "1. **使用更小的模型**: 0.5B-1.5B参数模型适合大多数CPU/8GB GPU",
        "2. **启用量化**: 使用4bit或8bit量化大幅减少内存占用",
        "3. **分批处理**: 不要一次性处理太多数据",
        "4. **使用CPU卸载**: 将部分层保留在CPU，需要时加载到GPU",
        "5. **清理缓存**: 定期调用 torch.cuda.empty_cache()",
        "6. **监控使用情况**: 使用 nvidia-smi 或 torch.cuda.memory_allocated()",
    ]
    
    for tip in tips:
        print(f"  {tip}")
    
    # 显示当前内存使用（如果可用）
    try:
        import torch
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            print(f"\n  📈 当前GPU内存: 已分配 {allocated:.2f}GB, 已保留 {reserved:.2f}GB")
    except:
        pass

def main():
    """主函数"""
    print("🤖 本地LLM使用示例")
    print("=" * 60)
    
    # 1. 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请先安装必要依赖")
        sys.exit(1)
    
    # 2. 基础演示
    model, tokenizer = basic_llm_demo()
    
    # 3. 进阶演示
    if model is not None:
        advanced_generation_demo(model, tokenizer)
    
    # 4. 模型对比
    model_comparison_demo()
    
    # 5. 内存管理
    memory_management_tips()
    
    print("\n" + "=" * 60)
    print("🎉 演示完成!")
    print("\n💡 下一步:")
    print("  1. 尝试修改模型ID，使用不同模型")
    print("  2. 调整生成参数，观察效果变化")
    print("  3. 查看 chapters/chapter3/ 了解更多实现细节")
    print("  4. 阅读 docs/chapter3/chapter3_guide.md 获取完整指南")

if __name__ == "__main__":
    main()