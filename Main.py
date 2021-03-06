import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
import random
from time import time


class HatchiBot(sc2.BotAI):

    name = 'HatchiBot'
    version = "1.2.2"
    last_build_date = "7/13/2018"

    # Debug Info
    debug = True
    time_last = None
    iterations_per_second = None

    # Booleans
    message_sent = False
    fast_expand = True
    warpgate_started = False
    research_charge = False
    research_blink = False
    research_thermal_lance = False
    research_gravitic_booster = False
    research_resonating_glaives = False
    research_graviton_catapult = False

    PROTOSSGROUNDWEAPONSLEVEL1 = False
    PROTOSSGROUNDWEAPONSLEVEL2 = False
    PROTOSSGROUNDWEAPONSLEVEL3 = False
    PROTOSSGROUNDARMORLEVEL1 = False
    PROTOSSGROUNDARMORLEVEL2 = False
    PROTOSSGROUNDARMORLEVEL3 = False

    PROTOSSAIRWEAPONSLEVEL1 = False
    PROTOSSAIRWEAPONSLEVEL2 = False
    PROTOSSAIRWEAPONSLEVEL3 = False
    PROTOSSAIRARMORLEVEL1 = False
    PROTOSSAIRARMORLEVEL2 = False
    PROTOSSAIRARMORLEVEL3 = False

    """
    CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL1 = 1562
    CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL2 = 1563
    CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL3 = 1564
    CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL1 = 1565
    CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL2 = 1566
    CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL3 = 1567
    """

    attacking = False
    defending = False
    repositioning = False
    retreating = False
    regrouping = False

    # Strategy
    sky_protoss_switch = False
    priority_building = None

    # Hard cap - Max Economy
    max_active_expansions = 7

    # Hard cap - Max Units
    max_probes = 80
    max_zealots = 15
    max_stalkers = 15
    max_adepts = 10
    max_sentries = 3
    max_observers = 1
    max_immortals = 4
    max_colossus = 4
    max_voidrays = 4
    max_carriers = 12

    # Hard cap - Max Buildings
    max_gateways = 5
    max_forges = 1
    max_cyberneticscore = 1
    max_robotics_facility = 2
    max_stargates = 4

    # Units
    number_of_attacking_units = 25

    # Building Properties
    @property
    def nexuses(self):
        return self.units(NEXUS)

    @property
    def pylons(self):
        return self.units(PYLON)

    @property
    def assimilators(self):
        return self.units(ASSIMILATOR)

    @property
    def gateways(self):
        return self.units(GATEWAY)

    @property
    def forges(self):
        return self.units(FORGE)

    @property
    def cyberneticscores(self):
        return self.units(CYBERNETICSCORE)

    @property
    def roboticsfacilities(self):
        return self.units(ROBOTICSFACILITIES)

    @property
    def stargates(self):
        return self.units(STARGATE)

    @property
    def twilightcouncils(self):
        return self.units(TWILIGHTCOUNCIL)

    @property
    def roboticsbays(self):
        return self.units(ROBOTICSBAY)

    @property
    def warpgates(self):
        return self.units(WARPGATE)

    # Unit Properties
    @property
    def probes(self):
        return self.units(PROBE)

    @property
    def zealots(self):
        return self.units(ZEALOT)

    @property
    def stalkers(self):
        return self.units(STALKER)

    @property
    def adepts(self):
        return self.units(ADEPT)

    @property
    def sentries(self):
        return self.units(SENTRY)

    @property
    def immortals(self):
        return self.units(IMMORTAL)

    @property
    def colossus(self):
        return self.units(COLOSSUS)

    @property
    def observers(self):
        return self.units(OBSERVER)

    @property
    def voidrays(self):
        return self.units(VOIDRAY)

    @property
    def carriers(self):
        return self.units(CARRIER)

    @property
    def ideal_nexus_count(self):
        return self.units(PROBE).ready.amount * 22

    @property
    def active_nexuses(self):
        # TODO: I want to create a number of active expansions. active expansions are expansions that are ready and have - 7/13/2018
        # TODO: an ideal number of workers. Active Expansions have 8 mineral fields and 2 vespene geysers - 7/13/2018
        return

    @property
    def enemy_threats(self):
        return self.known_enemy_units.not_structure

    @property
    def near_by_enemy_threats(self):
        # TODO: This logic could be improved for performance. Don't know how yet - 7/11/2018
        total = None
        for nexus in self.nexuses:
            group = self.enemy_threats.filter(lambda unit: self.enemy_threats.closer_than(20, nexus))
            if not total:
                total = group
            else:
                total += group
        return total

    @property
    def attacking_units(self):
        return self.zealots | \
               self.stalkers | \
               self.sentries | \
               self.adepts | \
               self.observers | \
               self.immortals | \
               self.colossus | \
               self.voidrays | \
               self.carriers

    @property
    def idle_attacking_units(self):
        return self.attacking_units.idle

    @property
    def ready_attacking_units(self):
        return self.attacking_units.ready

    @property
    def ready_idle_attacking_units(self):
        return self.idle_attacking_units.ready

    @property
    def sky_protoss_check(self):
        if self.units(NEXUS).ready.amount >= 4:
            return True
        else:
            return False

    async def message_send(self):
        await self.chat_send(f"{self.name} Online - Version {self.version}")
        await self.chat_send(f"Last Build Date: {self.last_build_date}")

    async def on_step(self, iteration):
        if not self.message_sent:
            await self.message_send()
            self.message_sent = True

        # Debugging Information

        if iteration == 0:
            self.time_last = time()
        if self.debug:
            if iteration % 250 == 0:
                await self.chat_send(f"Iteration: {iteration}")
        if iteration % 1000 == 0 and iteration > 0:
            current_time = time()
            self.iterations_per_second = 1000 // (current_time - self.time_last)
            self.time_last = current_time
            if self.debug:
                await self.chat_send(f'Iterations Per Second: {self.iterations_per_second}')

        # Strategy Check
        if self.sky_protoss_check:
            self.sky_protoss_switch = True

        # Worker Distribution Logic
        await self.distribute_workers()

        # Build Order Priority
        await self.expansion_commander()

        # Upgrades
        await self.upgrade_gateways()
        await self.upgrade_warpgate()

        if self.minerals > 100 and self.priority_building is None:
            await self.upgrade_commander()

        # Building Tech
            await self.building_commander()

        # Build Units
            await self.recruit_commander()

        # Attack
        await self.army_commander()

    def soft_max_assimilators(self):
        return self.units(NEXUS).ready.amount * 2

    def soft_max_gateways(self):
        return 1 + ((self.units(NEXUS).ready.amount - 1) * 2)

    def soft_max_forges(self):
        return self.units(NEXUS).ready.amount // 3 + 1

    def soft_max_robotics_facility(self):
        return self.units(NEXUS).ready.amount * 1

    def soft_max_stargates(self):
        return self.units(NEXUS).ready.amount - 1

    def soft_max_probes(self):
        return self.units(NEXUS).amount * 22

    def soft_max_zealots(self):
        return self.units(NEXUS).ready.amount * 3

    def soft_max_stalkers(self):
        return self.units(NEXUS).ready.amount * 3

    def soft_max_adepts(self):
        return self.units(NEXUS).ready.amount * 1

    def soft_max_sentries(self):
        return self.units(NEXUS).ready.amount * 1

    def soft_max_immortals(self):
        return self.units(NEXUS).ready.amount * 1

    def soft_max_colossus(self):
        return self.units(NEXUS).ready.amount * 1

    def soft_max_voidrays(self):
        return self.units(NEXUS).ready.amount * 1

    def soft_max_carriers(self):
        return self.units(NEXUS).ready.amount * 3

    async def can_train_probe(self):
        return self.supply_left >= 1 and \
               self.can_afford(PROBE) and \
               self.units(PROBE).amount < self.max_probes and \
               self.units(PROBE).amount < self.soft_max_probes()

    async def can_train_zealot(self):
        return self.supply_left >= 2 and \
               self.can_afford(ZEALOT) and \
               self.units(ZEALOT).amount < self.max_zealots and \
               self.units(ZEALOT).amount < self.soft_max_zealots() and \
               self.units(STALKER).ready.amount >= 2

    async def can_train_stalker(self):
        return self.supply_left >= 2 and \
               self.can_afford(STALKER) and \
               self.units(STALKER).amount < self.max_stalkers and \
               self.units(STALKER).amount < self.soft_max_stalkers()

    async def can_train_adepts(self):
        return self.supply_left >= 2 and \
               self.can_afford(ADEPT) and \
               self.units(ADEPT).amount < self.max_adepts and \
               self.units(ADEPT).amount < self.soft_max_adepts()

    async def can_train_sentry(self):
        return self.supply_left >= 2 and \
               self.can_afford(SENTRY) and \
               self.units(SENTRY).amount < self.max_sentries and \
               self.units(SENTRY).amount < self.soft_max_sentries() and \
               self.units(STALKER).amount >= 2

    async def can_train_observers(self):
        return self.supply_left >= 1 and \
               self.can_afford(OBSERVER) and \
               self.units(OBSERVER).amount < self.max_observers

    async def can_train_immortal(self):
        return self.supply_left >= 4 and \
               self.can_afford(IMMORTAL) and \
               self.units(IMMORTAL).amount < self.max_immortals and \
               self.units(IMMORTAL).amount < self.soft_max_immortals()

    async def can_train_colossus(self):
        return self.supply_left >= 6 and \
               self.can_afford(COLOSSUS) and \
               self.units(COLOSSUS).amount < self.max_colossus and \
               self.units(COLOSSUS).amount < self.soft_max_colossus()

    async def can_train_voidrays(self):
        return self.supply_left >= 4 and \
               self.can_afford(VOIDRAY) and \
               self.units(VOIDRAY).amount < self.max_voidrays and \
               self.units(VOIDRAY).amount < self.soft_max_voidrays()

    async def can_train_carriers(self):
        return self.supply_left >= 6 and \
               self.can_afford(CARRIER) and \
               self.units(CARRIER).amount < self.max_carriers and \
               self.units(CARRIER).amount < self.soft_max_carriers()

    async def can_build_nexus(self):
        return self.can_afford(NEXUS) and \
               self.units(PROBE).ready.amount / 15 > self.units(NEXUS).ready.amount and \
               self.units(NEXUS).amount < self.max_active_expansions and not \
               self.already_pending(NEXUS)

    async def can_build_assimilator(self):
        return self.units(PYLON).ready.amount > 0 and \
               self.units(CYBERNETICSCORE).amount > 0 and \
               self.can_afford(ASSIMILATOR) and \
               (self.units(ASSIMILATOR).amount < self.units(PROBE).amount / 11 or self.units(PROBE).amount > 45) and not \
               self.already_pending(ASSIMILATOR)

    async def can_build_gateway(self):
        buildings = self.units(GATEWAY).amount + self.units(WARPGATE).amount
        return buildings < self.max_gateways and \
               buildings < self.soft_max_gateways() and \
               self.can_afford(GATEWAY)

    async def can_build_forge(self):
        return self.units(PYLON).ready.amount > 0 and \
               self.units(FORGE).amount < self.max_forges and \
               self.units(FORGE).amount < self.soft_max_forges() and \
               self.units(CYBERNETICSCORE).amount > 0 and \
               self.can_afford(FORGE)

    async def can_build_cyberneticscore(self):
        if self.sky_protoss_switch:
            self.max_cyberneticscore = 2
        return self.units(PYLON).ready.amount > 0 and \
               self.units(GATEWAY).ready.amount > 0 and \
               self.units(CYBERNETICSCORE).amount < self.max_cyberneticscore and \
               self.can_afford(CYBERNETICSCORE) and not \
               self.already_pending(CYBERNETICSCORE) and not \
               self.fast_expand

    async def can_build_twilight_council(self):
        return self.units(PYLON).ready.amount > 0 and \
               self.units(CYBERNETICSCORE).ready.amount > 0 and \
               self.units(TWILIGHTCOUNCIL).ready.amount < 1 and \
               self.can_afford(TWILIGHTCOUNCIL) and not \
               self.already_pending(TWILIGHTCOUNCIL)

    async def can_build_stargate(self):
        return self.units(PYLON).ready.amount > 0 and \
               self.units(CYBERNETICSCORE).ready.amount > 0 and \
               self.units(STARGATE).amount < self.max_stargates and \
               self.units(STARGATE).amount < self.soft_max_stargates() and \
               self.units(ROBOTICSFACILITY).ready.amount > 0 and \
               self.can_afford(STARGATE) and not \
               self.already_pending(STARGATE)

    async def can_build_robotics_facility(self):
        return self.units(PYLON).ready.amount > 0 and \
               self.units(CYBERNETICSCORE).ready.amount > 0 and \
               self.units(ROBOTICSFACILITY).ready.amount < self.units(NEXUS).ready.amount and \
               self.units(ROBOTICSFACILITY).ready.amount < self.max_robotics_facility and \
               self.can_afford(ROBOTICSFACILITY) and not \
               self.already_pending(ROBOTICSFACILITY)

    async def can_build_fleet_beacon(self):
        return self.units(PYLON).ready.amount > 0 and \
               self.units(STARGATE).ready.amount > 0 and \
               self.units(FLEETBEACON).amount < 1 and \
               self.units(NEXUS).amount >= 3 and not \
               self.already_pending(FLEETBEACON)

    async def can_build_robotics_bay(self):
        return self.units(PYLON).ready.amount > 0 and \
               self.units(NEXUS).ready.amount >= 3 and \
               self.units(ROBOTICSFACILITY).ready.amount > 0 and \
               self.units(ROBOTICSBAY).amount < 1 and \
               self.can_afford(ROBOTICSBAY) and not \
               self.already_pending(ROBOTICSBAY)

    async def build_worker(self):
        for nexus in self.units(NEXUS).ready.noqueue:
            if await self.can_train_probe():
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
                    await self.build(PYLON, near=nexuses.random.position.towards(self.game_info.map_center, 8))

    async def expand(self):
        if self.ideal_nexus_count < self.units(NEXUS).ready.amount and not self.already_pending(NEXUS):
            self.priority_building = NEXUS
        if await self.can_build_nexus():
            await self.expand_now()
            if self.fast_expand:
                self.fast_expand = False
            if self.priority_building == NEXUS:
                self.priority_building = None

    async def build_assimilator(self):
        for nexus in self.units(NEXUS).ready:
            vaspenes = self.state.vespene_geyser.closer_than(10.0, nexus)
            for vaspene in vaspenes:
                if await self.can_build_assimilator():
                    worker = self.select_build_worker(vaspene.position)
                    if worker is None:
                        break
                    if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
                        await self.do(worker.build(ASSIMILATOR, vaspene))

    async def build_gateway(self):
        if self.units(PYLON).ready.amount > 0:
            if await self.can_build_gateway():
                pylon = self.units(PYLON).ready.random
                if self.units(CYBERNETICSCORE).amount > 0:
                    await self.build(GATEWAY, near=pylon.position.towards(self.game_info.map_center, 8))
                else:
                    if self.units(GATEWAY).amount < 1:
                        await self.build(GATEWAY, near=pylon.position.towards(self.game_info.map_center, 8))

    async def build_forge(self):
        if await self.can_build_forge():
            pylon = self.units(PYLON).ready.random
            await self.build(FORGE, near=pylon.position.towards(self.game_info.map_center, 8))

    async def build_cybernetics_core(self):
        if await self.can_build_cyberneticscore():
            pylon = self.units(PYLON).ready.random
            await self.build(CYBERNETICSCORE, near=pylon.position.towards(self.game_info.map_center, 8))

    async def build_twilight_council(self):
        if await self.can_build_twilight_council():
            pylon = self.units(PYLON).ready.random
            await self.build(TWILIGHTCOUNCIL, near=pylon.position.towards(self.game_info.map_center, 8))

    async def build_stargate(self):
        if await self.can_build_stargate():
            pylon = self.units(PYLON).ready.random
            await self.build(STARGATE, near=pylon.position.towards(self.game_info.map_center, 8))

    async def build_robotics_facility(self):
        if await self.can_build_robotics_facility():
            pylon = self.units(PYLON).ready.random
            await self.build(ROBOTICSFACILITY, near=pylon.position.towards(self.game_info.map_center, 8))

    async def build_robotics_bay(self):
        if await self.can_build_robotics_bay():
            pylon = self.units(PYLON).ready.random
            await self.build(ROBOTICSBAY, near=pylon.position.towards(self.game_info.map_center, 8))

    async def build_fleet_beacon(self):
        if await self.can_build_fleet_beacon():
            if self.can_afford(FLEETBEACON):
                pylon = self.units(PYLON).ready.random
                await self.build(FLEETBEACON, near=pylon.position.towards(self.game_info.map_center, 8))

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
                if await self.can_train_zealot():
                    await self.do(gateway.train(ZEALOT))
        else:
            for warpgate in self.units(WARPGATE).ready:
                if await self.can_train_zealot():
                    await self.warp_new_units(warpgate,
                                              self.closest_pylon_to_reposition_location(),
                                              unit=ZEALOT,
                                              warpId=AbilityId.WARPGATETRAIN_ZEALOT)

    async def build_stalkers(self):
        if len(self.units(WARPGATE).ready) < 1:
            for gateway in self.units(GATEWAY).ready.noqueue:
                await self.morph_warpgate(gateway)
                if await self.can_train_stalker():
                    await self.do(gateway.train(STALKER))
        else:
            for warpgate in self.units(WARPGATE).ready:
                if await self.can_train_stalker():
                    await self.warp_new_units(warpgate,
                                              self.closest_pylon_to_reposition_location(),
                                              unit=STALKER,
                                              warpId=AbilityId.WARPGATETRAIN_STALKER)

    async def build_sentries(self):
        if len(self.units(WARPGATE).ready) < 1:
            for gateway in self.units(GATEWAY).ready.noqueue:
                await self.morph_warpgate(gateway)
                if await self.can_train_sentry():
                    await self.do(gateway.train(SENTRY))
        else:
            warpgate = self.units(WARPGATE).ready.random
            if await self.can_train_sentry():
                await self.warp_new_units(warpgate,
                                          self.closest_pylon_to_reposition_location(),
                                          unit=SENTRY,
                                          warpId=AbilityId.WARPGATETRAIN_SENTRY)

    async def build_adepts(self):
        if len(self.units(WARPGATE).ready) < 1:
            for gateway in self.units(GATEWAY).ready.noqueue:
                await self.morph_warpgate(gateway)
                if await self.can_train_adepts():
                    await self.do(gateway.train(ADEPT))
        else:
            for warpgate in self.units(WARPGATE).ready:
                if await self.can_train_adepts():
                    await self.warp_new_units(warpgate,
                                              self.closest_pylon_to_reposition_location(),
                                              unit=ADEPT,
                                              warpId=AbilityId.TRAINWARP_ADEPT)

    async def build_observers(self):
        for robo in self.units(ROBOTICSFACILITY).ready.noqueue:
            if await self.can_train_observers():
                await self.do(robo.train(OBSERVER))

    async def build_immortals(self):
        for robo in self.units(ROBOTICSFACILITY).ready.noqueue:
            if await self.can_train_immortal():
                await self.do(robo.train(IMMORTAL))

    async def build_colossus(self):
        if self.units(ROBOTICSBAY).ready.amount > 0:
            for robo in self.units(ROBOTICSFACILITY).ready.noqueue:
                if await self.can_train_colossus():
                    await self.do(robo.train(COLOSSUS))

    async def build_voidrays(self):
        if self.units(STARGATE).ready.amount > 0:
            for sg in self.units(STARGATE).ready.noqueue:
                if await self.can_train_voidrays():
                    await self.do(sg.train(VOIDRAY))

    async def build_carriers(self):
        if self.units(STARGATE).ready.amount > 0 and self.units(FLEETBEACON).ready.amount > 0:
            for sg in self.units(STARGATE).ready.noqueue:
                if await self.can_train_carriers():
                    await self.do(sg.train(CARRIER))
                    await self.use_chronoboost(sg)

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

    async def upgrade_resonating_glaives(self):
        if self.units(TWILIGHTCOUNCIL).ready.amount > 0:
            if self.can_afford(RESEARCH_ADEPTRESONATINGGLAIVES) and not self.research_resonating_glaives:
                tcouncil = self.units(TWILIGHTCOUNCIL).ready.first
                if tcouncil.noqueue:
                    await self.do(tcouncil(RESEARCH_ADEPTRESONATINGGLAIVES))
                    await self.use_chronoboost(tcouncil)
                    self.research_resonating_glaives = True

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

    async def upgrade_graviton_catapult(self):
        if self.units(FLEETBEACON).ready.amount > 0:
            if self.can_afford(RESEARCH_INTERCEPTORGRAVITONCATAPULT) and not self.research_graviton_catapult:
                fleetbeacon = self.units(FLEETBEACON).ready.first
                if fleetbeacon.noqueue:
                    await self.do(fleetbeacon(RESEARCH_INTERCEPTORGRAVITONCATAPULT))
                    await self.use_chronoboost(fleetbeacon)
                    self.research_graviton_catapult = True

    async def upgrade_ground_weapons(self):
        if not self.PROTOSSGROUNDWEAPONSLEVEL3:
            if self.units(NEXUS).ready.amount > 2:
                forge = self.units(FORGE).ready.random
                if not self.PROTOSSGROUNDWEAPONSLEVEL1 and forge.noqueue:
                    if self.can_afford(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1):
                        await self.do(forge(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1))
                        await self.use_chronoboost(forge)
                        self.PROTOSSGROUNDWEAPONSLEVEL1 = True
                if not self.PROTOSSGROUNDWEAPONSLEVEL2 and \
                        self.PROTOSSGROUNDWEAPONSLEVEL1 and \
                        forge.noqueue and \
                        self.units(TWILIGHTCOUNCIL).ready.amount > 0:
                    if self.can_afford(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2):
                        await self.do(forge(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2))
                        await self.use_chronoboost(forge)
                        self.PROTOSSGROUNDWEAPONSLEVEL2 = True
                if not self.PROTOSSGROUNDWEAPONSLEVEL3 and \
                        self.PROTOSSGROUNDWEAPONSLEVEL2 and \
                        forge.noqueue and \
                        self.units(TWILIGHTCOUNCIL).ready.amount > 0:
                    if self.can_afford(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3):
                        await self.do(forge(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3))
                        await self.use_chronoboost(forge)
                        self.PROTOSSGROUNDWEAPONSLEVEL3 = True

    async def upgrade_ground_armor(self):
        if not self.PROTOSSGROUNDARMORLEVEL3:
            if self.units(NEXUS).ready.amount > 2:
                forge = self.units(FORGE).ready.random
                if not self.PROTOSSGROUNDARMORLEVEL1 and forge.noqueue:
                    if self.can_afford(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1):
                        await self.do(forge(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1))
                        await self.use_chronoboost(forge)
                        self.PROTOSSGROUNDARMORLEVEL1 = True
                if not self.PROTOSSGROUNDARMORLEVEL2 and \
                        self.PROTOSSGROUNDARMORLEVEL1 and \
                        forge.noqueue and \
                        self.units(TWILIGHTCOUNCIL).ready.amount > 0:
                    if self.can_afford(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2):
                        await self.do(forge(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2))
                        await self.use_chronoboost(forge)
                        self.PROTOSSGROUNDARMORLEVEL2 = True
                if not self.PROTOSSGROUNDARMORLEVEL3 and \
                        self.PROTOSSGROUNDARMORLEVEL2 and \
                        forge.noqueue and \
                        self.units(TWILIGHTCOUNCIL).ready.amount > 0:
                    if self.can_afford(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3):
                        await self.do(forge(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3))
                        await self.use_chronoboost(forge)
                        self.PROTOSSGROUNDARMORLEVEL3 = True

    async def upgrade_air_weapons(self):
        if not self.PROTOSSAIRWEAPONSLEVEL3:
            if self.sky_protoss_switch:
                cc = self.units(CYBERNETICSCORE).ready.random
                if not self.PROTOSSAIRWEAPONSLEVEL1 and cc.noqueue:
                    if self.can_afford(CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL1):
                        await self.do(cc(CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL1))
                        await self.use_chronoboost(cc)
                        self.PROTOSSAIRWEAPONSLEVEL1 = True
                if not self.PROTOSSAIRWEAPONSLEVEL2 and \
                        self.PROTOSSAIRWEAPONSLEVEL1 and \
                        cc.noqueue and \
                        self.units(FLEETBEACON).ready.amount > 0:
                    if self.can_afford(CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL2):
                        await self.do(cc(CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL2))
                        await self.use_chronoboost(cc)
                        self.PROTOSSAIRWEAPONSLEVEL2 = True
                if not self.PROTOSSAIRWEAPONSLEVEL3 and \
                        self.PROTOSSAIRWEAPONSLEVEL2 and \
                        cc.noqueue and \
                        self.units(FLEETBEACON).ready.amount > 0:
                    if self.can_afford(CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL3):
                        await self.do(cc(CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL3))
                        await self.use_chronoboost(cc)
                        self.PROTOSSAIRWEAPONSLEVEL3 = True

    async def upgrade_air_armor(self):
        if not self.PROTOSSAIRARMORLEVEL3:
            if self.sky_protoss_switch:
                cc = self.units(CYBERNETICSCORE).ready.random
                if not self.PROTOSSAIRARMORLEVEL1 and cc.noqueue:
                    if self.can_afford(CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL1):
                        await self.do(cc(CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL1))
                        await self.use_chronoboost(cc)
                        self.PROTOSSAIRARMORLEVEL1 = True
                if not self.PROTOSSAIRARMORLEVEL2 and \
                        self.PROTOSSAIRARMORLEVEL1 and \
                        cc.noqueue and \
                        self.units(FLEETBEACON).ready.amount > 0:
                    if self.can_afford(CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL2):
                        await self.do(cc(CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL2))
                        await self.use_chronoboost(cc)
                        self.PROTOSSAIRARMORLEVEL2 = True
                if not self.PROTOSSAIRARMORLEVEL3 and \
                        self.PROTOSSAIRARMORLEVEL2 and \
                        cc.noqueue and \
                        self.units(FLEETBEACON).ready.amount > 0:
                    if self.can_afford(CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL3):
                        await self.do(cc(CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL3))
                        await self.use_chronoboost(cc)
                        self.PROTOSSAIRARMORLEVEL3 = True

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

    def regroup_location(self):
        return self.game_info.map_center.towards(self.enemy_start_locations[0], 120 / self.units(NEXUS).amount)

    def total_army_value(self, units):
        # TODO: This logic could be improved for better performance. 7/11/2018
        total = 0
        for unit in units:
            total += unit._type_data.cost.minerals + (unit._type_data.cost.vespene * 1.20)
        return total

    def find_target(self, targets=None):
        if targets and targets.amount > 0:
            return random.choice(targets)
        else:
            if len(self.known_enemy_units.not_structure) > 0:
                return random.choice(self.known_enemy_units.not_structure)
            if len(self.known_enemy_units.structure) > 0:
                return random.choice(self.known_enemy_units.structure).position
            else:
                return self.enemy_start_locations[0]

    def should_we_retreat(self):
        return len(self.enemy_threats) > 5 and \
               self.total_army_value(self.enemy_threats) > self.total_army_value(self.ready_attacking_units)

    async def attack(self):
        if self.should_we_retreat():
            if self.attacking:
                if self.debug:
                    await self.chat_send("Attacking Flag Off!")
                self.attacking = False
            await self.retreat()
            return
        if 200 - self.supply_used <= 10 or self.attacking:
            if not self.attacking:
                if self.debug:
                    await self.chat_send("Looks like we are Attacking!")
                self.retreating = False
                self.defending = False
                self.attacking = True
            for s in self.ready_idle_attacking_units:
                await self.do(s.attack(self.find_target()))

    async def defend(self):
        if not self.attacking:
            if self.should_we_retreat():
                await self.retreat()
                return
            if self.ready_attacking_units.amount > 1:
                if self.near_by_enemy_threats.amount > 0:
                    if not self.defending:
                        if self.debug:
                            await self.chat_send("Looks like we are Defending!")
                        self.defending = True
                    for s in self.ready_attacking_units:
                        await self.do(s.attack(self.find_target(targets=self.near_by_enemy_threats)))
                else:
                    if self.defending:
                        self.defending = False
                        if self.debug:
                            await self.chat_send("Defending Flag Off")

    async def reposition(self):
        if not self.attacking and not self.defending:
            group = self.ready_idle_attacking_units.filter(lambda unit: unit.distance_to(self.reposition_location()) > 10)
            if group.amount > 0:
                if not self.repositioning:
                    if self.debug:
                        await self.chat_send("Repositioning Army!")
                    self.repositioning = True
                for s in group:
                    if s.distance_to(self.reposition_location()) > 10:
                        await self.do(s.attack(self.reposition_location()))
        else:
            self.repositioning = False

    async def retreat(self):
        if not self.retreating:
            if self.debug:
                await self.chat_send("Retreating Army!")
            self.retreating = True
        group = self.attacking_units.filter(lambda unit: unit.distance_to(self.reposition_location()) > 40)
        for s in group:
            await self.do(s.move(self.reposition_location()))

    async def regroup(self, units, location):
        # TODO: This Method is not yet implemented. Waiting on better logic for finding a regroup location - 7/13/2018
        group = units.filter(lambda unit: unit.distance_to(location) > 5)
        for s in group:
            await self.do(s.move(location))

    async def expansion_commander(self):
        # TODO: Incorporate Expansion Priority Here - 7/13/2018
        await self.expand()
        await self.build_pylon()
        if self.units(ASSIMILATOR).amount < self.soft_max_assimilators():
            await self.build_assimilator()
        await self.build_worker()

    async def worker_commander(self):
        # TODO: Incorporate Worker Recruitment Here - 7/13/2018
        pass

    async def building_commander(self):
        # TODO: Incorporate Building Priority Here - 7/13/2018
        await self.build_fleet_beacon()
        await self.build_robotics_bay()
        await self.build_robotics_facility()
        await self.build_twilight_council()
        await self.build_stargate()
        await self.build_forge()
        await self.build_cybernetics_core()
        await self.build_gateway()

    async def recruit_commander(self):
        # TODO: Incorporate Unit Recruitment Here - 7/13/2018
        await self.build_observers()
        await self.build_carriers()
        await self.build_colossus()
        await self.build_immortals()
        await self.build_voidrays()
        if not self.sky_protoss_switch:
            await self.build_stalkers()
            await self.build_adepts()
            await self.build_sentries()
            await self.build_zealots()

    async def upgrade_commander(self):
        # TODO: Incorporate Upgrade Tactic into Here - 7/13/2018
        # TODO: It's possible for upgrade flags to be turned to True even if the upgrade hasn't triggered. - 7/13/2018
        await self.upgrade_graviton_catapult()
        await self.upgrade_thermal_lance()
        await self.upgrade_zealot_charge()
        await self.upgrade_gravitic_boosters()
        await self.upgrade_resonating_glaives()
        # await self.upgrade_stalker_blink() # Right now I don't have any Blink Logic - its useless
        if not self.sky_protoss_switch:
            await self.upgrade_ground_weapons()
            await self.upgrade_ground_armor()
        else:
            await self.upgrade_air_weapons()
            await self.upgrade_air_armor()

    async def army_commander(self):
        # TODO: Incorporate Troop Tactic into Here - 7/13/2018
        await self.defend()
        await self.attack()
        await self.reposition()

    def __repr__(self):
        return f'{self.name} - {self.version} - {self.last_build_date}'


if __name__ == '__main__':

    Races = [Race.Protoss, Race.Terran, Race.Zerg]
    Difficulties = [Difficulty.Hard, Difficulty.Harder, Difficulty.VeryHard]
    Maps = ["BlackpinkLE"]

    run_game(maps.get(random.choice(Maps)), [
        Bot(race=Race.Protoss, ai=HatchiBot()),
        Computer(race=random.choice(Races),
                 difficulty=random.choice(Difficulties))
    ], realtime=True)
