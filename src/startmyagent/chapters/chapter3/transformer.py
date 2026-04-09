import math

import torch
import torch.nn as nn

"""
torch 是 PyTorch 框架的核心库。

在你之前看到的代码中，nn.LayerNorm、nn.Dropout 等模块都来自 torch.nn 子模块。简单来说：

torch 本身提供了张量（Tensor）运算、自动求导（Autograd）、GPU加速等底层功能。

torch.nn 则构建在 torch 之上，提供了构建神经网络所需的各种层（如 Linear、LayerNorm、Dropout）、损失函数和容器（如 Module）。
"""


# --- 占位符模块，在后续小节中实现 ---

class PositionalEncoding(nn.Module):
    """
    位置编码模块
    """

    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super.__init__()
        self.dropout = nn.Dropout(p=dropout)

        # 创建一个足够长的位置编码矩阵
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))

        # PE的大小为(max_len, d_model)
        pe = torch.zero_(max_len, d_model)

        # 偶数维度使用sin，奇数维度使用cos
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        # 将pe注册为buffer，这样他就不会被视为模型参数，但会随模型移动
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x):
        # x.size(1)是当前输入的序列长度
        # 将位置编码加入到输入向量中
        x = x + self.pe[:, :x.size(1)]
        return self.dropout(x)


class MultiHeadAttention(nn.Module):
    """
    多头注意力机制模块
    """

    def __init__(self, d_model, num_heads):
        super(MultiHeadAttention, self).__init__()
        assert d_model % num_heads == 0, "d_model % num_heads is not 0"
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        # 定义Q,K,V和输出的线性变换层
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_out = nn.Linear(d_model, d_model)

    def scaled_dot_product_attention(self, Q, K, V, mask=None):
        # 1. 计算注意力得分（QK^T）
        attn_scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        # 2. 应用掩码（如果提供）
        if mask is not None:
            # 将掩码中为0的位置设置为一个非常小的负数，这样softmax后会非常接近0
            attn_scores = attn_scores.masked_fill(mask == 0, -1e9)

        # 3. 计算注意力权重（softmax）
        attn_probs = torch.softmax(attn_scores, dim=-1)

        # 4. 加权求和（权重*V）
        output = torch.matmul(attn_probs, V)
        return output

    def split_heads(self, x):
        # 将输入的x的形状从（batch_size，seq_length，d_model）
        # 变换为（batch_size，num_heads，seq_length，d_k）
        batch_size, seq_length, d_model = x.size()
        return x.view(batch_size, seq_length, self.num_heads, self.d_k).transpose(1, 2)

    def combine_heads(self, x):
        # 将输入的x的形状从（batch_size，num_heads，seq_length，d_k）
        # 变换为（batch_size，seq_length，d_model）
        batch_size, num_heads, seq_length, d_k = x.size()
        return x.transpose(1, 2).contiguous().view(batch_size, seq_length, self.d_model)

    def forward(self, query, key, value, mark=None):
        # 1. 对Q、K、V进行线性变换
        Q = self.split_heads(self.W_q(query))
        K = self.split_heads(self.W_k(key))
        V = self.split_heads(self.W_v(value))

        # 2. 计算缩放点积注意力
        attn_output = self.scaled_dot_product_attention(Q, K, V, mark)

        # 3. 合并多头输出并进行最终线性变换
        output = self.combine_heads(attn_output)
        return output


class PositionWiseFeedForward(nn.Module):
    """
    位置前馈网络模块
    """

    def __init__(self, d_model, d_ff, dropout=0.1):
        super(PositionWiseFeedForward, self).__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.relu = nn.ReLU()

    def forward(self, x):
        # x的形状（batch_size，seq_length，d_model）
        x = self.linear1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.linear2(x)
        # 最终形状：（batch_size，seq_length，d_model）
        return x


# --- 编码器核心层 ---

class EncoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout):
        super(EncoderLayer, self).__init__()
        self.self_attn = MultiHeadAttention()  # 待实现
        self.feed_forward = PositionWiseFeedForward()  # 待实现
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask):
        # 残差连接与层归一化在后续小节详解
        # 1. 多头自注意力
        attn_output = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))

        # 2. 前馈网络
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_output))

        return x


# --- 解码器核心层 ---
class DecoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout):
        super(DecoderLayer, self).__init__()
        self.self_attn = MultiHeadAttention()  # 待实现
        self.cross_attn = MultiHeadAttention()  # 待实现
        self.feed_forward = PositionWiseFeedForward()  # 待实现
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, encoder_output, src_mask, tgt_mask):
        # 1. 掩码多头自注意力（对自己）
        attn_output = self.self_attn(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout(attn_output))

        # 2. 交叉注意力（对编码器输出）
        cross_attn_output = self.cross_attn(x, encoder_output, encoder_output, src_mask)
        x = self.norm2(x + self.dropout(cross_attn_output))

        # 3. 前馈网络
        ff_output = self.feed_forward(x)
        x = self.norm3(x + self.dropout(ff_output))

        return x
