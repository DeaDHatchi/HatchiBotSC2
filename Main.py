import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
import random


class HatchiBot(sc2.BotAI):

    name = 'HatchiBot'
    version = "1.1.10"
    build_date = "7/5/2018"
    debug = True

    # Booleans
    message_sent = False
    fast_expand = True
    warpgate_started = False
    research_charge = False
    research_blink = False
    research_thermal_lance = False
    research_gravitic_booster = False
    attacking = False
    defending = False
    repositioning = False
    retreating = False

    # Hard cap - Max Economy
    max_active_expansions = 5

    # Hard cap - Max Units
    max_probes = 80
    max_zealots = 10
    max_stalkers = 20
    max_sentries = 3
    max_observers = 1
    max_immortals = 4
    max_colossus = 4
    max_voidrays = 4

    # Hard cap - Max Buildings
    max_gateways = 10
    max_robotics_facility = 2
    max_star_gates = 1

    async def message_send(self):
        await self.chat_send(f"{self.name} Online - Version {self.version}")
        await self.chat_send(f"Last Build Date: {self.build_date}")

    async def on_step(self, iteration):
        if not self.message_sent:
            await self.message_send()
            self.message_sent = True
        if iteration == 1:
            await self.distribute_workers()
        else:
            if iteration % 3 == 0:
                await self.distribute_workers()
        if iteration % 250 == 0:
            await self.chat_send(f"Iteration: {iteration}")

        # Build Order Priority
        await self.expand()
        await self.build_pylon()
        await self.build_worker()

        # Upgrades
        await self.upgrade_gateways()
        await self.upgrade_warpgate()
        await self.upgrade_thermal_lance()
        await self.upgrade_zealot_charge()
        await self.upgrade_gravitic_boosters()
        # await self.upgrade_stalker_blink() # Right now I don't have any Blink Logic - its useless

        # Building Tech
        await self.build_robotics_bay()
        await self.build_robotics_facility()
        await self.build_twilight_council()
        await self.build_stargate()
        await self.build_cybernetics_core()
        await self.build_gateway()
        await self.build_assimilator()

        # Build Units
        await self.build_observers()
        await self.build_colossus()
        await self.build_immortals()
        await self.build_voidrays()
        await self.build_stalkers()
        await self.build_sentries()
        await self.build_zealots()

        # Attack
        await self.defend()
        await self.attack()
        await self.reposition()

    def soft_max_gateways(self):
        return 1 + ((self.units(NEXUS).ready.amount - 1) * 3)

    def soft_max_robotics_facility(self):
        return self.units(NEXUS).ready.amount * 1

    def soft_max_probes(self):
        return self.units(NEXUS).ready.amount * 22

    def soft_max_zealots(self):
        return self.units(NEXUS).ready.amount * 2

    def soft_max_stalker(self):
        return self.units(NEXUS).ready.amount * 4

    def soft_max_sentries(self):
        return self.units(NEXUS).ready.amount * 1

    def soft_max_immortals(self):
        return self.units(NEXUS).ready.amount * 1

    def soft_max_colossus(self):
        return self.units(NEXUS).ready.amount * 1

    def soft_max_voidrays(self):
        return self.units(NEXUS).ready.amount * 1

    def can_train_probe(self):
        return self.supply_left >= 1 and \
               self.can_afford(PROBE) and \
               self.units(PROBE).amount < self.max_probes and \
               self.units(PROBE).amount < self.soft_max_probes()

    def can_train_zealot(self):
        return self.supply_left >= 2 and \
               self.can_afford(ZEALOT) and \
               self.units(ZEALOT).amount < self.max_zealots and \
               self.units(ZEALOT).amount < self.soft_max_zealots() and \
               self.units(STALKER).ready.amount >= 2

    def can_train_stalker(self):
        return self.supply_left >= 2 and \
               self.can_afford(STALKER) and \
               self.units(STALKER).amount < self.max_stalkers and \
               self.units(STALKER).amount < self.soft_max_stalker()

    def can_train_sentry(self):
        return self.supply_left >= 2 and \
               self.can_afford(SENTRY) and \
               self.units(SENTRY).amount < self.max_sentries and \
               self.units(SENTRY).amount < self.soft_max_sentries() and \
               self.units(STALKER).amount >= 2

    def can_train_observers(self):
        return self.supply_left >= 1 and \
               self.can_afford(OBSERVER) and \
               self.units(OBSERVER).amount < self.max_observers

    def can_train_immortal(self):
        return self.supply_left >= 4 and \
               self.can_afford(IMMORTAL) and \
               self.units(IMMORTAL).amount < self.max_immortals and \
               self.units(IMMORTAL).amount < self.soft_max_immortals()

    def can_train_colossus(self):
        return self.supply_left >= 6 and \
               self.can_afford(COLOSSUS) and \
               self.units(COLOSSUS).amount < self.max_colossus and \
               self.units(COLOSSUS).amount < self.soft_max_colossus()

    def can_train_voidrays(self):
        return self.supply_left >= 4 and \
               self.can_afford(VOIDRAY) and \
               self.units(VOIDRAY).amount < self.max_voidrays and \
               self.units(VOIDRAY).amount < self.soft_max_voidrays()

    def can_build_nexus(self):
        return self.can_afford(NEXUS) and \
               self.units(NEXUS).amount < self.max_active_expansions and not \
               self.already_pending(NEXUS)

    def can_build_assimilator(self):
        return self.units(PYLON).ready.amount > 0 and \
               self.units(CYBERNETICSCORE).amount > 0 and \
               self.can_afford(ASSIMILATOR) and \
               (self.units(ASSIMILATOR).amount < self.units(PROBE).amount / 11 or self.units(PROBE).amount > 45) and not \
               self.already_pending(ASSIMILATOR)

    def can_build_gateway(self):
        buildings = self.units(GATEWAY).amount + self.units(WARPGATE).amount
        return buildings < self.max_gateways and \
               buildings < self.soft_max_gateways() and \
               self.can_afford(GATEWAY)

    def can_build_cyberneticscore(self):
        return self.units(PYLON).ready.amount > 0 and \
               self.units(GATEWAY).ready.amount > 0 and \
               self.units(CYBERNETICSCORE).amount < 1 and \
               self.can_afford(CYBERNETICSCORE) and not \
               self.already_pending(CYBERNETICSCORE) and not \
               self.fast_expand

    def can_build_twilight_council(self):
        return self.units(PYLON).ready.amount > 0 and \
               self.units(CYBERNETICSCORE).ready.amount > 0 and \
               self.units(TWILIGHTCOUNCIL).ready.amount < 1 and \
               self.can_afford(TWILIGHTCOUNCIL) and not \
               self.already_pending(TWILIGHTCOUNCIL)

    def can_build_stargate(self):
        return self.units(PYLON).ready.amount > 0 and \
               self.units(CYBERNETICSCORE).ready.amount > 0 and \
               self.units(STARGATE).ready.amount < 1 and \
               self.units(ROBOTICSFACILITY).ready.amount > 0 and \
               self.can_afford(STARGATE) and not \
               self.already_pending(STARGATE)

    def can_build_robotics_facility(self):
        return self.units(PYLON).ready.amount > 0 and \
               self.units(CYBERNETICSCORE).ready.amount > 0 and \
               self.units(ROBOTICSFACILITY).ready.amount < self.units(NEXUS).ready.amount and \
               self.units(ROBOTICSFACILITY).ready.amount < self.max_robotics_facility and \
               self.can_afford(ROBOTICSFACILITY) and not \
               self.already_pending(ROBOTICSFACILITY)

    async def build_worker(self):
        for nexus in self.units(NEXUS).ready.noqueue:
            if self.can_train_probe():
                await self.do(nexus.train(PROBE))
                await self.use_chronoboost(nexus)

    async def build_pylon(self):
        supply_threashold = 5
        if self.supply_used > 60:
            supply_threashold = 10
        if self.supply_used > 100:
            supply_threashold = 15
        if self.supply_left <= supply_threashold and not self.already_pending(PYLON) and self.supply_cap <= 200:
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=nexuses.random.position.towards(self.game_info.map_center, 5))

    async def expand(self):
        if self.can_build_nexus():
            await self.expand_now()
            if self.fast_expand:
                self.fast_expand = False

    async def build_assimilator(self):
        for nexus in self.units(NEXUS).ready:
            vaspenes = self.state.vespene_geyser.closer_than(10.0, nexus)
            for vaspene in vaspenes:
                if self.can_build_assimilator():
                    worker = self.select_build_worker(vaspene.position)
                    if worker is None:
                        break
                    if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
                        await self.do(worker.build(ASSIMILATOR, vaspene))

    async def build_gateway(self):
        if self.units(PYLON).ready.amount > 0:
            if self.can_build_gateway():
                pylon = self.units(PYLON).ready.random
                if self.units(CYBERNETICSCORE).amount > 0:
                    await self.build(GATEWAY, near=pylon.position.towards(self.game_info.map_center, 5))
                else:
                    if self.units(GATEWAY).amount < 1:
                        await self.build(GATEWAY, near=pylon.position.towards(self.game_info.map_center, 5))

    async def build_cybernetics_core(self):
        if self.can_build_cyberneticscore():
            pylon = self.units(PYLON).ready.random
            await self.build(CYBERNETICSCORE, near=pylon.position.towards(self.game_info.map_center, 5))

    async def build_twilight_council(self):
        if self.can_build_twilight_council():
            pylon = self.units(PYLON).ready.random
            await self.build(TWILIGHTCOUNCIL, near=pylon.position.towards(self.game_info.map_center, 5))

    async def build_stargate(self):
        if self.can_build_stargate():
            pylon = self.units(PYLON).ready.random
            await self.build(STARGATE, near=pylon.position.towards(self.game_info.map_center, 5))

    async def build_robotics_facility(self):
        if self.units(PYLON).ready.amount > 0 and self.units(CYBERNETICSCORE).ready.amount > 0:
            if self.units(ROBOTICSFACILITY).ready.amount < self.units(NEXUS).ready.amount and not self.already_pending(ROBOTICSFACILITY):
                if self.units(ROBOTICSFACILITY).ready.amount < self.max_robotics_facility:
                    if self.can_afford(ROBOTICSFACILITY):
                        pylon = self.units(PYLON).ready.random
                        await self.build(ROBOTICSFACILITY, near=pylon.position.towards(self.game_info.map_center, 5))

    async def build_robotics_bay(self):
        if self.units(PYLON).ready.amount > 0 and self.units(ROBOTICSFACILITY).ready.amount > 0:
            if self.units(ROBOTICSBAY).ready.amount < 1 and not self.already_pending(ROBOTICSBAY):
                if self.can_afford(ROBOTICSBAY):
                    pylon = self.units(PYLON).ready.random
                    await self.build(ROBOTICSBAY, near=pylon.position.towards(self.game_info.map_center, 5))

    async def upgrade_warpgate(self):
        if self.units(CYBERNETICSCORE).ready.amount > 0:
            if self.can_afford(RESEARCH_WARPGATE) and not self.warpgate_started:
                ccore = self.units(CYBERNETICSCORE).ready.first
                await self.do(ccore(RESEARCH_WARPGATE))
                await self.use_chronoboost(ccore)
                self.warpgate_started = True

    async def upgrade_gateways(self):
        for gateway in self.units(GATEWAY).ready:
            abilities = await self.get_available_abilities(gateway)
            if AbilityId.MORPH_WARPGATE in abilities and self.can_afford(AbilityId.MORPH_WARPGATE):
                await self.do(gateway(MORPH_WARPGATE))

    async def morph_warpgate(self, gateway):
        abilities = await self.get_available_abilities(gateway)
        if AbilityId.MORPH_WARPGATE in abilities and self.can_afford(AbilityId.MORPH_WARPGATE):
            await self.do(gateway(MORPH_WARPGATE))

    async def warp_new_units(self, warpgate, warppoint, unit=STALKER, warpId=AbilityId.WARPGATETRAIN_STALKER):
            abilities = await self.get_available_abilities(warpgate)
            if AbilityId.WARPGATETRAIN_ZEALOT in abilities:
                pos = warppoint.position.to2.random_on_distance(4)
                placement = await self.find_placement(warpId, pos, placement_step=1)
                if placement is None:
                    return
                await self.do(warpgate.warp_in(unit, placement))

    async def build_zealots(self):
        if len(self.units(WARPGATE).ready) < 1:
            for gateway in self.units(GATEWAY).ready.noqueue:
                await self.morph_warpgate(gateway)
                if self.can_train_zealot():
                    await self.do(gateway.train(ZEALOT))
        else:
            for warpgate in self.units(WARPGATE).ready:
                if self.can_train_zealot():
                    await self.warp_new_units(warpgate,
                                              self.closest_pylon_to_reposition_location(),
                                              unit=ZEALOT,
                                              warpId=AbilityId.WARPGATETRAIN_ZEALOT)

    async def build_stalkers(self):
        if len(self.units(WARPGATE).ready) < 1:
            for gateway in self.units(GATEWAY).ready.noqueue:
                await self.morph_warpgate(gateway)
                if self.can_train_stalker():
                    await self.do(gateway.train(STALKER))
        else:
            for warpgate in self.units(WARPGATE).ready:
                if self.can_train_stalker():
                    await self.warp_new_units(warpgate,
                                              self.closest_pylon_to_reposition_location(),
                                              unit=STALKER,
                                              warpId=AbilityId.WARPGATETRAIN_STALKER)

    async def build_sentries(self):
        if len(self.units(WARPGATE).ready) < 1:
            for gateway in self.units(GATEWAY).ready.noqueue:
                await self.morph_warpgate(gateway)
                if self.can_train_sentry():
                    await self.do(gateway.train(SENTRY))
        else:
            for warpgate in self.units(WARPGATE).ready:
                if self.can_train_sentry():
                    await self.warp_new_units(warpgate,
                                              self.closest_pylon_to_reposition_location(),
                                              unit=SENTRY,
                                              warpId=AbilityId.WARPGATETRAIN_SENTRY)

    async def build_observers(self):
        for robo in self.units(ROBOTICSFACILITY).ready.noqueue:
            if self.can_train_observers():
                await self.do(robo.train(OBSERVER))

    async def build_immortals(self):
        for robo in self.units(ROBOTICSFACILITY).ready.noqueue:
            if self.can_train_immortal():
                await self.do(robo.train(IMMORTAL))

    async def build_colossus(self):
        if len(self.units(ROBOTICSBAY).ready) > 0:
            for robo in self.units(ROBOTICSFACILITY).ready.noqueue:
                if self.can_train_colossus():
                    await self.do(robo.train(COLOSSUS))

    async def build_voidrays(self):
        if len(self.units(STARGATE).ready) > 0:
            for sg in self.units(STARGATE).ready.noqueue:
                if self.can_train_voidrays():
                    await self.do(sg.train(VOIDRAY))

    async def upgrade_zealot_charge(self):
        if self.units(TWILIGHTCOUNCIL).ready.amount > 0:
            if self.can_afford(RESEARCH_CHARGE) and not self.research_charge:
                tcouncil = self.units(TWILIGHTCOUNCIL).ready.first
                if tcouncil.noqueue:
                    await self.do(tcouncil(RESEARCH_CHARGE))
                    await self.use_chronoboost(tcouncil)
                    self.research_charge = True

    async def upgrade_stalker_blink(self):
        if self.units(TWILIGHTCOUNCIL).ready.amount > 0:
            if self.can_afford(RESEARCH_BLINK) and not self.research_blink:
                tcouncil = self.units(TWILIGHTCOUNCIL).ready.first
                if tcouncil.noqueue:
                    await self.do(tcouncil(RESEARCH_BLINK))
                    await self.use_chronoboost(tcouncil)
                    self.research_blink = True

    async def upgrade_thermal_lance(self):
        if self.units(ROBOTICSBAY).ready.amount > 0:
            if self.can_afford(RESEARCH_EXTENDEDTHERMALLANCE) and not self.research_thermal_lance:
                robobay = self.units(ROBOTICSBAY).ready.first
                if robobay.noqueue:
                    await self.do(robobay(RESEARCH_EXTENDEDTHERMALLANCE))
                    await self.use_chronoboost(robobay)
                    self.research_thermal_lance = True

    async def upgrade_gravitic_boosters(self):
        if self.units(ROBOTICSBAY).ready.amount > 0:
            if self.can_afford(RESEARCH_GRAVITICBOOSTER) and not self.research_gravitic_booster and self.research_thermal_lance:
                robobay = self.units(ROBOTICSBAY).ready.first
                if robobay.noqueue:
                    await self.do(robobay(RESEARCH_GRAVITICBOOSTER))
                    await self.use_chronoboost(robobay)
                    self.research_gravitic_booster = True

    async def use_chronoboost(self, building):
        for nexus in self.units(NEXUS).ready:
            if nexus.energy > 50:
                if not building.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                    await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, building))

    def closest_nexus_to_enemy(self):
        return self.units(NEXUS).closest_to(self.enemy_start_locations[0]).position

    def closest_pylon_to_reposition_location(self):
        return self.units(PYLON).ready.closest_to(self.enemy_start_locations[0].position)

    def reposition_location(self):
        return self.game_info.map_center.towards(self.closest_nexus_to_enemy(), 120 / self.units(NEXUS).amount)

    def enemy_threats(self, units):
        enemies = []
        for unit in units:
            if unit.is_enemy:
                if not unit.is_structure:
                    enemies.append(unit)
        return enemies

    def get_enemy_threats(self):
        return self.enemy_threats(self.known_enemy_units)

    def total_army_value(self, units):
        total = 0
        for unit in units:
            total += unit._type_data.cost.minerals + (unit._type_data.cost.vespene * 1.25)
        return total

    def find_target(self, state):
        if len(self.get_enemy_threats()) > 0:
            return random.choice(self.get_enemy_threats())
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        elif len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        else:
            return self.enemy_start_locations[0]

    def get_idle_attacking_units(self):
        attacking_units = []
        if self.units(STALKER).idle.amount > 0:
            attacking_units += self.units(STALKER).idle
        if self.units(ZEALOT).idle.amount > 0:
            attacking_units += self.units(ZEALOT).idle
        if self.units(OBSERVER).idle.amount > 0:
            attacking_units += self.units(OBSERVER).idle
        if self.units(IMMORTAL).idle.amount > 0:
            attacking_units += self.units(IMMORTAL).idle
        if self.units(COLOSSUS).idle.amount > 0:
            attacking_units += self.units(COLOSSUS).idle
        if self.units(VOIDRAY).idle.amount > 0:
            attacking_units += self.units(VOIDRAY).idle
        if self.units(SENTRY).idle.amount > 0:
            attacking_units += self.units(SENTRY).idle
        return attacking_units

    def get_attacking_units(self):
        attacking_units = []
        if self.units(STALKER).idle.amount > 0:
            attacking_units += self.units(STALKER).idle
        if self.units(ZEALOT).idle.amount > 0:
            attacking_units += self.units(ZEALOT).idle
        if self.units(OBSERVER).idle.amount > 0:
            attacking_units += self.units(OBSERVER).idle
        if self.units(IMMORTAL).idle.amount > 0:
            attacking_units += self.units(IMMORTAL).idle
        if self.units(COLOSSUS).idle.amount > 0:
            attacking_units += self.units(COLOSSUS).idle
        if self.units(VOIDRAY).idle.amount > 0:
            attacking_units += self.units(VOIDRAY).idle
        if self.units(SENTRY).idle.amount > 0:
            attacking_units += self.units(SENTRY).idle
        return attacking_units

    def total_attacking_units(self):
        total_units = []
        if self.units(STALKER).amount > 0:
            total_units += self.units(STALKER).ready
        if self.units(ZEALOT).amount > 0:
            total_units += self.units(ZEALOT).ready
        if self.units(OBSERVER).amount > 0:
            total_units += self.units(OBSERVER).ready
        if self.units(IMMORTAL).amount > 0:
            total_units += self.units(IMMORTAL).ready
        if self.units(COLOSSUS).amount > 0:
            total_units += self.units(COLOSSUS).ready
        if self.units(VOIDRAY).amount > 0:
            total_units += self.units(VOIDRAY).ready
        if self.units(SENTRY).amount > 0:
            total_units += self.units(SENTRY).ready
        return total_units

    def get_all_attacking_units_even_unready(self):
        total_units = []
        if self.units(STALKER).amount > 0:
            total_units += self.units(STALKER)
        if self.units(ZEALOT).amount > 0:
            total_units += self.units(ZEALOT)
        if self.units(OBSERVER).amount > 0:
            total_units += self.units(OBSERVER)
        if self.units(IMMORTAL).amount > 0:
            total_units += self.units(IMMORTAL)
        if self.units(COLOSSUS).amount > 0:
            total_units += self.units(COLOSSUS)
        if self.units(VOIDRAY).amount > 0:
            total_units += self.units(VOIDRAY)
        if self.units(SENTRY).amount > 0:
            total_units += self.units(SENTRY)
        return total_units

    async def should_we_retreat(self):
        return len(self.get_enemy_threats()) > 5 and \
               self.total_army_value(self.get_enemy_threats()) > self.total_army_value(self.total_attacking_units())

    async def attack(self):
        if await self.should_we_retreat():
            if self.attacking:
                await self.chat_send("Attacking Flag Off!")
                self.attacking = False
            await self.retreat()

            return
        if len(self.total_attacking_units()) > 20:
            if not self.attacking:
                await self.chat_send("Looks like we are Attacking!")
                self.retreating = False
                self.defending = False
                self.attacking = True
            for s in self.get_all_attacking_units_even_unready():
                await self.do(s.attack(self.find_target(self.state)))

    async def defend(self):
        if not self.attacking:
            if await self.should_we_retreat():
                await self.retreat()
                return
            if len(self.get_attacking_units()) > 3:
                if len(self.enemy_threats(self.known_enemy_units)) > 0:
                    if not self.defending:
                        await self.chat_send("Looks like we are Defending!")
                        self.defending = True
                    for s in self.get_all_attacking_units_even_unready():
                        await self.do(s.attack(self.find_target(self.state)))
                else:
                    if self.defending:
                        self.defending = False
                        await self.chat_send("Defending Flag Off")

    async def reposition(self):
        if not self.attacking and not self.defending:
            if len(self.get_attacking_units()) > 0:
                if not self.repositioning:
                    self.repositioning = True
                    await self.chat_send("Repositioning Army!")
                for s in self.total_attacking_units():
                    if s.distance_to(self.reposition_location()) > 10:
                        await self.do(s.move(self.reposition_location()))
        else:
            self.repositioning = False

    async def retreat(self):
        if not self.retreating:
            await self.chat_send("Retreating Army!")
            self.retreating = True
        for s in self.get_all_attacking_units_even_unready():
            if s.distance_to(self.reposition_location()) > 40:
                await self.do(s.move(self.reposition_location()))

    def __repr__(self):
        return f'{self.name} - {self.version}'


if __name__ == '__main__':

    Races = [Race.Protoss, Race.Terran, Race.Zerg]
    Difficulties = [Difficulty.Hard]
    Maps = ["BlackpinkLE"]

    run_game(maps.get(random.choice(Maps)), [
        Bot(race=Race.Protoss, ai=HatchiBot()),
        Computer(race=random.choice(Races),
                 difficulty=random.choice(Difficulties))
        ], realtime=True)
