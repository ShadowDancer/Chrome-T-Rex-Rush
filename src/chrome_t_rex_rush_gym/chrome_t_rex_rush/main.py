"""Dino game from chrome"""
__author__ = "Shivam Shekhar,ShadowDancer"



from envs.t_rex_env import TRexEnvRgb


def presentation():
    env = TRexEnv()
    env.reset()

    done = False
    x = 0
    while not done:
        x += 1
        obs, reward, done, _ = env.step(env.action_space.sample())
        env.render()

        if done:
            env.reset()
            done = False

        print(obs.shape, reward, done)

def learning():
    import learning.vector_trainer

def game():
    from game import Game
    Game().run()

if __name__ == '__main__':
    #game()
    learning()