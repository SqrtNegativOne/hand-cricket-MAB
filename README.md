# Hand Cricket Multi-Armed-Bandit Model
- Full feedback; the computer observes all losses or rewards for all the strategies in the list of strategies, not just the one played it played against the adversary.
- Adversarial bandit; losses are determined by both the computer's and the adversary's actions; not i.i.d.
- Adaptive adversary; the adversary can change its strategy based on the computer's actions.
- Two-player setting
- Discrete actions; the player and computer both choose from a discrete set of actions (in this case, choosing a number between 1 and 6).
- Asymmetric game; the player and computer have different roles
- Minimax game; One player tries to maximize score while the other tries to minimize it.

To satisfy the above conditions the Hedge algorithm was used.