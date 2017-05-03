import threading

class SocketRecvThread(threading.Thread):
    def __init__(self, connection_socket, policy, num_local_steps, summary_writer, render, global_rollout, sess, conf):
#        super(SocketRecvThread, self).__init__()
        threading.Thread.__init__(self)
        self.connection_socket = connection_socket
        self.policy = policy
        self.num_local_steps = num_local_steps
        self.summary_writer = summary_writer
        self.render = render
        self.global_rollout = global_rollout
        self.buffer_size = 1400
        self.daemon = True
        self.sess = sess
        self.conf = conf
#        print ('55555')

    def _frag_recv(self, mess_len):
        mess_remain = mess_len
        mess = ''
        while mess_remain > 0:
            mess_temp = self.connection_socket.recv(min(mess_remain, self.buffer_size))
            mess += mess_temp
            mess_remain -= len(mess_temp)
        return mess

    def run(self):
        with self.sess.as_default():
            self._run()

    def _run(self):
#        print ('66666')
        #last_state = self.env.reset()
        raw_message_len = self.connection_socket.recv(4)
        if raw_message_len:
            message_len = struct.unpack('I', raw_message_len)[0]
            message = self._frag_recv(message_len)
            recovered_message = pickle.loads(message)
        last_state = recovered_message['obs']

        last_features = self.policy.get_initial_features()
        length = 0
        rewards = 0

        while True:
            terminal_end = False
            rollout = PartialRollout()

            for _ in range(self.num_local_steps):
                #print ('aaaaa')
                fetched = self.policy.act(last_state, *last_features)
                action, value_, features = fetched[0], fetched[1], fetched[2:]
                # argmax to convert from one-hot
                #state, reward, terminal, info = env.step(action.argmax())
                #print ('88888')
                #print (fetched)
                #print (action.argmax())
                self.connection_socket.send(struct.pack('I', action.argmax()))

                if self.render:
                    self.env.render()

                # collect the experience
                raw_message_len = self.connection_socket.recv(4)
                if raw_message_len:
                    message_len = struct.unpack('I', raw_message_len)[0]
                    message = self._frag_recv(message_len)
                    recovered_message = pickle.loads(message)

#                print (recovered_message)

                rollout.add(last_state, action, recovered_message['reward'], value_, recovered_message['terminal'], last_features)
                length += 1
                rewards += recovered_message['reward']

                last_state = recovered_message['obs']
                last_features = features

                if recovered_message['info']:
                    summary = tf.Summary()
                    for k, v in recovered_message['info'].items():
                        summary.value.add(tag=k, simple_value=float(v))
                    self.summary_writer.add_summary(summary, self.policy.global_step.eval())
                    self.summary_writer.flush()

                timestep_limit = self.conf['timestep_limit']
                if recovered_message['terminal'] or length >= timestep_limit:
                    terminal_end = True
                    if length >= timestep_limit or not self.conf['autoreset']:
                        #last_state = self.env.reset()
                        self.connection_socket.send('rest')
                        raw_message_len = self.connection_socket.recv(4)
                        if raw_message_len:
                            message_len = struct.unpack('I', raw_message_len)[0]
                            message = self._frag_recv(message_len)
                            recovered_message = pickle.loads(message)
                        last_state = recovered_message['obs']
                    last_features = self.policy.get_initial_features()
                    print("Episode finished. Sum of rewards: %d. Length: %d" % (rewards, length))
                    length = 0
                    rewards = 0
                    break

            if not terminal_end:
                rollout.r = self.policy.value(last_state, *last_features)

            self.global_rollout[0] = rollout
