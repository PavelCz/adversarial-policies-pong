import numpy as np
import gym
from gym import spaces

class ImageToPyTorch(gym.ObservationWrapper):
    """
    Image shape to num_channels x weight x height
    """
    def __init__(self, env):
        super(ImageToPyTorch, self).__init__(env)
        old_shape = self.observation_space.shape
        print(old_shape)
        self.observation_space = gym.spaces.Box(low=0.0, high=1.0, shape=(old_shape[-1], old_shape[0], old_shape[1]), dtype=np.uint8)

    def observation(self, observation):
        return (np.swapaxes(observation[0], 2, 0), np.swapaxes(observation[1], 2, 0))
    

def wrap_image_to_pytorch(env):
    return ImageToPyTorch(env)

class ToPytorch(gym.ObservationWrapper):

    def __init__(self,env):
        super(ToPytorch, self).__init__(env)
        self.observation_space.shape = env.observation_space[0].shape

    def observation(self, observation):
        return (observation[0], observation[1])

def wrap_pytorch(env):
    return ToPytorch(env)