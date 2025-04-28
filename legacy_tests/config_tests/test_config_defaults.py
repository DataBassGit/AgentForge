# test_config_defaults.py

import unittest
from tests.base_test_case import BaseTestCase  # Adjust as needed for your framework

class TestConfigDefaults(BaseTestCase):

    # ---------------------------------
    # Prep.
    # ---------------------------------

    def setUp(self):
        super().setUp()
        self.system_data = self.config.data['settings']['system']
        self.models_data = self.config.data['settings']['models']
        self.storage_data = self.config.data['settings']['storage']

    def tearDown(self):
        super().tearDown()
        self.system_data = None

    # ---------------------------------
    # Test System Defaults.
    # ---------------------------------

    def test_default_persona_settings(self):
        # Persona settings
        persona_data = self.system_data.get('persona', {})
        self.assertTrue(persona_data.get('enabled', False))
        self.assertEqual(persona_data.get('name'), 'default')

    def test_default_debug_settings(self):
        # Debug settings
        debug_data = self.system_data.get('debug', {})
        self.assertFalse(debug_data.get('mode', True))
        self.assertFalse(debug_data.get('save_memory', True))
        self.assertEqual(
            debug_data.get('simulated_response'),
            "Text designed to simulate an LLM response for debugging purposes without invoking the model."
        )

    def test_default_logging_settings(self):
        # Logging settings
        logging_data = self.system_data.get('logging', {})
        self.assertTrue(logging_data.get('enabled', False))
        self.assertEqual(logging_data.get('folder'), './logs')

        log_files = logging_data.get('files', {})
        self.assertEqual(log_files.get('agentforge'), 'error')
        self.assertEqual(log_files.get('model_io'), 'error')

    def test_default_misc_settings(self):
        # Misc settings
        misc_data = self.system_data.get('misc', {})
        self.assertTrue(misc_data.get('on_the_fly', False))

    def test_default_path_settings(self):
        # Paths
        paths_data = self.system_data.get('paths', {})
        self.assertEqual(paths_data.get('files'), './files')

    # ---------------------------------
    # Test Model Defaults.
    # ---------------------------------

    def test_default_model_settings(self):
        # Default model settings
        default_model = self.models_data.get('default_model', {})
        self.assertEqual(default_model.get('api'), 'gemini_api')
        self.assertEqual(default_model.get('model'), 'gemini_flash')

    def test_default_model_library_settings(self):
        # Model library validations
        model_library = self.models_data.get('model_library', {})
        self.assertIn('openai_api', model_library)
        self.assertIn('gemini_api', model_library)
        self.assertIn('lm_studio_api', model_library)

        gemini_api = model_library.get('gemini_api', {}).get('Gemini', {}).get('models', {})
        self.assertIn('gemini_pro', gemini_api)
        self.assertIn('gemini_flash', gemini_api)

        gemini_params = model_library.get('gemini_api', {}).get('Gemini', {}).get('params', {})
        self.assertEqual(gemini_params.get('max_output_tokens'), 10000)
        self.assertEqual(gemini_params.get('temperature'), 0.8)

    # ---------------------------------
    # Test Storage Defaults.
    # ---------------------------------

    def test_default_option_settings(self):
        # Options
        options_data = self.storage_data.get('options', {})
        self.assertTrue(options_data.get('enabled', False))
        self.assertTrue(options_data.get('save_memory', False))
        self.assertTrue(options_data.get('iso_timestamp', False))
        self.assertTrue(options_data.get('unix_timestamp', False))
        self.assertEqual(options_data.get('persist_directory'), './db/ChromaDB')
        self.assertFalse(options_data.get('fresh_start', True))

    def test_default_embedding_settings(self):
        # Embedding settings
        embedding_data = self.storage_data.get('embedding', {})
        self.assertEqual(embedding_data.get('selected'), 'distil_roberta')

    def test_default_embedding_library_settings(self):
        # Library defaults
        library_data = self.storage_data.get('embedding_library', {})
        self.assertEqual(library_data.get('distil_roberta'), 'all-distilroberta-v1')
        self.assertEqual(library_data.get('all_mini'), 'all-MiniLM-L6-v2')

if __name__ == '__main__':
    unittest.main()
