import numpy as np
import tensorflow as tf
import gym

from envs.t_rex_env import TRexEnvVector

class MyModel(TensorflowAgent):

    def __init__(self, input_size, actions_size, hidden_size=8, hidden_count=1):
        super().__init__()

        self.gamma = 0.99
        self.lr = 1e-2
        self.memory_buffer = []

        with tf.name_scope('model'):
            self.input_tensor = x = tf.placeholder(tf.float32, [None, input_size], "observation_in")
    
            for i in range(hidden_count):
                print('aAdding dense')
                x = tf.layers.dense(x, hidden_size, activation=tf.nn.relu, name="dense_" + str(i))

            self.output = tf.layers.dense(x, actions_size, activation=tf.nn.softmax, use_bias=False, name="output") # q wartosci
            tf.summary.scalar('avg-q', tf.reduce_mean(tf.reduce_max(self.output, axis=1)))

            self.action_tensor = tf.argmax(self.output, axis=1, output_type = tf.int32, name="choosen_action") # wybrana akcja

            self.action_holder = tf.placeholder(tf.int32, [None], "action_holder")    # bufor akcja - z replay buffera
            self.reward_holder = tf.placeholder(tf.float32, [None], "reward_holder")  # bufor na oczekiwaną akcję do uczenia
            tf.summary.scalar('avg-reward', tf.reduce_mean(self.reward_holder))
            tf.summary.scalar('avg-action', tf.reduce_mean(self.action_holder))

            indexes = tf.range(0, tf.shape(self.output)[0]) * tf.shape(self.output)[1] + self.action_holder
            responsible_outputs = tf.gather(tf.reshape(self.output, [-1]), indexes)
            self.loss = tf.reduce_mean(tf.log(responsible_outputs) * self.reward_holder, name="Loss")

            tf.summary.scalar('loss', self.loss)

            #self.optimizer = tf.train.AdamOptimizer( learning_rate=1e-2).minimize(loss)
            self.summary = tf.summary.merge_all()
            self.summary_writer = tf.summary.FileWriter('logs/model')

            tvars = tf.trainable_variables()
            self.gradient_holders = []
            for idx,var in enumerate(tvars):
                placeholder = tf.placeholder(tf.float32,name=str(idx)+'_holder')
                self.gradient_holders.append(placeholder)
            self.gradients = tf.gradients(self.loss,tvars)
            optimizer = tf.train.AdamOptimizer(learning_rate=self.lr)
            self.update_batch = optimizer.apply_gradients(zip(self.gradient_holders,tvars))

    def setup(self):
        self.memory_buffer = [] 
        self.sess.run(tf.global_variables_initializer())
        self.gradBuffer = self.sess.run(tf.trainable_variables())
        for ix,grad in enumerate(self.gradBuffer):
            self.gradBuffer[ix] = grad * 0

    def act(self, observation):
        """Computes next action based on given observations"""
        action = self.sess.run(self.output, feed_dict={
            self.input_tensor: observation})

        return self.map_action(action[0])
    def map_action(self, q_values, learning=True):
        """Returns action accounting for exploration factor"""
        if learning:
            prob = np.random.choice(q_values, p=q_values)

        return np.argmax(q_values)
        
    def observe(self, observation, reward, action):
        self.memory_buffer.append([observation, action, reward])

    def next_episode(self, episode):
        sess = self.sess

        if len(self.memory_buffer) == 0:
            return

        memory_buffer = np.array(self.memory_buffer)
        self.memory_buffer = []
        memory_buffer[:,2] = self.discount_rewards(memory_buffer[:,2])
         # posumuj nagrody mniejszając znaczenia nagrody wraz z kolejnymi akcjami
        feed_dict={# przekształcenie bufora w słownik
                self.reward_holder:memory_buffer[:,2],
                self.action_holder:memory_buffer[:,1],
                self.input_tensor:np.vstack(memory_buffer[:,0])}

        summary, grads = sess.run([self.summary, self.gradients], feed_dict=feed_dict)
        self.summary_writer.add_summary(summary, i)

        for idx,grad in enumerate(grads):
            self.gradBuffer[idx] += grad

        if episode % 5 == 0 and episode != 0:
            feed_dict= dictionary = dict(zip(self.gradient_holders, self.gradBuffer))
            _ = sess.run(self.update_batch, feed_dict=feed_dict)
            for ix,grad in enumerate(self.gradBuffer):
                self.gradBuffer[ix] = grad * 0

    def discount_rewards(self, r):
        """ take 1D float array of rewards and compute discounted reward """
        discounted_r = np.zeros_like(r)
        running_add = 0
        for t in reversed(range(0, r.size)):
            running_add = running_add * self.gamma + r[t]
            discounted_r[t] = running_add
        return discounted_r

    def save(self, fileName):
        """Saves model to file"""
        import os
        if not os.path.exists(fileName):
            os.makedirs(fileName)
        else:
            shutil.rmtree(fileName)
        saver = tf.train.Saver(tf.trainable_variables())
        saver.save(self.sess, fileName)

    def load(self, fileName):
        """Loads model from file"""
        saver = tf.train.Saver(tf.trainable_variables())
        saver.restore(self.sess, fileName)


def make_model(env):
    input_size = np.prod(env.observation_space.shape)
    actions_size = np.prod(env.action_space.n)

    model = MyModel(input_size, actions_size)
    return model

def episode(model, i, batches=30):

    model.setup()
    episode_rewards = []
    for x in range(batches):
        obs = env.reset()
        reward = 0
        done = False
        episode_reward = 0
        while not done:
            action = model.act([obs])
            new_obs, reward, done, _ = env.step(action)
            model.observe(obs, action, reward)
            #env.render()
            episode_reward += reward
            model.next_episode(i)
            
            obs = new_obs
        episode_rewards.append(episode_reward)
    print("Training batch: ", np.mean(episode_rewards))






    
#env = TRexEnvVector()
env =  gym.make('CartPole-v0')
model = make_model(env)
with model:
    i = 0
    while True:
        i += 1
        episode(model, i)