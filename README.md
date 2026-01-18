# 单臂拖拽录制脚本使用指南

## 简介

`drag_and_record.py` （没有使用归一化参数）和`drag_and_record_v2.py` 是一个用于 SO-101 Follower 机械臂的单臂拖拽录制脚本。

**作者**：xiao  
**日期**：2026年1月

## 为什么创建这个脚本？

原版 LeRobot 需要 Leader 臂和 Follower 臂配合使用来录制数据。但对于只有 Follower 臂的用户，无法使用标准的遥操作录制功能。

本脚本通过关闭电机扭矩，允许用户直接用手拖动机械臂来录制动作轨迹，然后开启扭矩回放动作。

## 功能特点

- ✅ 无需 Leader 臂
- ✅ 支持归一化位置值
- ✅ 加载校准数据
- ✅ 实时显示关节位置
- ✅ 轨迹保存为 JSON 格式
- ✅ 支持动作回放

## 使用方法

### 前置条件

1. 已安装 LeRobot
2. 已完成机械臂校准：
```bash
   lerobot-calibrate \
       --robot.type=so101_follower \
       --robot.port=/dev/ttyACM0 \
       --robot.id=your_arm_id
```

### 运行脚本
```bash
cd ~/lerobot
python drag_and_record.py
```

### 操作流程

1. 选择 **1. 录制新动作**
2. 输入录制时长
3. 扭矩关闭后，用手拖动机械臂完成动作
4. 按 Enter 开始录制
5. 录制完成后，选择是否立即回放

## 配置说明

在脚本开头可以修改以下配置：
```python
PORT = "/dev/ttyACM0"  # 串口端口
RECORD_FPS = 30        # 录制帧率
RECORD_FILE = "recorded_trajectory.json"  # 保存文件名
CALIBRATION_FILE = "/home/xiao/.cache/huggingface/lerobot/calibration/robots/so101_follower/xiao_follower_arm.json"  # 校准文件路径
```

## 数据格式

录制的轨迹保存为 JSON 格式：
```json
[
  {
    "timestamp": 0.0,
    "positions": [-5.2, 12.3, 45.0, -10.5, 20.0, 50.0]
  },
  {
    "timestamp": 0.033,
    "positions": [-5.1, 12.5, 45.2, -10.3, 20.2, 50.0]
  }
]
```

- `timestamp`: 时间戳（秒）
- `positions`: 6个电机的归一化位置（-100 到 +100）

## 后续计划

- [ ] 添加摄像头支持
- [ ] 转换为 LeRobot 数据集格式
- [ ] 支持 AI 模型训练
```

4. 在下方填写 Commit message：
```
   Add documentation for drag and record script
