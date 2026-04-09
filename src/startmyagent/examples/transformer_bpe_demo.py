#!/usr/bin/env python3
"""


Transformer与BPE算法演示

本示例演示第三章的Transformer模型实现和BPE词元化算法。
展示了从词元化到模型架构的完整流程。

使用方法：
1. 安装依赖: pip install torch
2. 运行: python practice/examples/transformer_bpe_demo.py
"""

import sys
from pathlib import Path
import numpy as np



def demonstrate_bpe_algorithm():
    """演示BPE算法"""
    print("🔤 BPE（Byte Pair Encoding）算法演示")
    print("=" * 60)
    
    try:
        # 导入BPE实现
        from startmyagent.chapters.chapter3.byte_pair_encoding import (
            get_stats, 
            merge_vocab, 
            vocab as initial_vocab
        )
        
        print("原始词表（字符级别）:")
        for word in initial_vocab:
            print(f"  '{word}'")
        
        print("\n📊 词元对频率统计:")
        pairs = get_stats(initial_vocab)
        for (a, b), freq in pairs.items():
            print(f"  ('{a}', '{b}') -> {freq}次")
        
        print("\n🔄 模拟BPE合并过程:")
        vocab = initial_vocab.copy()
        num_merges = 3
        
        for i in range(num_merges):
            pairs = get_stats(vocab)
            if not pairs:
                break
            
            # 找到频率最高的词元对
            best_pair = max(pairs, key=pairs.get)
            best_freq = pairs[best_pair]
            
            print(f"\n  第{i+1}次合并:")
            print(f"    最高频词元对: {best_pair} (出现{best_freq}次)")
            print(f"    合并为: '{''.join(best_pair)}'")
            
            # 执行合并
            vocab = merge_vocab(best_pair, vocab)
            
            print(f"    新词表: {list(vocab.keys())}")
        
        print("\n🎯 BPE算法要点:")
        print("  1. 从字符级别开始，逐步合并高频词元对")
        print("  2. 每次合并创建新的子词词元")
        print("  3. 最终得到平衡字符和单词级别的词表")
        print("  4. 能有效处理未知词和稀有词")
        
        return True
        
    except Exception as e:
        print(f"❌ BPE演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_transformer_components():
    """演示Transformer组件"""
    print("\n🧠 Transformer组件演示")
    print("=" * 60)
    
    try:
        import torch
        import torch.nn as nn
        
        print("1. 🔢 位置编码 (Positional Encoding)")
        print("   为序列中的每个位置生成唯一的编码向量")
        print("   使用正弦和余弦函数的不同频率")
        print("   帮助模型理解token的相对位置")
        
        print("\n2. 🎯 缩放点积注意力 (Scaled Dot-Product Attention)")
        print("   公式: Attention(Q, K, V) = softmax(QKᵀ/√dₖ)V")
        print("   - Q: 查询矩阵 (想要什么)")
        print("   - K: 键矩阵 (有什么)")
        print("   - V: 值矩阵 (实际内容)")
        print("   - dₖ: 键向量的维度（缩放因子）")
        
        print("\n3. 👥 多头注意力 (Multi-Head Attention)")
        print("   将注意力分割到多个'头'，分别学习不同表示")
        print("   公式: MultiHead(Q, K, V) = Concat(head₁, ..., headₕ)Wᴼ")
        print("   其中 headᵢ = Attention(QWᵢᵠ, KWᵢᴷ, VWᵢⱽ)")
        
        print("\n4. 🏗️  位置前馈网络 (Position-wise Feed Forward)")
        print("   每个位置独立应用相同的两层全连接网络")
        print("   FFN(x) = max(0, xW₁ + b₁)W₂ + b₂")
        print("   通常中间维度是输入维度的4倍")
        
        print("\n5. 🏭 编码器层 (Encoder Layer)")
        print("   包含: 多头注意力 + 前馈网络")
        print("   每个子层都有: 残差连接 + 层归一化")
        print("   公式: LayerNorm(x + Sublayer(x))")
        
        print("\n6. 🏗️  解码器层 (Decoder Layer)")
        print("   包含: 掩码多头注意力 + 编码器-解码器注意力 + 前馈网络")
        print("   掩码注意力防止看到未来token（自回归生成）")
        
        # 演示简单的注意力计算
        print("\n📐 简单注意力计算示例:")
        
        # 创建模拟数据
        batch_size = 2
        seq_len = 3
        d_model = 4
        
        # 模拟Q, K, V
        Q = torch.randn(batch_size, seq_len, d_model)
        K = torch.randn(batch_size, seq_len, d_model)
        V = torch.randn(batch_size, seq_len, d_model)
        
        print(f"   Q形状: {Q.shape}")  # [2, 3, 4]
        print(f"   K形状: {K.shape}")  # [2, 3, 4]
        print(f"   V形状: {V.shape}")  # [2, 3, 4]
        
        # 计算注意力分数
        d_k = K.size(-1)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (d_k ** 0.5)
        attention_weights = torch.softmax(scores, dim=-1)
        output = torch.matmul(attention_weights, V)
        
        print(f"   注意力分数形状: {scores.shape}")  # [2, 3, 3]
        print(f"   注意力权重形状: {attention_weights.shape}")  # [2, 3, 3]
        print(f"   输出形状: {output.shape}")  # [2, 3, 4]
        
        print("\n   📈 注意力权重示例（第一个batch，第一个位置）:")
        print(f"   {attention_weights[0, 0].detach().numpy()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Transformer演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_transformer_architecture():
    """演示完整Transformer架构"""
    print("\n🏗️  完整Transformer架构")
    print("=" * 60)
    
    try:
        # 注意：这里不实际实例化完整Transformer，因为需要大量参数
        # 只演示架构概念
        
        print("📚 架构组成:")
        
        architecture = {
            "输入处理": [
                "词嵌入层 (Token Embeddings)",
                "位置编码 (Positional Encoding)",
                "Dropout正则化"
            ],
            "编码器栈": [
                "N个相同的编码器层",
                "每层包含:",
                "  - 多头自注意力机制",
                "  - 前馈神经网络",
                "  - 残差连接 + 层归一化"
            ],
            "解码器栈": [
                "N个相同的解码器层",
                "每层包含:",
                "  - 掩码多头自注意力",
                "  - 编码器-解码器注意力",
                "  - 前馈神经网络",
                "  - 残差连接 + 层归一化"
            ],
            "输出处理": [
                "线性投影层",
                "Softmax激活",
                "生成概率分布"
            ]
        }
        
        for component, parts in architecture.items():
            print(f"\n🔸 {component}:")
            for part in parts:
                print(f"   {part}")
        
        print("\n🔄 数据流:")
        data_flow = [
            "1. 输入序列 → 词嵌入 + 位置编码",
            "2. 编码器处理 → 上下文表示",
            "3. 解码器接收: 目标序列 + 编码器输出",
            "4. 解码器生成: 下一个token的概率",
            "5. 自回归生成: 重复直到结束标记"
        ]
        
        for step in data_flow:
            print(f"   {step}")
        
        print("\n🎯 Transformer关键创新:")
        innovations = [
            "✅ 完全基于注意力机制，无需循环或卷积",
            "✅ 并行处理整个序列，训练效率高",
            "✅ 长距离依赖建模能力强",
            "✅ 可扩展性强（更多层、更大维度）",
            "✅ 适合各种序列到序列任务"
        ]
        
        for innovation in innovations:
            print(f"   {innovation}")
        
        return True
        
    except Exception as e:
        print(f"❌ 架构演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def practical_applications():
    """实际应用示例"""
    print("\n🚀 Transformer的实际应用")
    print("=" * 60)
    
    applications = [
        {
            "name": "机器翻译",
            "desc": "序列到序列的典型应用",
            "example": "英语→中文翻译",
            "model": "原始Transformer论文的应用"
        },
        {
            "name": "文本生成",
            "desc": "GPT系列模型的基础",
            "example": "故事创作、代码生成",
            "model": "GPT-2, GPT-3, GPT-4"
        },
        {
            "name": "文本分类",
            "desc": "BERT系列模型的基础",
            "example": "情感分析、垃圾邮件检测",
            "model": "BERT, RoBERTa, ALBERT"
        },
        {
            "name": "问答系统",
            "desc": "理解和回答自然语言问题",
            "example": "SQuAD数据集",
            "model": "BERT, T5, GPT-3"
        },
        {
            "name": "代码理解与生成",
            "desc": "理解和生成编程代码",
            "example": "GitHub Copilot",
            "model": "Codex, CodeT5, StarCoder"
        }
    ]
    
    print("现代AI系统的核心架构:")
    
    for app in applications:
        print(f"\n🔹 {app['name']}")
        print(f"   描述: {app['desc']}")
        print(f"   示例: {app['example']}")
        print(f"   代表模型: {app['model']}")
    
    print("\n💡 在本项目中的学习路径:")
    print("  1. 理解BPE词元化 (byte_pair_encoding.py)")
    print("  2. 掌握注意力机制 (transformer.py)")
    print("  3. 实践本地LLM调用 (use_llm.py)")
    print("  4. 构建完整AI代理 (chapter1/)")

def hands_on_exercise():
    """动手练习建议"""
    print("\n🔧 动手练习建议")
    print("=" * 60)
    
    exercises = [
        {
            "难度": "初级",
            "任务": "修改BPE合并次数",
            "目标": "观察词表变化",
            "文件": "chapters/chapter3/byte_pair_encoding.py",
            "修改": "第38行: num_merges = 4 → 修改为其他值"
        },
        {
            "难度": "初级",
            "任务": "尝试不同模型",
            "目标": "比较生成效果",
            "文件": "chapters/chapter3/use_llm.py",
            "修改": "第7行: model_id = 'qwen/Qwen3-0.6B' → 改为其他模型"
        },
        {
            "难度": "中级",
            "任务": "添加新的注意力头",
            "目标": "理解多头注意力",
            "文件": "chapters/chapter3/transformer.py",
            "修改": "第137行: num_heads参数 → 尝试不同值（需能被d_model整除）"
        },
        {
            "难度": "中级",
            "任务": "实现不同的位置编码",
            "目标": "理解位置信息的重要性",
            "文件": "chapters/chapter3/transformer.py",
            "修改": "PositionalEncoding类 → 实现可学习的位置编码"
        },
        {
            "难度": "高级",
            "任务": "添加层归一化位置",
            "目标": "理解Pre-LN vs Post-LN",
            "文件": "chapters/chapter3/transformer.py",
            "修改": "TransformerEncoderLayer类 → 尝试不同的归一化位置"
        }
    ]
    
    for ex in exercises:
        print(f"\n📝 {ex['难度']}练习: {ex['任务']}")
        print(f"   目标: {ex['目标']}")
        print(f"   文件: {ex['文件']}")
        print(f"   建议修改: {ex['修改']}")

def main():
    """主函数"""
    print("🧠 Transformer与BPE算法演示")
    print("=" * 60)
    
    print("本示例将演示:")
    print("  1. 🔤 BPE词元化算法的工作原理")
    print("  2. 🧠 Transformer核心组件的实现")
    print("  3. 🏗️  完整Transformer架构")
    print("  4. 🚀 实际应用场景")
    print("  5. 🔧 动手练习建议")
    
    # 演示BPE算法
    print("\n" + "=" * 60)
    bpe_success = demonstrate_bpe_algorithm()
    
    # 演示Transformer组件
    print("\n" + "=" * 60)
    transformer_success = demonstrate_transformer_components()
    
    # 演示完整架构
    print("\n" + "=" * 60)
    architecture_success = demonstrate_transformer_architecture()
    
    # 实际应用
    print("\n" + "=" * 60)
    practical_applications()
    
    # 动手练习
    print("\n" + "=" * 60)
    hands_on_exercise()
    
    # 总结
    print("\n" + "=" * 60)
    print("🎉 演示完成!")
    
    success_count = sum([bpe_success, transformer_success, architecture_success])
    print(f"\n📊 演示结果: {success_count}/3 个演示成功")
    
    if success_count == 3:
        print("✅ 所有演示成功完成!")
    else:
        print("⚠️  部分演示失败，请检查依赖和环境")
    
    print("\n📚 深入学习建议:")
    print("  1. 阅读原始论文: 'Attention Is All You Need'")
    print("  2. 查看可视化教程: http://jalammar.github.io/illustrated-transformer/")
    print("  3. 运行实际代码: python chapters/chapter3/transformer.py")
    print("  4. 修改参数实验: 调整模型维度、头数等参数")
    
    print("\n🔗 相关文件:")
    print("  - chapters/chapter3/byte_pair_encoding.py (BPE实现)")
    print("  - chapters/chapter3/transformer.py (Transformer实现)")
    print("  - docs/chapter3/chapter3_guide.md (详细指南)")

if __name__ == "__main__":
    main()