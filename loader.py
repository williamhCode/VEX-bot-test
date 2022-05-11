from bot import VexBot
from actions import Action


class ActionsLoader:

    def __init__(self, actions: list[Action]):
        self.actions = actions
        self.step = 0
        self.currentAction = self.actions[self.step]

    def add_action(self, action: Action):
        self.actions.append(action)

    def reset(self, bot: VexBot):
        self.step = 0
        self.currentAction = self.actions[self.step]
        self.currentAction.set_up(bot)

    def set_up(self, bot: VexBot):
        self.currentAction.set_up(bot)

    def update(self, bot: VexBot):
        if self.step == None:
            return 0, 0

        if self.currentAction.stop(bot):
            if self.step == len(self.actions)-1:
                self.step = None
                return 0, 0
            self.step += 1
            self.currentAction = self.actions[self.step]
            self.currentAction.set_up(bot)

        leftInput, rightInput = self.currentAction.update(bot)

        return leftInput, rightInput
