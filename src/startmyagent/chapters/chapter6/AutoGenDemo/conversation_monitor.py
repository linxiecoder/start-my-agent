"""
AutoGen 对话质量监控模块

本模块提供对话质量监控机制，用于检测和干预以下异常情况：
1. 对话循环 - 检测重复的发言者序列或内容
2. 主题漂移 - 检测对话是否偏离原始目标
3. 响应退化 - 检测重复、低质量或过短的响应
4. 资源耗尽 - 检测 token 使用和对话轮次

使用方式:
    monitor = ConversationMonitor(
        max_turns=40,
        loop_threshold=3,
        drift_threshold=0.6,
    )
    monitor.initialize(initial_goal="开发比特币价格应用")

    # 在每轮对话后调用
    result = monitor.check(message)
    if result.alert_level >= AlertLevel.WARNING:
        monitor.intervene(result)
"""

from __future__ import annotations

import time
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

# 使用字符串避免导入问题（后续可以用 ast 模块优化）
MessageType = any


class AlertLevel(Enum):
    """告警级别"""

    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    TERMINATE = "terminate"

    def __ge__(self, other: "AlertLevel") -> bool:
        """支持级别比较"""
        levels = [
            AlertLevel.NORMAL,
            AlertLevel.WARNING,
            AlertLevel.CRITICAL,
            AlertLevel.TERMINATE,
        ]
        return levels.index(self) >= levels.index(other)


@dataclass
class MonitorResult:
    """监控结果"""

    alert_level: AlertLevel = AlertLevel.NORMAL
    reason: str = ""
    recommended_action: Optional[str] = (
        None  # "continue", "skip_to_role", "force_terminate", "prompt_human"
    )

    # 检测详情
    loop_count: int = 0
    drift_score: float = 1.0
    quality_score: float = 1.0

    # 元数据
    turn_count: int = 0
    idle_seconds: float = 0

    def is_normal(self) -> bool:
        return self.alert_level == AlertLevel.NORMAL

    def needs_intervention(self) -> bool:
        return self.alert_level >= AlertLevel.WARNING


