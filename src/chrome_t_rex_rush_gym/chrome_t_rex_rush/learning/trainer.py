import numpy as np
import time

def format_float(f):
    return format(f, '07.2f')

def run_agent(agent, env, episodes=100, frames=1000, learn=True, visualize=None):
    """Executes predefined number of steps, actions are choosen by agent, environment should be openai gym environemnt"""

    rewards = []
    means = []
    start = time.time()

    env.reset() 
    agent.setup()
    #file = 'saves/' + env_split[0] + '/' + type(agent).__name__ + '/' + FLAGS.name
        #agent.load(file)

    for episode in range(episodes):
        observation = env.reset()
        # this is each frame, up to 200...but we wont make it that far.
        current_reward = 0
        for t in range(frames):
            if not visualize is None:
                env.render(mode=visualize)
            action = agent.act(observation, env.action_space)
            old_observation = observation
            observation, reward, done, info = env.step(action)
            if learn:    
                agent.observe(old_observation, reward, action)
            current_reward += reward
            if done:
                rewards.append(current_reward)
                if len(rewards) > 100:
                    rewards.pop(0)
                if episode > 0 and ((episode + 1) % 100 == 0):
                    mean = np.mean(rewards)
                    std = np.std(rewards)
                    max = np.max(rewards)
                    print("100 episodes reward mean: " + format_float(mean) + " std: " + format_float(std) + " max: " + format_float(max))
                    #if learn and len(means) > 5 and mean > max(means):
                        #agent.save(file)
                        #print('Saving agent with score ' + format_float(mean) + ' in ' + file)
                    means.append(mean)
                break
        agent.next_episode(episode)
        
    end = time.time()
    print("Finished with best mean: " + format_float(max(means)) + " in " + str(end-start) + "s")
