from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
import numpy as np
import json
doc = """
A demo of how rounds work in oTree, in the context of 'matching pennies'
"""


class Constants(BaseConstants):
    name_in_url = 'matching_pennies'
    players_per_group = 2
    num_rounds = 4
    stakes = c(100)


def rand_game(size):
    return np.random.randint(10, size=(3,3,2))

def transpose_game(game):
    return np.flip(np.swapaxes(game, 0, 1), 2)

class Subsession(BaseSubsession):
    def creating_session(self):
        for group in self.get_groups():
            game = rand_game(3)
            p1, p2 = group.get_players()
            p1.game = json.dumps(game.tolist())
            p2.game = json.dumps(transpose_game(game).tolist())


        # if self.round_number == 1:
        #     self.game = "One"
        #     paying_round = random.randint(1, Constants.num_rounds)
        #     self.session.vars['paying_round'] = paying_round
        # if self.round_number == 3:
        #     # reverse the roles
        #     matrix = self.get_group_matrix()
        #     for row in matrix:
        #         row.reverse()
        #     self.set_group_matrix(matrix)
        # if self.round_number > 3:
        #     self.group_like_round(3)


class Group(BaseGroup):

    def set_payoffs(self):
        p1, p2 = self.get_players()
        p1.other_choice = p2.choice
        p2.other_choice = p1.choice


        game = json.loads(p1.game)
        p1.payoff = c(game[p1.choice][p2.choice][0])
        p2.payoff = c(game[p1.choice][p2.choice][1])

        # matcher = self.get_player_by_role('Matcher')
        # mismatcher = self.get_player_by_role('Mismatcher')

        # if matcher.penny_side == mismatcher.penny_side:
        #     matcher.is_winner = True
        #     mismatcher.is_winner = False
        # else:
        #     matcher.is_winner = False
        #     mismatcher.is_winner = True
        # for player in [mismatcher, matcher]:
        #     if self.subsession.round_number == self.session.vars['paying_round'] and player.is_winner:
        #         player.payoff = Constants.stakes
        #     else:
        #         player.payoff = c(0)


class Player(BasePlayer):
    game = models.StringField()
    choice = models.IntegerField()
    other_choice = models.IntegerField()

    def role(self):
        if self.id_in_group == 1:
            return 'Mismatcher'
        if self.id_in_group == 2:
            return 'Matcher'
