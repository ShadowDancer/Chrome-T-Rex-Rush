
import tensorflow as tf
import numpy as np

from learning.tensorflow_agent import TensorflowAgent


class QNetworkAgent(TensorflowAgent):
    """Test agent executing random ctions"""
    def __init__(self, obs_space, ats_space):
        TensorflowAgent.__init__(self)
        
        self.gamma = 0.99
        self.lr = 1e-2

        i_size = np.prod(obs_space.shape)
        a_size = np.prod(ats_space.n)
        h_size = 16
        h_num = 1
        
        with tf.name_scope('model'):
            self.input = x = tf.placeholder(tf.float32, [None,i_size], "input")

            for i in range(h_num):
                x = tf.layers.dense(x, h_size, activation=tf.nn.relu, name="Hidden" + str(i))

            self.output = tf.layers.dense(x, a_size, activation=tf.nn.softmax)
            tf.summary.scalar('avg-max-q-value', tf.reduce_mean(tf.reduce_max(self.output, axis=1)))

            self.chosen_action = tf.argmax(self.output,1) # choosen action if acting
    
            # learning variables
            self.reward_holder = tf.placeholder(tf.float32, [None])  # bufor na nagrodę
            self.action_holder = tf.placeholder(tf.int32, shape=[None])    # bufor na akcję
            tf.summary.scalar('reward-avg', tf.reduce_mean(self.reward_holder))
            tf.summary.scalar('action-avg', tf.reduce_mean(self.action_holder))
            tf.summary.scalar('action-mean', tf.contrib.distributions.percentile(self.action_holder, 50.0))
            tf.summary.histogram('action-historgram', self.action_holder)

            # corss entrophy
            self.indexes = tf.range(0, tf.shape(self.output)[0]) * tf.shape(self.output)[1] + self.action_holder
            self.responsible_outputs = tf.gather(tf.reshape(self.output, [-1]), self.indexes)
            self.loss = -tf.reduce_mean(tf.log(self.responsible_outputs) * self.reward_holder)        
            tf.summary.scalar('loss', self.loss)
        
            # gradient
            tvars = tf.trainable_variables()
            self.gradient_holders = []
            for idx,var in enumerate(tvars):
                placeholder = tf.placeholder(tf.float32,name=str(idx) + '_holder')
                self.gradient_holders.append(placeholder)

            self.gradients = tf.gradients(self.loss,tvars)
        
            optimizer = tf.train.AdamOptimizer(learning_rate=self.lr)
            self.update_batch = optimizer.apply_gradients(zip(self.gradient_holders,tvars))
            self.summary = tf.summary.merge_all()
        self.summary_writer = tf.summary.FileWriter('logs/model')

    def setup(self):
        self.memory_buffer = [] # bufor na obserwacje
        #inicializuj tensorflow
        self.sess.run(tf.global_variables_initializer())    
        self.gradBuffer = self.sess.run(tf.trainable_variables())
        for ix,grad in enumerate(self.gradBuffer):
            self.gradBuffer[ix] = grad * 0
            

    def act(self, observation, action_space):
        q_values = self.sess.run(self.output,feed_dict={
            self.input:[observation]
            })[0]
       
        action = np.random.choice(q_values,p=q_values)
        action = np.argmax(q_values == action)
        action = action_space.sample()
        return action

    def observe(self, observation, reward, action):
        """Stores observation and its results in memory buffer"""
        self.memory_buffer.append([observation, action, reward])
        
    def next_episode(self, episode):
        sess = self.sess

        if len(self.memory_buffer) == 0:
            return

        memory_buffer = np.array(self.memory_buffer)
        self.memory_buffer = []
        memory_buffer[:,2] = self.discount_rewards(memory_buffer[:,2])
        np.random.shuffle(memory_buffer)
        feed_dict = {# przekształcenie bufora w słownik
                self.reward_holder:memory_buffer[:,2],
                self.action_holder:memory_buffer[:,1],
                self.input:np.vstack(memory_buffer[:,0])}

        summary,grads = sess.run([self.summary, self.gradients], feed_dict=feed_dict)
        for idx,grad in enumerate(grads):
            self.gradBuffer[idx] += grad

        if episode % 5 == 0 and episode != 0:
            feed_dict = dictionary = dict(zip(self.gradient_holders, self.gradBuffer))
            _ = sess.run(self.update_batch, feed_dict=feed_dict)
            for ix,grad in enumerate(self.gradBuffer):
                self.gradBuffer[ix] = grad * 0
        self.summary_writer.add_summary(summary, episode)
    def discount_rewards(self, r):
        """ take 1D float array of rewards and compute discounted reward """
        # sumujemy nagrody, pamietając stare ze współczynnikiem gamma
        discounted_r = np.zeros_like(r)
        running_add = 0
        for t in reversed(range(0, r.size)):
            running_add = running_add * self.gamma + r[t]
            discounted_r[t] = running_add
        return discounted_r

    def save(self, fileName):
        import os
        if not os.path.exists(fileName):
            os.makedirs(fileName)
        else:
            shutil.rmtree(fileName)
        saver = tf.train.Saver(tf.trainable_variables())
        saver.save(self.sess, fileName)

    def load(self, fileName):
        saver = tf.train.Saver(tf.trainable_variables())
        saver.restore(self.sess, fileName)
