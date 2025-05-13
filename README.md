# PPOCarla 项目
每次 LLM 建议后要做的操作
# step 0：确保你知道当前 global_step，例如 12800
GLOBAL_STEP=12800

# step 1：替换 reward 函数
python tools/replace_reward.py \
  --target_file envs/carla_gym/carla_env.py \
  --new_reward_file outputs/YYYY-MM-DD/HH-MM-SS/wandb/run-.../llm_reward_step_${GLOBAL_STEP}.py

# step 2：同步更新 evaluation.py 中所有 reward 相关的字段（见上方列表）

# step 3：记录 reward 版本
echo "| ${GLOBAL_STEP} | agent_llm_${GLOBAL_STEP}.pt | llm_reward_step_${GLOBAL_STEP}.py | 改动描述 |" >> logs/reward_log.md

# step 4：修改 config 以加载 checkpoint（只需要改 `config_gray_bev_frame.yaml`）
# 搜索并修改：
setup:
  load_checkpoint:
    use: true
    dir: /完整路径/outputs/YYYY-MM-DD/HH-MM-SS/wandb/run-.../files
    model_name: agent_llm_${GLOBAL_STEP}.pt

# step 5：重新运行
bash run.sh

涉及的文件：
config_gray_bev_frame.yaml,carla_env.py,evaluation.py,training.py

流程图：
┌────────────┐
│ LLM 触发   │
└────┬───────┘
     ↓
📌 保存新 reward -> llm_reward_step_XXXX.py
📌 保存模型      -> agent_llm_XXXX.pt

📝 修改 config:
 - setup.load_checkpoint.use = true
 - setup.load_checkpoint.dir, model_name 设置为最新 pt

📦 替换 carla_env.py 中的 _get_reward()
🔧 同步修改 evaluation.py 中所有 reward_component 相关字段

📁 记录到 logs/reward_log.md
🚀 bash run.sh 重启训练（自动接续 global_step）


## 项目简介

本项目是一个基于 PPO 的自动驾驶系统实验，使用 CARLA 仿真环境。实验的输入采用基于鸟瞰视角的图像信息（Frame Stacking + Gray），并通过简化的奖励函数（仅包含碰撞、超速、车道偏离和红灯违规）训练一个 PPO Agent。项目同时支持多种配置（例如 LSTM、Multi-BEV、RGB 等），本分支专注于简单的 Frame Stacking + Gray 版本。

## 项目架构

项目主要目录和文件说明如下：

- **agents/**  
  - `agent_base.py`：定义了基础代理类（BaseAgent）和部分扩展类。  
  - `agent.py`：根据不同的输入模态（如 RGBBEV、GrayBEV 等）构造不同的代理类。
  - `loss.py`：定义 PPO 的损失函数（PPOLoss）。
  - `rl_modules.py`：包含 actor（策略网络）和 critic（值网络）的网络结构模块。

- **envs/**  
  - `carla_gym/`：封装了 CARLA 环境为 Gym 接口，包括：
    - `carla_env.py`：Gym 环境实现，包含 reset 和 step 方法，以及奖励函数（_get_reward）。
    - `carla_manager.py`：管理 CARLA 服务器的启动、连接、以及演员（车辆、行人等）的管理。
    - `actors/`：包含演员管理（actor_manager.py）和生成演员蓝图（actors.py）的代码。
    - `sensors/`：传感器相关代码，包括鸟瞰视图（bird_eye_view_sensor_cv2.py）、RGB相机、激光雷达等。
    - `vehicle_control/`：包含车辆控制的各个模块，例如横向 PID/Stanley 控制器、纵向控制器、路线规划（route_planner.py）等。
    - `misc.py`：包含了一些工具函数，如碰撞检测、状态归一化等。
    - `render.py`：用于渲染鸟瞰图和其他可视化内容。

- **configs/**  
  - 存放 Hydra 配置文件，如 `config_gray_bev_frame.yaml`、`config_multi_bev_frame.yaml` 等，控制实验参数（例如传感器配置、网络结构、奖励函数参数等）。


- **utils/**  
  - `maker.py`：封装环境、代理、传感器的创建函数。  
  - `evaluation.py`：评估模块，负责周期性地评估训练好的模型表现，并记录指标到 wandb。  
  - `compile_return_plot.py`：用于生成训练回报图。
  - `evaluation.py`：记录评估过程中的各项指标。

- **training.py**  
  - 主训练脚本，负责采集数据、更新模型、记录日志以及周期性评估。

- **inference.py**  
  - 推理脚本，用于加载训练好的模型，在环境中运行，并生成最终的演示结果。

## 注意事项

- 本分支使用简化版奖励函数，仅保留碰撞、超速、车道偏离和红灯违规这四项指标。
- 训练配置采用 `config_gray_bev_frame.yaml` 文件，确保 `rl.lstm.use` 为 `false`，`rl.image.grayscale` 为 `true`，且 `rl.frame_stack.use` 为 `true`。
- 输出结果（模型权重、训练日志、回报曲线等）会保存在 outputs 目录，且该目录在 .gitignore 中被忽略，不会提交到仓库。
- 如有需要，请修改配置文件或奖励函数以满足特定实验要求。