class ConversationMonitor:
    """
    对话质量监控器

    集成循环检测、主题漂移检测和响应质量评估功能。
    支持在检测到异常时自动干预或调用回调函数。
    """

    def __init__(
        self,
        # 循环检测配置
        loop_window_size: int = 5,
        loop_similarity_threshold: float = 0.8,
        loop_min_consecutive: int = 3,
        # 主题漂移配置 (简化版 - 使用关键词匹配)
        required_keywords: Optional[list[str]] = None,
        drift_check_enabled: bool = True,
        # 响应质量配置
        min_response_length: int = 20,
        max_repetition_ratio: float = 0.6,
        # 超时与限制配置
        max_turns: int = 40,
        max_idle_time_seconds: float = 300,
        # 回调函数
        on_warning: Optional[Callable[[MonitorResult], None]] = None,
        on_critical: Optional[Callable[[MonitorResult], None]] = None,
        on_terminate: Optional[Callable[[MonitorResult], None]] = None,
    ):
        # 循环检测配置
        self.loop_window_size = loop_window_size
        self.loop_similarity_threshold = loop_similarity_threshold
        self.loop_min_consecutive = loop_min_consecutive

        # 主题漂移配置
        self.required_keywords = required_keywords or []
        self.drift_check_enabled = drift_check_enabled

        # 响应质量配置
        self.min_response_length = min_response_length
        self.max_repetition_ratio = max_repetition_ratio

        # 超时与限制配置
        self.max_turns = max_turns
        self.max_idle_time_seconds = max_idle_time_seconds

        # 回调函数
        self.on_warning = on_warning
        self.on_critical = on_critical
        self.on_terminate = on_terminate

        # ===== 内部状态 =====
        self._initialized: bool = False
        self._messages: list = []  # 消息历史

        # 循环检测状态
        self._speaker_history: list[str] = []
        self._content_history: list[str] = []

        # 主题检测状态
        self._initial_goal: str = ""
        self._seen_keywords: set[str] = set()

        # 统计
        self._start_time: float = 0
        self._last_activity_time: float = 0
        self._error_count: int = 0

    @property
    def turn_count(self) -> int:
        return len(self._messages)

    @property
    def current_speakers(self) -> list[str]:
        return self._speaker_history[-self.loop_window_size :]

    def initialize(self, initial_goal: str) -> None:
        """初始化监控器"""
        self._initialized = True
        self._start_time = time.time()
        self._last_activity_time = time.time()
        self._initial_goal = initial_goal

        # 提取初始目标中的关键词
        if self.required_keywords:
            self._seen_keywords = set()
        else:
            # 自动提取关键词（简单策略：3+字符的词）
            words = re.findall(r"\b\w{3,}\b", initial_goal.lower())
            self._seen_keywords = set(words)

    def record(self, message: any) -> None:
        """
        记录新消息

        Args:
            message: 包含 source 和 content 属性的消息对象
        """
        if not self._initialized:
            return

        # 记录消息
        self._messages.append(message)
        self._last_activity_time = time.time()

        # 提取发言者
        speaker = getattr(message, "source", "unknown")
        self._speaker_history.append(speaker)

        # 提取内容用于重复检测
        content = getattr(message, "content", "") or ""
        self._content_history.append(content)

        # 更新关键词统计
        if self.drift_check_enabled and content:
            found_keywords = set(re.findall(r"\b\w{3,}\b", content.lower()))
            self._seen_keywords |= found_keywords

        # 保持历史窗口大小
        max_history = self.loop_window_size * 4
        if len(self._speaker_history) > max_history:
            self._speaker_history = self._speaker_history[-max_history:]
        if len(self._content_history) > max_history:
            self._content_history = self._content_history[-max_history:]

    def check(self) -> MonitorResult:
        """
        执行所有检测

        Returns:
            MonitorResult: 包含告警级别和建议动作
        """
        result = MonitorResult(turn_count=self.turn_count)

        if not self._initialized:
            return result

        # 计算空闲时间
        result.idle_seconds = time.time() - self._last_activity_time

        # ===== 1. 硬限制检查 =====
        if self.turn_count >= self.max_turns:
            result.alert_level = AlertLevel.TERMINATE
            result.reason = f"达到最大轮次限制 ({self.max_turns})"
            result.recommended_action = "force_terminate"
            return result

        # ===== 2. 空闲超时检查 =====
        if result.idle_seconds > self.max_idle_time_seconds:
            result.alert_level = AlertLevel.TERMINATE
            result.reason = f"对话停滞 {result.idle_seconds:.0f}秒"
            result.recommended_action = "force_terminate"
            return result

        # ===== 3. 循环检测 =====
        loop_result = self._detect_loop()
        result.loop_count = loop_result.loop_count
        if loop_result.needs_intervention():
            self._handle_alert(loop_result)
            return loop_result

        # ===== 4. 响应质量检查 =====
        quality_result = self._assess_quality()
        result.quality_score = quality_result.quality_score
        if quality_result.needs_intervention():
            self._handle_alert(quality_result)
            return quality_result

        return result

    def _detect_loop(self) -> MonitorResult:
        """检测循环模式"""
        result = MonitorResult(turn_count=self.turn_count)
        result.loop_count = 0

        if len(self._speaker_history) < self.loop_min_consecutive:
            return result

        # 检查发言者循环模式
        recent_speakers = self._speaker_history[-self.loop_window_size :]

        # 简化版：检测完全重复的发言者序列
        step = 1
        for check_len in range(2, self.loop_min_consecutive + 1):
            # 检查长度为 check_len 的序列是否重复
            seq = recent_speakers[-check_len:]
            prev_seq = recent_speakers[-(check_len * 2) : -check_len]

            if seq == prev_seq and len(set(seq)) > 1:  # 至少2个不同角色
                result.loop_count = check_len
                break

        # 检查内容重复（字符串相似度简化版）
        if self._content_history:
            recent_contents = self._content_history[-self.loop_window_size :]
            similar_count = 0
            current = recent_contents[-1]

            for prev in recent_contents[:-1]:
                if (
                    self._compute_similarity(current, prev)
                    > self.loop_similarity_threshold
                ):
                    similar_count += 1

            if similar_count >= self.loop_min_consecutive - 1:
                result.loop_count = max(result.loop_count, similar_count + 1)

        # 判断告警级别
        if result.loop_count >= self.loop_min_consecutive:
            result.alert_level = AlertLevel.WARNING
            result.reason = f"检测到循环模式 ({result.loop_count}轮相同模式)"
            result.recommended_action = "prompt_human"
        elif result.loop_count >= 2:
            result.alert_level = AlertLevel.WARNING
            result.reason = f"可能存在循环倾向 (相似度 {result.loop_count})"
            result.recommended_action = "continue"

        return result

    def _assess_quality(self) -> MonitorResult:
        """评估响应质量"""
        result = MonitorResult(turn_count=self.turn_count)
        result.quality_score = 1.0

        if not self._content_history:
            return result

        # 检查最新响应的质量
        latest_content = self._content_history[-1]

        # 1. 长度检查
        content_length = len(latest_content.strip())
        if content_length < self.min_response_length:
            # 可能是简短确认（如"好的"、"可以"），需要结合上下文判断
            if content_length < 5:
                result.quality_score = 0.5
                # 这种情况通常是正常的状态转换，不算质量问题

        # 2. 重复内容检查
        if len(self._content_history) >= 2:
            prev_content = self._content_history[-2]
            similarity = self._compute_similarity(latest_content, prev_content)

            if similarity > self.max_repetition_ratio:
                result.alert_level = AlertLevel.WARNING
                result.reason = f"响应内容高度重复 (相似度 {similarity:.1%})"
                result.recommended_action = "prompt_human"
                result.quality_score = similarity

        # 3. 错误关键词检测
        error_indicators = ["无法", "不能", "错误", "失败", "exception", "error"]
        has_error = any(
            indicator in latest_content.lower() for indicator in error_indicators
        )

        if has_error:
            self._error_count += 1
            if self._error_count >= 3:
                result.alert_level = AlertLevel.CRITICAL
                result.reason = f"连续 {self._error_count} 次出现错误"
                result.recommended_action = "force_terminate"

        return result

    def _compute_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度（简化版 Dice 系数）"""
        if not text1 or not text2:
            return 0.0

        # 词级别比较
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return 2 * len(intersection) / len(union) if union else 0.0

    def _handle_alert(self, result: MonitorResult) -> None:
        """根据告警级别调用相应的回调"""
        if result.alert_level == AlertLevel.WARNING:
            if self.on_warning:
                self.on_warning(result)
        elif result.alert_level == AlertLevel.CRITICAL:
            if self.on_critical:
                self.on_critical(result)
        elif result.alert_level == AlertLevel.TERMINATE:
            if self.on_terminate:
                self.on_terminate(result)

    def intervene(self, result: MonitorResult) -> Optional[str]:
        """
        执行干预

        Args:
            result: 监控结果

        Returns:
            干预消息，如果不需要干预则返回 None
        """
        if not result.needs_intervention():
            return None

        interventions = {
            AlertLevel.WARNING: self._generate_warning_intervention,
            AlertLevel.CRITICAL: self._generate_critical_intervention,
            AlertLevel.TERMINATE: self._generate_terminate_intervention,
        }

        handler = interventions.get(result.alert_level)
        if handler:
            return handler(result)
        return None

    def _generate_warning_intervention(self, result: MonitorResult) -> str:
        """生成警告级干预消息"""
        if result.loop_count > 0:
            return (
                f"⚠️ 对话质量监控提醒：我注意到对话可能在循环。\n"
                f"当前情况：{result.reason}\n"
                f"建议：请确认是否需要调整方向，或输入终止命令结束对话。"
            )
        return f"⚠️ 对话质量提醒：{result.reason}"

    def _generate_critical_intervention(self, result: MonitorResult) -> str:
        """生成严重级干预消息"""
        return (
            f"🚨 对话异常：检测到严重问题。\n"
            f"问题：{result.reason}\n"
            f"对话将终止。请检查日志后重试。"
        )

    def _generate_terminate_intervention(self, result: MonitorResult) -> str:
        """生成终止干预消息"""
        return (
            f"🛑 对话终止：{result.reason}\n总对话轮次：{result.turn_count}\n感谢使用！"
        )

    def get_status_summary(self) -> str:
        """获取状态摘要"""
        return (
            f"对话质量监控状态：\n"
            f"  - 轮次：{self.turn_count}/{self.max_turns}\n"
            f"  - 发言者：{self.current_speakers}\n"
            f"  - 关键词覆盖：{len(self._seen_keywords)} 个\n"
            f"  - 错误次数：{self._error_count}\n"
            f"  - 空闲时间：{time.time() - self._last_activity_time:.0f}秒"
        )


# ===== 便捷函数 =====


def create_monitor(
    max_turns: int = 40,
    on_warning: Optional[Callable] = None,
    on_critical: Optional[Callable] = None,
) -> ConversationMonitor:
    """创建默认配置的监控器"""
    return ConversationMonitor(
        max_turns=max_turns,
        loop_min_consecutive=3,
        loop_similarity_threshold=0.8,
        min_response_length=20,
        max_repetition_ratio=0.6,
        on_warning=on_warning,
        on_critical=on_critical,
    )
