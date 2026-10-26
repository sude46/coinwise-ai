"""储蓄目标相关事件"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class SavingsGoalCreated:
    user_id: int
    goal_id: int
    target_amount: float


@dataclass
class SavingsGoalProgressUpdated:
    user_id: int
    goal_id: int
    old_amount: float
    new_amount: float