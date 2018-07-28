import r6sapi as api
import json
import random
import asyncio
import urllib.request
import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

import warnings
warnings.filterwarnings("ignore")


class RainbowSix:

    def __init__(self):

        self.stat_dict = {}
        self.rank_dict = {}
        self.auth = None

    @asyncio.coroutine
    def server_auth(self, email, password):

        #self.auth = api.Auth(email, password)
        self.auth = api.Auth(email.format(random.randint(1, 10)), password)

    @asyncio.coroutine
    def get_ranked_stats(self, player_name):

        player = yield from self.auth.get_player(player_name, api.Platforms.UPLAY)
        yield from player.load_general()
        yield from player.load_queues()
        yield from player.load_level()

        for season_id in range(6, 11):
            rank = yield from player.get_rank(api.RankedRegions.EU, season_id)

            mmr = rank.mmr
            rank_name = rank.rank
            max_mmr = rank.max_mmr
            wins = rank.wins
            losses = rank.losses
            abandons = rank.abandons
            next_rank_mmr = rank.next_rank_mmr
            url = rank.get_icon_url()
            season_id = rank.season

            level = player.level
            ranked_games = player.ranked.played
            try:
                kd = round(player.ranked.kills / player.ranked.deaths, 2)
            except ZeroDivisionError:
                kd = "---"
            try:
                wl = round(player.ranked.won / player.ranked.lost, 2)
            except ZeroDivisionError:
                wl = "---"
            try:
                headshot_ratio = round(player.headshots / player.kills * 100, 2)
            except ZeroDivisionError:
                headshot_ratio = "---"

            self.rank_dict[season_id] = {'player_name': player_name, 'level': level, 'ranked_games': ranked_games,
                                         'season_id': season_id, 'mmr': mmr, 'max_mmr': max_mmr,
                                         'rank_name': rank_name, 'next_rank_mmr': next_rank_mmr,
                                         'win': wins, 'lose': losses,'abandon': abandons, 'kd': kd, 'wl': wl,
                                         'headshot_ratio': headshot_ratio, 'rank_icon_url': url}
        self.auth.session.connector.close()
        self.auth.session.detach()

    @asyncio.coroutine
    def get_op_stats(self, player_name, op_name):

        player = yield from self.auth.get_player(player_name, api.Platforms.UPLAY)

        operator = yield from player.get_operator(op_name)
        op_icon_url = yield from self.auth.get_operator_badge(op_name)

        op_win = operator.wins
        op_lose = operator.losses
        op_kill = operator.kills
        op_death = operator.deaths
        op_playtime = operator.time_played
        try:
            op_wl = round(op_win / op_lose, 3)
        except ZeroDivisionError:
            op_wl = "---"
        try:
            op_kd = round(op_kill / op_death, 3)
        except ZeroDivisionError:
            op_kd = "---"

        self.stat_dict = {'op_name': op_name, 'op_playtime': op_playtime, 'op_win': op_win, 'op_lose': op_lose,
                          'op_w/l': op_wl, 'op_kill': op_kill, 'op_death': op_death, 'op_k/d': op_kd,
                          'op_icon_url': op_icon_url, 'player_name': player_name}

        self.auth.session.connector.close()
        self.auth.session.detach()

    def draw_ranked(self):

        img = Image.new('RGB', (800, 450), color=(255, 255, 255))
        d = ImageDraw.Draw(img)

        # Name
        font = ImageFont.truetype("arial.ttf", 25)
        d.text((10, 10), (self.rank_dict[6]['player_name']).upper(), fill=(1, 1, 1), font=font)

        # Subheadings
        font = ImageFont.truetype("arial.ttf", 20)
        d.text((10, 50), "Operation Health: ", fill=(1, 1, 1), font=font)
        d.text((10, 120), "Operation Blood Orchid: ", fill=(1, 1, 1), font=font)
        d.text((10, 190), "Operation White Noise: ", fill=(1, 1, 1), font=font)
        d.text((10, 260), "Operation Chimera: ", fill=(1, 1, 1), font=font)
        d.text((10, 330), "Operation Para Bellum", fill=(1, 1, 1), font=font)

        font = ImageFont.truetype("arial.ttf", 15)
        for i in range(0, 330, 70):
            d.text((10, 80+i), "mmr: ", fill=(1, 1, 1), font=font)
            d.text((10, 100+i), "max_mmr: ", fill=(1, 1, 1), font=font)
            d.text((150, 80+i), "abandons: ", fill=(1, 1, 1), font=font)
            d.text((150, 100+i), "mmr to next rank: ", fill=(1, 1, 1), font=font)
            d.text((350, 80+i), "wins: ", fill=(1, 1, 1), font=font)
            d.text((350, 100+i), "losses: ", fill=(1, 1, 1), font=font)


        # Stats
        i = 0
        for j in range(6, 11):
            d.text((90, 80+i), str(round(self.rank_dict[j]['mmr'], 1)), fill=(1, 1, 1), font=font)
            d.text((90, 100+i), str(round(self.rank_dict[j]['max_mmr'], 1)), fill=(1, 1, 1), font=font)
            d.text((270, 80+i), str(self.rank_dict[j]['abandon']), fill=(1, 1, 1), font=font)
            d.text((270, 100+i), str(round(self.rank_dict[j]['next_rank_mmr'], 1)), fill=(1, 1, 1), font=font)
            d.text((400, 80+i), str(self.rank_dict[j]['win']), fill=(1, 1, 1), font=font)
            d.text((400, 100+i), str(self.rank_dict[j]['lose']), fill=(1, 1, 1), font=font)
            rank_img = urllib.request.urlopen(self.rank_dict[j]['rank_icon_url'])
            icon = Image.open(rank_img)
            icon = icon.resize((75, 75), Image.ANTIALIAS)
            img.paste(icon, (500, 50+i))
            i = i + 70

        img.save('op_stat_img.png')

    def draw_op(self):

        img = Image.new('RGB', (400, 300), color=(255, 255, 255))
        d = ImageDraw.Draw(img)

        # Name
        font = ImageFont.truetype("arial.ttf", 25)
        d.text((10, 10), (self.stat_dict['op_name']).upper(), fill=(1, 1, 1), font=font)

        # Subheadings
        font = ImageFont.truetype("arial.ttf", 15)
        d.text((10, 50), "playername: ", fill=(1, 1, 1), font=font)
        d.text((10, 90), "total time played: ", fill=(1, 1, 1), font=font)
        d.text((10, 110), "wins: ", fill=(1, 1, 1), font=font)
        d.text((10, 130), "losses: ", fill=(1, 1, 1), font=font)
        d.text((10, 170), "wins/loss ratio: ", fill=(1, 1, 1), font=font)
        d.text((10, 190), "kills: ", fill=(1, 1, 1), font=font)
        d.text((10, 210), "death: ", fill=(1, 1, 1), font=font)
        d.text((10, 230), "kill/death ration: ", fill=(1, 1, 1), font=font)

        # Stats
        d.text((120, 50), str(self.stat_dict['player_name']), fill=(1, 1, 1), font=font)
        d.text((150, 90), str(round(self.stat_dict['op_playtime']/3600, 2)) + " h", fill=(1, 1, 1), font=font)
        d.text((150, 110), str(self.stat_dict['op_win']), fill=(1, 1, 1), font=font)
        d.text((150, 130), str(self.stat_dict['op_lose']), fill=(1, 1, 1), font=font)
        d.text((150, 170), str(self.stat_dict['op_w/l']), fill=(1, 1, 1), font=font)
        d.text((150, 190), str(self.stat_dict['op_kill']), fill=(1, 1, 1), font=font)
        d.text((150, 210), str(self.stat_dict['op_death']), fill=(1, 1, 1), font=font)
        d.text((150, 230), str(self.stat_dict['op_k/d']), fill=(1, 1, 1), font=font)

        op_img = urllib.request.urlopen(self.stat_dict['op_icon_url'])
        icon = Image.open(op_img)
        img.paste(icon, (250, 10))

        img.save('op_stat_img.png')








