import hearthbreaker
from hearthbreaker.constants import MINION_TYPE
from hearthbreaker.tags.base import Condition, Amount


class HasSecret(Condition):
    def evaluate(self, target, *args):
        return len(target.player.secrets) > 0

    def __to_json__(self):
        return {
            'name': 'has_secret'
        }


class IsSecret(Condition):
    def evaluate(self, target, obj, *args):
        return obj.is_secret()

    def __to_json__(self):
        return {
            'name': 'is_secret'
        }


class IsSpell(Condition):
    def evaluate(self, target, obj, *args):
        return obj.is_spell()

    def __to_json__(self):
        return {
            'name': 'is_spell'
        }


class CardMatches(Condition):
    def __init__(self, selector):
        super().__init__()
        self.selector = selector

    def evaluate(self, target, card, *args):
        return self.selector.match(target, card)

    def __to_json__(self):
        return {
            'name': 'card_matches',
            'selector': self.selector,
        }

    def __from_json__(self, selector):
        selector = hearthbreaker.tags.selector.Selector.from_json(**selector)
        self.__init__(selector)
        return self


class HasOverload(Condition):

    def evaluate(self, target, card, args):
        return card.overload > 0

    def __to_json__(self):
        return {
            'name': 'has_overload'
        }


class ManaCost(Condition):
    def __init__(self, cost):
        self.cost = cost

    def evaluate(self, target, obj, *args):
        return obj.mana == self.cost

    def __to_json__(self):
        return {
            'name': 'mana_cost',
            'cost': self.cost
        }


class CardRarity(Condition):
    def __init__(self, rarity):
        self.rarity = rarity

    def evaluate(self, target, obj, *args):
        return obj.is_card() and obj.rarity == self.rarity

    def __to_json__(self):
        return {
            'name': 'card_rarity',
            'rarity': self.rarity
        }


class IsMinion(Condition):
    def evaluate(self, target, minion, *args):
        return minion.is_minion()

    def __to_json__(self):
        return {
            "name": 'is_minion'
        }


class IsWeapon(Condition):
    def evaluate(self, target, weapon, *args):
        return weapon.is_weapon()

    def __to_json__(self):
        return {
            "name": 'is_weapon'
        }


class NotCurrentTarget(Condition):
    def evaluate(self, target, minion, *args):
        return minion is not target.current_target

    def __to_json__(self):
        return {
            'name': 'not_current_target'
        }


class MinionIsTarget(Condition):
    def evaluate(self, target, minion, *args):
        return minion is target

    def __to_json__(self):
        return {
            'name': 'minion_is_target'
        }


class MinionIsNotTarget(Condition):
    def evaluate(self, target, minion, *args):
        return minion is not target

    def __to_json__(self):
        return {
            'name': 'minion_is_not_target'
        }


class CardIsNotTarget(Condition):
    def evaluate(self, target, card, *args):
        return target.card is not card

    def __to_json__(self):
        return {
            'name': 'card_is_not_target'
        }


class Not(Condition):
    def __init__(self, condition):
        super().__init__()
        self.condition = condition

    def evaluate(self, target, *args):
        return not self.condition.evaluate(target, *args)

    def __to_json__(self):
        return {
            'name': 'not',
            'condition': self.condition,
        }

    def __from_json__(self, condition):
        self.condition = Condition.from_json(**condition)
        return self


class IsType(Condition):
    def __init__(self, minion_type, include_self=False):
        super().__init__()
        self.minion_type = minion_type
        self.include_self = include_self

    def evaluate(self, target, minion, *args):
        if minion.is_minion():
            if not minion.is_card():
                if self.include_self or target is not minion:
                    return minion.card.minion_type == self.minion_type
                return False
            else:
                return minion.minion_type == self.minion_type
        return False

    def __to_json__(self):
        return {
            'name': 'is_type',
            'include_self': self.include_self,
            'minion_type': MINION_TYPE.to_str(self.minion_type)
        }

    def __from_json__(self, minion_type, include_self=False):
        self.minion_type = MINION_TYPE.from_str(minion_type)
        self.include_self = include_self
        return self


