from bot import VexBot

class ActionsLoader:

    def __init__(self, actions):
        self.actions = actions
        self.step = 0
        self.currentAction = self.actions[self.step]

    def addAction(self, action):
        self.actions.append(action)

    def setUp(self, bot):
        self.currentAction.setUp(bot)

    def update(self, bot:VexBot):
        if self.actions[self.step].stop(bot):
            if self.step == len(self.actions)-1:
                return 0, 0
            self.step += 1
            self.currentAction = self.actions[self.step]
            self.currentAction.setUp(bot)

        leftInput, rightInput = self.currentAction.update(bot)

        return leftInput, rightInput