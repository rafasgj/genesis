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
import pygame  # pylint: disable=import-error

from genesis.errors import ClassNotFoundError
from genesis.engine.screen import Screen
from genesis.engine.interpreter import GenesisIntepreter
from genesis.behavior.basic import Drawable


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

    def __init__(self, script):
        """Initialize object."""
        self.__script = GameScript(script)
        self.__clock = pygame.time.Clock()
        self.__fps = 30  # TODO: make this configurable.
        self.__game_classes = {}
        self.__levels = []
        self.event_handlers = {}
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

    def __load_object_classes(self):
        """Create game objects."""
        # TODO: document this method.
        for object_item in self.__script.get("game.objects"):
            global_events = {}
            name = next(iter(object_item))
            object_behaviors = object_item[name]["behaviors"]
            if "GameObject" not in object_behaviors:
                object_behaviors.insert(
                    0,
                    {
                        "genesis.objects.GameObject": {
                            "name": name,
                            "game": self,
                        }
                    },
                )
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
            global_events[name] = events
            self.__game_classes[name] = (tuple(classes), parameters)
            for events in global_events.values():
                for event, actions in events.items():
                    self.event_handlers[event] = {name: actions}

    def notify(self, event):
        """Receive object notification."""
        if event.name in self.event_handlers:
            emitters = self.event_handlers[event.name]
            if event.sender.name in emitters:
                params = {
                    "object": event.sender,
                    event.name: event,
                    "actions": emitters[event.sender.name],
                }
                # NOTE: this could be in another thread!
                self.__process_event_code(params)

    def tick(self):
        """Ensure game loop executes, at most, the configured times per sec."""
        self.__clock.tick(self.__fps)

    def __process_event_code(self, params):  # pylint: disable=no-self-use
        """Run event code."""

        def get_param(name, params):
            data = params[name]
            del params[name]
            return data

        sender = get_param("object", params)
        actions = get_param("actions", params)
        for action in actions:
            self.execute_action(sender, action.copy(), params)

    def execute_action(self, obj, action, params):
        """Execute action code."""
        logger.debug(msg="ACTION: {}".format(action))
        execute = True
        statements = action["do"]
        if isinstance(statements, str):
            statements = [statements]
        del action["do"]
        if "when" in action:
            logger.debug(msg="Evaluating `when`: {}".format(action["when"]))
            execute = self.interpreter.evaluate_expression(
                action["when"], **params
            )
            del action["when"]
        if execute:
            for statement in statements:
                logger.debug(msg="Executing statement: {}".format(statement))
                method = getattr(obj, statement)
                if action:
                    method(**action)
                else:
                    method()

    def get_object_value(self, name):
        """Return a `value` for an item."""
        obj, *parts = name.split(".")
        for value in self.game_objects:
            if value.name == obj:
                for part in parts:
                    if hasattr(value, part):
                        value = getattr(value, part)
                    else:
                        raise Exception("Cannot access value for `%s`" % name)
                return value
        raise Exception("Cannot access value for `%s`" % name)

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

        for event, handlers in self.event_handlers.items():
            actions = handlers.get(obj.name, None)
            if actions:
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


class Level:
    """A level in a game."""

    def __init__(self, name, game, description):
        """Initialize the level object."""
        self.__name = name
        self.__running = True
        self.game = game
        self.__description = description

    @property
    def name(self):
        """Retrieve game name."""
        return self.__name or "level"

    def setup(self):
        """Configure level."""

    def start(self):
        """Start level."""
        start_ops = self.__description.get("start", [])
        for operation in start_ops:
            for method, instances in operation.items():
                for scope in [self, self.game]:
                    if hasattr(scope, method):
                        for params in instances:
                            getattr(scope, method)(**params, level=self)
                        break
                else:
                    raise Exception("Operation `%s` not defined." % operation)

    def finish(self):
        """Finish level."""
        self.__running = False

    @property
    def running(self):
        """Ask if the level is still executing."""
        return self.__running
