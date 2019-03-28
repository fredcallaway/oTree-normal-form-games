from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants

import numpy as np
import json

def rand_game(size):
    return np.random.randint(10, size=(size,size,2))

class MyPage(Page):
    def is_displayed(self):
        return not self.participant.vars.get('done', False)

    def before_next_page(self):
        self.player.game = json.dumps(rand_game(Constants.size).tolist())
        self.player.choice_quiz = np.random.randint(Constants.size)
        self.player.other_choice_quiz = np.random.randint(Constants.size)


class Instructions(MyPage):
    def before_next_page(self):
        super().before_next_page()
        self.player.correct = True
        self.player.participant.vars['done'] = False
        self.player.q_num = 1


class Quiz(MyPage):
    form_model = 'player'
    form_fields = ['payoff_quiz', 'other_payoff_quiz']

    def vars_for_template(self):
        row_num = self.player.choice_quiz
        col_num = self.player.other_choice_quiz
        texts = ["first", "second", "third"]
        return {
            'row': texts[row_num],
            'col': texts[col_num]
        }

    def is_displayed(self):
        return self.player.correct == True

    def before_next_page(self):
        p = self.player
        p.q_num += 1
        game = json.loads(p.game)
        cell = game[p.choice_quiz][p.other_choice_quiz]
        p.correct = (cell[0] == p.payoff_quiz and cell[1] == p.other_payoff_quiz)
        super().before_next_page()
        # p.participant.vars['passing'] &= p.correct

class LastQuiz(Quiz):

    def before_next_page(self):
        super().before_next_page()
        p = self.player
        if p.correct:
            p.participant.vars['done'] = True



class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        pass


class Results(Page):
    pass


page_sequence = [
    Instructions,
    Quiz,
    Quiz,
    LastQuiz,
    # ResultsWaitPage,
    # Results
]
