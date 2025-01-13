# test_config_persona.py
import unittest
from tests.base_test_case import BaseTestCase

class TestLoadPersona(BaseTestCase):

    def test_personas_disabled_returns_none(self):
        self.config.data['settings']['system']['persona']['enabled'] = False

        agent_data = {}  # no explicit Persona key
        persona = self.config.load_persona(agent_data)
        self.assertIsNone(persona, "Expected None when persona is disabled.")

    def test_missing_persona_raises_file_not_found(self):
        # Make sure persona is enabled
        self.config.data['settings']['system']['persona']['enabled'] = True
        self.config.data['personas'] = {}  # or ensure the requested persona doesn't exist

        with self.assertRaises(FileNotFoundError):
            self.config.load_persona({'Persona': 'NonExistentPersona'})

    def test_load_default_persona(self):
        # Enable persona
        self.config.data['settings']['system']['persona']['enabled'] = True
        # Suppose it's named 'default'
        self.config.data['settings']['system']['persona']['name'] = 'default'

        # Make sure there's an actual 'default' persona in the data
        self.config.data['personas'] = {
            'default': {"some_key": "some_value"}
        }

        persona = self.config.load_persona({})
        self.assertIsNotNone(persona)
        self.assertEqual(persona.get('some_key'), "some_value")

    def test_load_explicit_persona(self):
        self.config.data['settings']['system']['persona']['enabled'] = True

        persona = self.config.load_persona(self.config.data)
        self.assertEqual(persona.get('Name'), "Persona Name")

if __name__ == '__main__':
    unittest.main()