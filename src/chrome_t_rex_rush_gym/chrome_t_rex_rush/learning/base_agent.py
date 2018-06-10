class BaseAgent:
    def action(self, observation, action_space):
        pass

    def observe(self, observation, reward, action):
        pass

    def setup(self):
        pass
    
    def dispose(self):
        pass

    def next_episode(self, episode):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass
    
    def save(self, fileName):
        pass
    
    def load(self, fileName):
        pass