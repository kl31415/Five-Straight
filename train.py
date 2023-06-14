from keras.callbacks import TensorBoard
import matplotlib.pyplot as plt

from AIPlayer import RLPlayer

player = RLPlayer('magenta')
opponent = RLPlayer('blue')

num_episodes = 10
max_steps_per_episode = 100

episode_rewards = []
episode_loss = []

tensorboard = TensorBoard(log_dir='./logs')

for episode in range(num_episodes):
    player.initialize_board_state()
    opponent.initialize_board_state()
    done = False
    total_reward = 0

    for step in range(max_steps_per_episode):
        state = player.boardStateMrx
        action = player.nextAction(player.boardStateMrx)
        next_state, reward, done = player.take_action(action)

        player.remember(state, action, reward, next_state, done)
        loss = player.replay()/10**8
        player.update_target_model()

        total_reward += reward/100
        player.boardStateMrx = next_state
        if done:
            break

        adv_action = opponent.nextAction(player.boardStateMrx)
        next_state, adv_reward, done = opponent.take_action(adv_action)
        opponent.update_target_model()

        total_reward -= adv_reward/100
        player.boardStateMrx = next_state
        if done:
            total_reward -= adv_reward/100
            break

    player.epsilon *= player.epsilon_decay
    episode_rewards.append(total_reward)
    episode_loss.append(loss)

    print("Episode {}: Total Reward = {}, Loss = {}".format(episode + 1, total_reward, loss))

player.save_model("ep=10_rew=focus+deep_model")

plt.plot(range(1, num_episodes+1), episode_rewards)
plt.xlabel('Episode')
plt.ylabel('Total Reward')
plt.title('Episode Rewards')
plt.show()

plt.plot(range(1, num_episodes+1), episode_loss)
plt.xlabel('Episode')
plt.ylabel('Loss')
plt.title('Episode Loss')
plt.show()