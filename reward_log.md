# 🚗 PPOCarla Reward Function Log

用于记录每一次实验中使用的 `_get_reward` 函数版本及其说明，配合 WandB 的断点模型编号追踪效果变化。

---

## ✅ Reward Version 0

**Tag:** `initial`  
**Model Checkpoint:** 无（首次训练）  
**LLM 修改：** 无  
**说明：** 初始版本，奖励项较多，包含纵向速度奖励、碰撞、超速等。未包含红灯、出车道逻辑。

**Reward Components Used:**
- `reward_coll`
- `reward_vel_long`
- `reward_speed`

**函数代码：**
```python
def _get_reward(self, data):
    r_collision = -1 if data['collision'][1] else 0
    r_speeding = -1 if data['ego_state'][1]['speeding'] else 0
    vel_lon = data['ego_state'][1]['ego_vel_in_ego'][0]

    reward_coll = self.params.rl.reward.collision * r_collision
    reward_vel_long = self.params.rl.reward.vel_lon * vel_lon
    reward_speed = self.params.rl.reward.speeding * r_speeding

    reward = reward_coll + reward_speed + reward_vel_long

    reward_comp = {
        'reward_coll': reward_coll,
        'reward_vel_long': reward_vel_long,
        'reward_speed': reward_speed,
        'reward': reward,
    }
    return reward, reward_comp

## ✅ Reward Version 1
增加了红灯检测和out检测
**Tag:** `baseline_restart`  
**Model Checkpoint:** `agent_llm_12800.pt`  
**LLM 修改：** 启用，但仍使用最初设定的 4 个 reward 分量  
**说明：** 从头开始新一轮训练，首次触发 LLM，但当前 reward 没有变更，仅用于记录版本编号。

**Reward Components Used:**
- `reward_coll`
- `reward_speed`
- `reward_ool`
- `reward_red_light`

**函数代码：**
```python
def _get_reward(self, data):
    r_collision = -1 if data['collision'][1] else 0
    r_speeding = -1 if data['ego_state'][1]['speeding'] else 0
    r_out = -1 if abs(data['dis_to_wps'][1]) > self.params.rl.reward.out_lane_thres else 0
    r_red_light = -1 if data['run_red_light'][1] else 0

    reward = self.params.rl.reward.collision * r_collision \
           + self.params.rl.reward.speeding * r_speeding \
           + self.params.rl.reward.oo_lane * r_out \
           + self.params.rl.reward.red_light * r_red_light

    reward_comp = {
        'reward_coll': self.params.rl.reward.collision * r_collision,
        'reward_speed': self.params.rl.reward.speeding * r_speeding,
        'reward_ool': self.params.rl.reward.oo_lane * r_out,
        'reward_red_light': self.params.rl.reward.red_light * r_red_light,
        'reward': reward,
    }
    return reward, reward_comp


## ✅ Reward Version 2\3\4
没改

## ✅ Reward Version 5
加了steering

## ✅ Reward Version 6
加了r_speed_dev
# Speed tracking, not used for now
    # r_speed_dev = - (abs(data['ego_state'][1]['speed_tracking_error']))

## ✅ Reward Version 7、8
 reward_lat_acc