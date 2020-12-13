import os
import copy

import gym
import ma_gym  # Necessary so the PongDuel env exists
from stable_baselines3 import PPO

from src.agents.random_agent import RandomAgent
from src.selfplay.opponent_wrapper import OpponentWrapper


def learn_with_selfplay(max_agents=10):
    # Initialize environment
    env = gym.make('PongDuel-v0')
    env = OpponentWrapper(env)

    # Initialize first agent
    rand_agent = RandomAgent(env)
    previous_models = [rand_agent]

    # Load potentially saved previous models
    for i in range(1, max_agents):
        path = _make_model_path(i)
        if os.path.isfile(path):
            model = PPO.load(path)
            previous_models.append(model)
        else:
            break

    # Initialize first round
    last_agent = len(previous_models) - 1
    if last_agent == 0:
        main_model = PPO('MlpPolicy', env, verbose=0)
    else:
        main_model = copy.deepcopy(previous_models[last_agent])
        main_model.set_env(env)

    # Start training with self-play over several rounds
    for i in range(last_agent, max_agents):
        print(f"Running training round {i+1}")
        # Take opponent from the previous version of the model
        env.set_opponent(previous_models[i])

        main_model.learn(total_timesteps=1_000_000)
        # Save the further trained model to disk
        main_model.save(_make_model_path(i + 1))
        # Make a copy of the just saved model by loading it
        copy_of_model = PPO.load(_make_model_path(i + 1))
        # Save the copy to the list
        previous_models.append(copy_of_model)
        # Do evaluation for this training round
        avg_round_reward = evaluate(main_model, env)
        print(f"Average round reward after training: {avg_round_reward}")

    # Evaluate the last model against each of its previous iterations
    _evaluate_against_predecessors(previous_models, env)


def _make_model_path(i):
    model_dir = 'output/models/'
    return model_dir + 'ppo-' + str(i) + '.out'


def evaluate(model, env):
    num_eps = 100
    total_reward = 0
    total_rounds = 0
    for episode in range(num_eps):
        ep_reward = 0
        # Evaluate the agent
        done = False
        obs = env.reset()
        info = None
        while not done:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            ep_reward += reward
            # env.render()
        total_reward += ep_reward
        total_rounds += info['rounds']
    env.close()

    avg_round_reward = total_reward / total_rounds
    return avg_round_reward


def _evaluate_against_predecessors(previous_models, env):
    last_model = previous_models[-1]
    last_model_index = len(previous_models) - 1
    for i, model in enumerate(previous_models):
        env.set_opponent(model)
        avg_round_reward = evaluate(last_model, env)
        print(f"Model {last_model_index} against {i}: {avg_round_reward}")
