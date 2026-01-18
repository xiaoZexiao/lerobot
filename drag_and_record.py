#!/usr/bin/env python3
"""
手动拖动录制脚本
"""

import time
import json
from pathlib import Path

from lerobot.motors.feetech import FeetechMotorsBus
from lerobot.motors.motors_bus import Motor, MotorNormMode

# ========== 配置 ==========
PORT = "/dev/ttyACM0"  # 改成你的端口
RECORD_FPS = 30
RECORD_FILE = "recorded_trajectory.json"

# 电机名称列表
MOTOR_NAMES = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]

# SO-101 电机配置
MOTORS = {
    "shoulder_pan": Motor(1, "sts3215", MotorNormMode.RANGE_M100_100),
    "shoulder_lift": Motor(2, "sts3215", MotorNormMode.RANGE_M100_100),
    "elbow_flex": Motor(3, "sts3215", MotorNormMode.RANGE_M100_100),
    "wrist_flex": Motor(4, "sts3215", MotorNormMode.RANGE_M100_100),
    "wrist_roll": Motor(5, "sts3215", MotorNormMode.RANGE_M100_100),
    "gripper": Motor(6, "sts3215", MotorNormMode.RANGE_0_100),
}

def connect_motors():
    """连接电机"""
    motors = FeetechMotorsBus(
        port=PORT,
        motors=MOTORS,
    )
    motors.connect()
    print("电机已连接")
    return motors

def disable_torque(motors):
    """关闭扭矩"""
    for name in MOTOR_NAMES:
        motors.write("Torque_Enable", name, 0, normalize=False)
    print("扭矩已关闭 - 现在可以用手移动机械臂")

def enable_torque(motors):
    """开启扭矩"""
    for name in MOTOR_NAMES:
        motors.write("Torque_Enable", name, 1, normalize=False)
    print("扭矩已开启")

def read_positions(motors):
    """读取当前所有电机位置"""
    positions = []
    for name in MOTOR_NAMES:
        pos = motors.read("Present_Position", name, normalize=False)
        positions.append(pos)
    return positions

def write_positions(motors, positions):
    """写入所有电机位置"""
    for name, pos in zip(MOTOR_NAMES, positions):
        motors.write("Goal_Position", name, pos, normalize=False)

def record_trajectory(motors, duration=10):
    """录制轨迹"""
    print(f"\n开始录制，时长 {duration} 秒...")
    print("请用手移动机械臂完成动作")
    print("按 Ctrl+C 提前结束录制\n")
    
    trajectory = []
    interval = 1.0 / RECORD_FPS
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            positions = read_positions(motors)
            timestamp = time.time() - start_time
            trajectory.append({
                "timestamp": timestamp,
                "positions": positions
            })
            time.sleep(interval)
            elapsed = int(time.time() - start_time)
            print(f"\r录制中... {elapsed}/{duration}秒 | 已记录 {len(trajectory)} 帧", end="", flush=True)
            
    except KeyboardInterrupt:
        print("\n录制被手动停止")
    
    print(f"\n录制完成！共 {len(trajectory)} 帧")
    return trajectory

def save_trajectory(trajectory, filename):
    """保存轨迹"""
    with open(filename, 'w') as f:
        json.dump(trajectory, f, indent=2)
    print(f"轨迹已保存到: {filename}")

def load_trajectory(filename):
    """加载轨迹"""
    with open(filename, 'r') as f:
        trajectory = json.load(f)
    print(f"已加载轨迹: {len(trajectory)} 帧")
    return trajectory

def replay_trajectory(motors, trajectory):
    """回放轨迹"""
    print("\n开始回放轨迹...")
    print("按 Ctrl+C 停止回放\n")
    
    try:
        for i, frame in enumerate(trajectory):
            positions = frame["positions"]
            write_positions(motors, positions)
            
            if i < len(trajectory) - 1:
                wait_time = trajectory[i+1]["timestamp"] - frame["timestamp"]
                time.sleep(max(0, wait_time))
            
            print(f"\r回放中... {i+1}/{len(trajectory)}", end="", flush=True)
            
    except KeyboardInterrupt:
        print("\n回放被手动停止")
    
    print("\n回放完成！")

def main():
    print("=" * 50)
    print("       手动拖动录制工具")
    print("=" * 50)
    
    motors = connect_motors()
    
    while True:
        print("\n请选择操作:")
        print("1. 录制新动作")
        print("2. 回放上次录制的动作") 
        print("3. 退出")
        
        choice = input("\n请输入选项 (1/2/3): ").strip()
        
        if choice == "1":
            duration = input("请输入录制时长（秒，默认10）: ").strip()
            duration = int(duration) if duration else 10
            
            disable_torque(motors)
            input("\n按 Enter 开始录制...")
            
            trajectory = record_trajectory(motors, duration)
            save_trajectory(trajectory, RECORD_FILE)
            
            replay = input("\n是否立即回放？(y/n): ").strip().lower()
            if replay == 'y':
                enable_torque(motors)
                time.sleep(0.5)
                replay_trajectory(motors, trajectory)
            
        elif choice == "2":
            if not Path(RECORD_FILE).exists():
                print("错误：没有找到录制文件，请先录制")
                continue
            
            trajectory = load_trajectory(RECORD_FILE)
            enable_torque(motors)
            time.sleep(0.5)
            
            input("按 Enter 开始回放...")
            replay_trajectory(motors, trajectory)
            
        elif choice == "3":
            print("再见！")
            disable_torque(motors)
            break
        
        else:
            print("无效选项，请重新输入")

if __name__ == "__main__":
    main()