class MinionHasDeathrattle(Condition):
    def __to_json__(self):
        return {
            'name': 'minion_has_deathrattle'
        }

    def __init__(self):
        super().__init__()

    def evaluate(self, target, minion, *args):
        return len(minion.deathrattle) > 0


class HasStatus(Condition):
    def __init__(self, status):
        self.status = status

    def __to_json__(self):
        return {
            'name': 'has_status',
            'status': self.status,
        }

    def evaluate(self, target, minion, *args):
        return getattr(minion, self.status)


class MinionCountIs(Condition):
    def __init__(self, count):
        self.count = count

    def evaluate(self, target, *args):
        return len(target.player.minions) == self.count

    def __to_json__(self):
        return {
            'name': 'minion_count_is',
            'count': self.count,
        }


class OpponentMinionCountIsGreaterThan(Condition):
    def __init__(self, count):
        self.count = count

    def evaluate(self, target, *args):
        return len(target.player.opponent.minions) > self.count

    def __to_json__(self):
        return {
            'name': 'opponent_minion_count_is_greater_than',
            'count': self.count,
        }


class GreaterThan(Condition, metaclass=Amount):
    def __init__(self, value):
        self.value = value

    def evaluate(self, target, *args):
        return self.get_amount(target, target, *args) > self.value

    def __to_json__(self):
        return {
            'name': 'greater_than',
            'value': self.value,
        }


class Adjacent(Condition):
    def __to_json__(self):
        return {
            'name': 'adjacent'
        }

    def __init__(self):
        super().__init__()

    def evaluate(self, target, minion, *args):
        return minion.player is target.player and \
            (minion.index == target.index - 1) or (minion.index == target.index + 1)


class AttackLessThanOrEqualTo(Condition):
    def __init__(self, attack_max, include_self=False):
        super().__init__()
        self.attack_max = attack_max
        self.include_self = include_self

    def evaluate(self, target, minion, *args):
        return (self.include_self or target is not minion) and minion.calculate_attack() <= self.attack_max

    def __to_json__(self):
        return {
            'name': 'attack_less_than_or_equal_to',
            'include_self': self.include_self,
            'attack_max': self.attack_max
        }


class AttackGreaterThan(Condition):
    def __init__(self, attack_min, include_self=False):
        super().__init__()
        self.attack_min = attack_min
        self.include_self = include_self

    def evaluate(self, target, minion, *args):
        return (self.include_self or target is not minion) and minion.calculate_attack() > self.attack_min

    def __to_json__(self):
        return {
            'name': 'attack_greater_than',
            'include_self': self.include_self,
            'attack_min': self.attack_min
        }


class BaseAttackEqualTo(Condition):
    def __init__(self, attack_equal, include_self=False):
        super().__init__()
        self.attack_equal = attack_equal
        self.include_self = include_self

    def evaluate(self, target, minion, *args):
        return (self.include_self or target is not minion) and minion.base_attack == self.attack_equal

    def __to_json__(self):
        return {
            'name': 'attack_equal_to',
            'include_self': self.include_self,
            'base_attack_equal': self.attack_equal
        }


class IsDamaged(Condition):
    def evaluate(self, target, minion, *args):
        return minion.health != minion.calculate_max_health()

    def __to_json__(self):
        return {
            'name': 'is_damaged'
        }


class InGraveyard(Condition):
    def __init__(self, card):
        if isinstance(card, str):
            self.card = card
        else:
            self.card = card.ref_name

    def evaluate(self, target, *args):
        return self.card in target.player.graveyard or self.card in target.player.opponent.graveyard

    def __to_json__(self):
        return {
            'name': 'in_graveyard',
            'card': self.card
        }


class OneIn(Condition):
    def __init__(self, amount):
        self.amount = amount

    def evaluate(self, target, *args):
        return 0 == target.game.random_amount(0, self.amount - 1)

    def __to_json__(self):
        return {
            'name': 'one_in',
            'amount': self.amount,
        }


class HasDivineShield(Condition):
    def evaluate(self, target, minion, *args):
        return minion.divine_shield

    def __to_json__(self):
        return {
            'name': 'has_divine_shield',
        }
