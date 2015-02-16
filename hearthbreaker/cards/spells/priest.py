import copy
from hearthbreaker.cards.base import Card, MinionCard
from hearthbreaker.cards.minions.priest import ShadowOfNothing
from hearthbreaker.tags.base import BuffUntil, Buff
from hearthbreaker.tags.event import TurnEnded
from hearthbreaker.tags.status import Stolen, SpellDamage

import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY


class CircleOfHealing(Card):
    def __init__(self):
        super().__init__("Circle of Healing", 0, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        targets = copy.copy(game.other_player.minions)
        targets.extend(player.minions)

        for minion in targets:
            minion.heal(player.effective_heal_power(4), self)


class DivineSpirit(Card):
    def __init__(self):
        super().__init__("Divine Spirit", 2, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        # Increases by health, not max_health
        # source: http://www.hearthhead.com/card=1361/divine-spirit#comments:id=1908273
        self.target.increase_health(self.target.health)


class HolyFire(Card):
    def __init__(self):
        super().__init__("Holy Fire", 6, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.RARE,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(5), self)
        player.hero.heal(player.effective_heal_power(5), self)


class HolyNova(Card):  # TODO: Can this card be cast if no minions is in play?
    def __init__(self):
        super().__init__("Holy Nova", 5, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        for minion in copy.copy(game.other_player.minions):
            minion.damage(player.effective_spell_damage(2), self)

        for minion in player.minions:
            minion.heal(player.effective_heal_power(2), self)


class HolySmite(Card):
    def __init__(self):
        super().__init__("Holy Smite", 1, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.FREE, hearthbreaker.targeting.find_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(2), self)


class InnerFire(Card):
    def __init__(self):
        super().__init__("Inner Fire", 1, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        # This will increase/decrease a minions attack to its current health
        # It will set the attack to its current health, not max health
        # (source: http://www.hearthhead.com/card=376/inner-fire#comments:id=1931155)
        delta = self.target.health - self.target.calculate_attack()
        self.target.change_attack(delta)


# TODO: Can this spell be cast if the enemy have no minions?
class MassDispel(Card):
    def __init__(self):
        super().__init__("Mass Dispel", 4, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.RARE)

    def use(self, player, game):
        super().use(player, game)

        for minion in game.other_player.minions:
            minion.silence()

        player.draw()


class MindBlast(Card):
    def __init__(self):
        super().__init__("Mind Blast", 2, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.FREE)

    def use(self, player, game):
        super().use(player, game)

        game.other_player.hero.damage(player.effective_spell_damage(5), self)


class MindControl(Card):
    def __init__(self):
        super().__init__("Mind Control", 10, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_enemy_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        new_minion = self.target.copy(player)
        self.target.remove_from_board()
        new_minion.add_to_board(len(player.minions))

    def can_use(self, player, game):
        return super().can_use(player, game) and len(player.minions) < 7


class MindVision(Card):
    def __init__(self):
        super().__init__("Mind Vision", 1, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        # This card can be played even if opponent has no cards in hand
        # Source: http://www.hearthhead.com/card=1099/mind-vision#comments:id=2073386
        if (len(game.other_player.hand) > 0):
            card = copy.deepcopy(game.random_choice(game.other_player.hand))
            player.hand.append(card)


class Mindgames(Card):
    def __init__(self):
        super().__init__("Mindgames", 4, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)

        minion_card = game.random_draw(game.other_player.deck.cards,
                                       lambda c: not c.drawn and isinstance(c, MinionCard))
        if not minion_card:
            minion_card = ShadowOfNothing()
        else:
            minion_card = copy.copy(minion_card)
        minion_card.summon(player, game, 0)
        minion_card.drawn = True

    def can_use(self, player, game):
        return super().can_use(player, game) and len(player.minions) < 7


class PowerWordShield(Card):
    def __init__(self):
        super().__init__("Power Word: Shield", 1, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.increase_health(2)
        player.draw()


class ShadowMadness(Card):
    def __init__(self):
        super().__init__("Shadow Madness", 4, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.RARE,
                         hearthbreaker.targeting.find_enemy_minion_spell_target,
                         lambda target: target.calculate_attack() <= 3 and target.spell_targetable())

    def use(self, player, game):

        super().use(player, game)

        minion = self.target.copy(player)
        minion.active = True
        minion.exhausted = False

        # What happens if there are already 7 minions?
        self.target.remove_from_board()
        minion.add_to_board(len(player.minions))

        # When silenced, the minion should immediately come back to its previous
        # owner.  See https://twitter.com/bdbrode/status/510251195173470208
        minion.add_buff(BuffUntil(Stolen(), TurnEnded()))

    def can_use(self, player, game):
        return super().can_use(player, game) and len(player.minions) < 7


class ShadowWordDeath(Card):
    def __init__(self):
        super().__init__("Shadow Word: Death", 3, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target,
                         lambda target: target.calculate_attack() >= 5 and target.spell_targetable())

    def use(self, player, game):
        super().use(player, game)

        self.target.die(self)


class ShadowWordPain(Card):
    def __init__(self):
        super().__init__("Shadow Word: Pain", 2, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_minion_spell_target,
                         lambda target: target.calculate_attack() <= 3 and target.spell_targetable())

    def use(self, player, game):
        super().use(player, game)

        self.target.die(self)


class Shadowform(Card):
    def __init__(self):
        super().__init__("Shadowform", 3, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)

        if type(player.hero.power) is not hearthbreaker.powers.MindShatter and type(
                player.hero.power) is not hearthbreaker.powers.MindSpike:
            player.hero.power = hearthbreaker.powers.MindSpike(player.hero)
        elif type(player.hero.power) is hearthbreaker.powers.MindSpike:
            player.hero.power = hearthbreaker.powers.MindShatter(player.hero)


class Silence(Card):
    def __init__(self):
        super().__init__("Silence", 0, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.silence()


class Thoughtsteal(Card):
    def __init__(self):
        super().__init__("Thoughtsteal", 3, CHARACTER_CLASS.PRIEST,
                         CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)
        for i in range(0, 2):
            new_card = game.random_draw(game.other_player.deck.cards, lambda c: not c.drawn)
            if new_card:
                new_card = copy.copy(new_card)
                new_card.drawn = True
                if len(player.hand) < 10:
                    player.hand.append(new_card)
                    self.trigger("card_drawn", new_card)
                else:
                    player.trigger("card_destroyed", new_card)


class VelensChosen(Card):
    def __init__(self):
        super().__init__("Velen's Chosen", 3, CHARACTER_CLASS.PRIEST, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.change_attack(2)
        self.target.increase_health(4)
        self.target.add_buff(Buff(SpellDamage(1)))


class Lightbomb(Card):
    def __init__(self):
        super().__init__("Lightbomb", 6, CHARACTER_CLASS.PRIEST, CARD_RARITY.EPIC)

    def use(self, player, game):
        super().use(player, game)

        targets = copy.copy(game.other_player.minions)
        targets.extend(player.minions)

        for minion in targets:
            minion.damage(player.effective_spell_damage(minion.calculate_attack()), self)
