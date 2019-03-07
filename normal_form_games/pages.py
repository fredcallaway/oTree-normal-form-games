from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
# from .models import Constants, rand_game, transpose_game
from .models import Constants
import random
import pickle as pkl
import pandas as pd
import json
import numpy as np



def sample_cell(ρ=0, max=9, min=0, μ=5, σ=3):
    r,c = np.random.multivariate_normal([0,0], [[1, ρ], [ρ, 1]])*σ + μ
    r = round(r)
    c = round(c)
    while r < min or r > max or c < min or c > max:
        r,c = np.random.multivariate_normal([0,0], [[1, ρ], [ρ, 1]])*σ + μ
        r = round(r)
        c = round(c)
    return [int(r),int(c)]


def rand_game(size, ρ=0., σ=3):
    game = np.zeros((size,size,2))
    for i in range(size):
        for j in range(size):
            r,c = sample_cell(ρ=ρ, max=9.5, min=-0.5, μ=5, σ=σ)
            game[i,j,0] = r
            game[i,j,1] = c
    return game



def transpose_game(game):
    return np.flip(np.swapaxes(game, 0, 1), 2)

same_games_dict = dict()
same_games_dict[31] = np.array([[[9,3], [2,8],[8,7]],[[5,4],[5,8],[6,3]], [[6,5],[0,2],[3,0]]])
same_games_dict[37] = np.array([[[3,2], [3,1],[3,5]],[[4,0],[6,9],[1,4]], [[9,6],[2,6],[0,3]]])
same_games_dict[41] = np.array([[[1,3], [9,2],[5,7]],[[1,6],[7,7],[7,0]], [[5,7],[3,1],[6,9]]])
same_games_dict[44] = np.array([[[8,7], [1,7],[2,9]],[[0,9],[3,4],[4,1]], [[4,1],[3,6],[6,4]]])
same_games_dict[49] = np.array([[[9,8], [6,5],[1,5]],[[8,8],[5,4],[4,0]], [[6,1],[5,4],[6,6]]])



games_df_dict = dict()
try:
    games_df_dict[-0.8] = pd.read_pickle("games_df_negative.pkl")
    games_df_dict[0.8] = pd.read_pickle("games_df_positive.pkl")
except:
    for ρ_pop in [-0.8, 0.8]:
        games_df = pd.DataFrame()
        for i in range(1,51):
            ρ = ρ_pop
            if i in same_games_dict.keys():
                row_game = same_games_dict[i]
            else:
                ρ = ρ_pop
                row_game = rand_game(3, ρ=ρ, σ=5)
            col_game = transpose_game(row_game)
            row_choices = []
            col_choices = []
            games_df = games_df.append({"round":int(i), "row_game":json.dumps(row_game.tolist()), "col_game":json.dumps(col_game.tolist()), "row":row_choices, "col":col_choices, "corr":ρ}, ignore_index=True)
        games_df["round"] = games_df["round"].astype(int)
        games_df = games_df.set_index("round")
        games_df_dict[ρ_pop] = games_df

class Choice(Page):
    # timeout_seconds = 60
    form_model = 'player'
    form_fields = ['choice']

    def before_next_page(self):
        if not self.timeout_happened:
            games_df = games_df_dict[self.player.treatment]
            games_df.at[self.round_number,self.player.player_role].append(self.player.choice)

    def vars_for_template(self):
        games_df = games_df_dict[self.player.treatment]
        self.player.game = games_df.at[self.round_number, self.player.player_role + "_game"]
        return {"play_rounds":Constants.num_rounds - 1}

    def is_displayed(self):
        return self.round_number < Constants.num_rounds

    # def vars_for_template(self):
    #     prev = self.player.in_previous_rounds()
    #     return {
    #         'last_choice': prev[-1].choice + 1 if prev else False,
    #     }

# class GroupWaitPage(WaitPage):
#     pass
#     # wait_for_all_groups = True
#     group_by_arrival_time = True
#
#     def get_players_for_group(self, players):
#         # round = self.round_number
#         # if len(games_df[games_df[round] == round])
#         if len(players) >= 2:
#             p1, p2 = random.sample(players, 2)
#             game = rand_game(Constants.size)
#             p1.game = json.dumps(game.tolist())
#             p2.game = json.dumps(transpose_game(game).tolist())
#             return [p1, p2]



class ResultsWaitPage(WaitPage):
    # wait_for_all_groups = True
    group_by_arrival_time = True
    title_text = "Waiting for other players"

    def get_players_for_group(self, players):
        round = self.round_number
        players_negative = list(filter(lambda p: p.treatment == -0.8, players))
        players_positive = list(filter(lambda p: p.treatment == 0.8, players))
        players_to_return = []
        games_df = games_df_dict[-0.8]
        if len(games_df.at[round-1, "row"]) > 0 and len(games_df.at[round-1, "col"]) > 0:
            for player in  players_negative:
                prev_player = player.in_round(self.round_number - 1)
                opp_role = "col" if player.player_role == "row" else "row"
                prev_player.other_choice = random.choice(games_df.at[round-1,opp_role])
                # player.other_choice = random.choice(games_df.at[round-1,opp_role])
                player.set_payoff()
            players_to_return.extend(players_negative)

        games_df = games_df_dict[0.8]
        if len(games_df.at[round-1, "row"]) > 0 and len(games_df.at[round-1, "col"]) > 0:
            for player in  players_positive:
                prev_player = player.in_round(self.round_number - 1)
                opp_role = "col" if player.player_role == "row" else "row"
                prev_player.other_choice = random.choice(games_df.at[round-1,opp_role])
                # player.other_choice = random.choice(games_df.at[round-1,opp_role])
                player.set_payoff()
            players_to_return.extend(players_positive)

        return players_to_return

    def is_displayed(self):
        # return self.round_number < Constants.num_rounds
        return self.round_number > 1
    #
    #
    # def after_all_players_arrive(self):
    #     round = self.round_number
    #     while len(games_df.at[round, "row"]) == 0 or len(games_df.at[round, "col"]) == 0:
    #         time.sleep(5)
    #     for player in  self.group.get_players():
    #         opp_role = "col" if player.role == "row" else "row"
    #         player.other_choice = random.choice(games_df[games_df[round] == round][opp_role])
    #         player.set_payoff()

        # self.group.set_payoffs()
        # for group in self.subsession.get_groups():
        #     group.set_payoffs()
        # self.subsession.group_randomly()


class ResultsSummary(Page):
    # timeout_seconds = 5
    def is_displayed(self):
        # return self.round_number < Constants.num_rounds
        return self.round_number > 1

    def vars_for_template(self):

        return {
            "prev_player":self.player.in_round(self.round_number - 1)
        }
class FinalSummary(Page):
    def is_displayed(self):
        if self.round_number == Constants.num_rounds:
            games_df_dict[-0.8].to_pickle("games_df_negative.pkl")
            games_df_dict[0.8].to_pickle("games_df_positive.pkl")
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        cumulative_payoff = sum([p.payoff for p in self.player.in_previous_rounds()])
        return {"cumulative_payoff":cumulative_payoff}

page_sequence = [
    ResultsWaitPage,
    ResultsSummary,
    Choice,
    FinalSummary
]
