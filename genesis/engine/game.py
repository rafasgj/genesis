# -*- coding: utf-8 -*-

# This file is part of the Genesis project.
#
# Copyright (C) 2020 Rafael Guterres Jeffman
#
# Genesis is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more detail, frame=Nos.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <ht | pygame.HWSURFACEicenses/>.

"""Game engine internals."""

import sys
import logging
import importlib
from collections import defaultdict

import pygame  # pylint: disable=import-error

from genesis.errors import ClassNotFoundError
from genesis.behavior.basic import Drawable
from genesis.engine.screen import Screen
from genesis.engine.interpreter import GenesisIntepreter
from genesis.engine.events import EventPublisher, GameEvent


logger = logging.getLogger("genesis_gds")


class GameScript:
    # pylint: disable=too-few-public-methods
    """Game Script management."""

    def __init__(self, script):
        """Initialize script object."""
        # TODO: validate script parameters.
        self.__script = script

    def get(self, key, default=None):
        """Retrieve a value from the script."""
        keys = key.split(".")
        key = keys[-1]
        data = self.__script
        for k in keys[:-1]:
            if k not in data:
                return default
            data = data[k]
        return data.get(key, default)


class Game:
    """Class game."""

    def __init__(self, script, **options):
        """Initialize object."""
        logger.debug(
            msg="Game options:\n\t{}".format(
                "\n\t".join(
                    ["- {}: {}".format(k, v) for k, v in options.items()]
                )
            )
        )
        self.__script = GameScript(script)
        self.__clock = pygame.time.Clock()
        self.__fps = options.get("fps", 30)
        self.__game_classes = {}
        self.__levels = []
        self.event_handlers = defaultdict(dict)
        self.screen = self.__create_screen()
        self.game_objects = [self.screen, self]
        self.__name = "game"
        self.interpreter = GenesisIntepreter(self)

    def __create_screen(self,):
        default = {"width": 720, "height": 480}
        screen_info = self.__script.get("interface.screen", default)
        return Screen(**screen_info)

    @property
    def current_game(self):
        """Retrieve game name."""
        return self.__script.get("game_info.name") or "game"

    @property
    def name(self):
        """Retrieve game name."""
        return self.__name

    def game_info(self):
        """Retrieve game information."""
        prefix_for_fields = {
            "name": "",
            "author": "By",
            "copyright": "Copyright",
            "license": "Released under",
            "description": "",
        }
        result = []
        info = self.__script.get("game_info", None)
        if info:
            for field, prefix in prefix_for_fields.items():
                value = info.get(field, None)
                if value:
                    if prefix:
                        result.append(" ".join([prefix, value]))
                    else:
                        result.append(value)
        return result

    def game_over(self):  # pylint: disable=no-self-use
        """Finishes the current game."""
        # FIXME: It should end the current game, not the application.
        sys.exit(0)

    def run(self):
        """Run the game."""
        self.__load_object_classes()
        self.__levels = []
        for level in self.__script.get("game.levels"):
            for name, description in level.items():
                self.__levels.append(Level(name, self, description))
        for level in self.__levels:
            level.setup()
            level.start()
            while level.running:
                self.__process_pygame_events()
                self.__update_data()
                self.__draw_objects(self.screen)
                self.__clock.tick(self.__fps)
            # TODO:
            # else: player finished level
            # otherwise, player lost game.
        # TODO:
        # else: player won the game.
        # otherwise, player lost the game.

    @staticmethod
    def __parse_behaviors(object_behaviors):
        """Parse object_behaviors used by __looad_object_classes()."""
        classes = []
        events = {}
        parameters = {}
        for behavior in object_behaviors:
            classname = next(iter(behavior))
            classes.append(Game.__load_class("%s" % classname))
            for attributes in [attr or {} for attr in behavior.values()]:
                if attributes and "events" in attributes:
                    for event_description in attributes["events"]:
                        events.update(event_description)
                    del attributes["events"]
                parameters.update(attributes)

        return (classes, events, parameters)

    def __load_object_classes(self):
        """Create game objects."""
        # TODO: document this method.
        for object_item in self.__script.get("game.objects"):
            global_events = {}
            name = next(iter(object_item))
            behaviors = object_item[name]["behaviors"]
            if "GameObject" not in behaviors:
                behaviors.insert(
                    0,
                    {
                        "genesis.objects.GameObject": {
                            "name": name,
                            "game": self,
                        }
                    },
                )
            classes, events, parameters = Game.__parse_behaviors(behaviors)
            global_events[name] = events
            self.__game_classes[name] = (tuple(classes), parameters)
            for events in global_events.values():
                for event_name, actions in events.items():
                    self.add_event(name, event_name, actions)

    def add_event(self, object_name, name, actions):
        """Add an event to the game event set."""
        self.event_handlers[object_name].update({name: actions})

    def notify(self, event):
        """Receive object notification."""
        if event.sender.name in self.event_handlers:
            emitters = self.event_handlers[event.sender.name]
            if event.name in emitters:
                # NOTE: this could be in another thread!
                for action in emitters[event.name]:
                    self.execute_action(event.sender, action.copy(), event)

    def tick(self):
        """Ensure game loop executes, at most, the configured times per sec."""
        self.__clock.tick(self.__fps)

    def execute_action(self, caller, action, event):
        """Execute action code."""
        logger.debug(msg="ACTION: {}".format(action))
        execute = True
        statements = action["do"]
        if isinstance(statements, str):
            statements = [statements]
        del action["do"]
        extra_args = event.as_dict()
        if "when" in action:
            logger.debug(msg="Evaluating `when`: {}".format(action["when"]))
            execute = self.interpreter.evaluate_expression(
                action["when"], **extra_args
            )
            del action["when"]
        if execute:
            self.execute_statements(caller, statements, **extra_args)

    def execute_statements(self, caller, statements, **scope):
        """Execute the list of statements."""
        scope["caller"] = caller
        calls = None
        for statement in statements:
            logger.debug(msg="Executing statement: {}".format(statement))
            if isinstance(statement, dict):
                if len(statement) != 1:
                    raise Exception("Multiple event action: " % statement)
                statement, calls = next(iter(statement.items()))
            if calls:
                if not isinstance(calls, list):
                    calls = [calls]
                for call in calls:
                    call.update(**scope)
                    self.interpreter.execute(statement, **call)
            else:
                self.interpreter.execute(statement, **scope)

    def get_object_value(self, name):
        """Return a `value` for an item."""
        obj, *parts = name.split(".")
        for value in self.game_objects:
            if value.name == obj:
                for part in parts:
                    if hasattr(value, part):
                        value = getattr(value, part)
                    else:
                        raise Exception("Invalid member name: `%s`" % name)
                return value
        raise Exception("Invalid object: `%s`" % name)

    def get_object(self, name):
        """Return a `value` for an item."""
        obj, *_ = name.split(".")
        for value in self.game_objects:
            if value.name == obj:
                return value
        raise Exception("Invalid object: `%s`" % name)

    def __process_pygame_events(self):  # pylint: disable=no-self-use
        """Process game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(1)
            else:
                pass

    def __update_data(self):
        """Update data for game objects."""
        for gameobj in self.game_objects:
            if hasattr(gameobj, "update"):
                gameobj.update()

    def __draw_objects(self, screen):
        """Draw game objects."""
        screen.clear()
        for gameobj in self.game_objects:
            if isinstance(gameobj, Drawable):
                gameobj.draw(screen)
        screen.update()

    def spawn(self, object_name, **parameters):
        """Spawn a new object."""
        # TODO: document this method.
        def constructor(self, **options):
            for superclass in classes:
                superclass.__init__(self, **options)

        if object_name not in self.__game_classes:
            raise Exception("Cannot find object `%s` to spawn." % object_name)

        classes, default_parameters = self.__game_classes[object_name]
        start_values = default_parameters.copy()
        start_values.update(parameters)
        object_to_spawn = type(object_name, classes, {"__init__": constructor})
        start_values.update({"name": object_name, "game": self})
        obj = object_to_spawn(**start_values)
        self.game_objects.append(obj)
        object_handlers = self.event_handlers.get(object_name, {})
        for event in object_handlers.keys():
            obj.subscribe(event, self)

    @staticmethod
    def __load_class(classname):
        """Load a class represented by the classname string."""
        # TODO: find a location for this, and document it.
        try:
            if "." not in classname:
                classname = "genesis.behavior.%s" % classname
            parts = classname.split(".")
            module_name = ".".join(parts[:-1])
            module = importlib.import_module(module_name)
            return getattr(module, parts[-1])
        except Exception:
            raise ClassNotFoundError(classname)


class Level(EventPublisher):
    """A level in a game."""

    def __init__(self, name, game, events):
        """Initialize the level object."""
        EventPublisher.__init__(self)
        self.__name = name
        self.__running = True
        self.game = game
        for event in events:
            for event_name, actions in event.items():
                self.game.add_event(name, event_name, actions)
                self.subscribe(event_name, self.game)

    @property
    def name(self):
        """Retrieve game name."""
        return self.__name or "level"

    def setup(self):
        """Configure level."""

    def start(self):
        """Start level."""
        sender = self.sender_instance(name=self.name)
        self.emit(GameEvent(sender, name="start"))

    def finish(self):
        """Finish level."""
        self.__running = False

    @property
    def running(self):
        """Ask if the level is still executing."""
        return self.__running
