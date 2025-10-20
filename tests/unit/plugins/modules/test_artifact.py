#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../plugins/modules'))

from artifact import run_module


class TestArtifactModule(unittest.TestCase):
    """Test cases for the artifact module."""

    @patch('artifact.AnsibleModule')
    @patch('artifact.run_cli_command')
    def test_list_artifacts(self, mock_cli, mock_module):
        """Test listing artifacts."""
        # Mock module and its parameters
        module_instance = MagicMock()
        mock_module.return_value = module_instance
        module_instance.params = {
            'state': 'list',
            'job_id': None,
            'id': None,
            'file_path': None,
            'fields': None
        }
        module_instance.check_mode = False
        module_instance._verbosity = 0
        
        # Mock CLI output
        mock_artifacts = [
            {"id": 1, "job_id": 123, "filename": "output1.txt"},
            {"id": 2, "job_id": 124, "filename": "output2.txt"}
        ]
        mock_cli.return_value = json.dumps(mock_artifacts)
        
        # Run the module
        run_module()
        
        # Verify CLI was called correctly
        mock_cli.assert_called_once()
        args = mock_cli.call_args[0][0]
        self.assertIn('multiflexi-cli', args)
        self.assertIn('artifact', args)
        self.assertIn('list', args)
        self.assertIn('--format', args)
        self.assertIn('json', args)
        
        # Verify module exit
        module_instance.exit_json.assert_called_once()
        exit_args = module_instance.exit_json.call_args[1]
        self.assertEqual(exit_args['artifact'], mock_artifacts)
        self.assertFalse(exit_args['changed'])

    @patch('artifact.AnsibleModule')
    @patch('artifact.run_cli_command')
    def test_get_artifact_by_id(self, mock_cli, mock_module):
        """Test getting a specific artifact by ID."""
        # Mock module and its parameters
        module_instance = MagicMock()
        mock_module.return_value = module_instance
        module_instance.params = {
            'state': 'get',
            'job_id': None,
            'id': 456,
            'file_path': None,
            'fields': None
        }
        module_instance.check_mode = False
        module_instance._verbosity = 0
        
        # Mock CLI output
        mock_artifact = {"id": 456, "job_id": 123, "filename": "output.txt", "content": "test content"}
        mock_cli.return_value = json.dumps(mock_artifact)
        
        # Run the module
        run_module()
        
        # Verify CLI was called correctly
        mock_cli.assert_called_once()
        args = mock_cli.call_args[0][0]
        self.assertIn('multiflexi-cli', args)
        self.assertIn('artifact', args)
        self.assertIn('get', args)
        self.assertIn('--id', args)
        self.assertIn('456', args)
        self.assertIn('--format', args)
        self.assertIn('json', args)
        
        # Verify module exit
        module_instance.exit_json.assert_called_once()
        exit_args = module_instance.exit_json.call_args[1]
        self.assertEqual(exit_args['artifact'], mock_artifact)
        self.assertFalse(exit_args['changed'])

    @patch('artifact.AnsibleModule')
    @patch('artifact.run_cli_command')
    @patch('artifact.os.path.exists')
    def test_save_artifact_check_mode(self, mock_exists, mock_cli, mock_module):
        """Test saving artifact in check mode."""
        # Mock module and its parameters
        module_instance = MagicMock()
        mock_module.return_value = module_instance
        module_instance.params = {
            'state': 'save',
            'job_id': None,
            'id': 456,
            'file_path': '/tmp/test_artifact.txt',
            'fields': None
        }
        module_instance.check_mode = True
        module_instance._verbosity = 0
        
        # Mock file doesn't exist
        mock_exists.return_value = False
        
        # Run the module
        run_module()
        
        # Verify no CLI calls were made (check mode)
        mock_cli.assert_not_called()
        
        # Verify module exit with changed=True
        module_instance.exit_json.assert_called_once()
        exit_args = module_instance.exit_json.call_args[1]
        self.assertTrue(exit_args['changed'])
        self.assertEqual(exit_args['saved_to'], '/tmp/test_artifact.txt')

    def test_get_without_id_fails(self):
        """Test that getting artifact without ID fails."""
        with patch('artifact.AnsibleModule') as mock_module:
            module_instance = MagicMock()
            mock_module.return_value = module_instance
            module_instance.params = {
                'state': 'get',
                'job_id': None,
                'id': None,
                'file_path': None,
                'fields': None
            }
            module_instance._verbosity = 0
            
            # Run the module
            run_module()
            
            # Verify failure
            module_instance.fail_json.assert_called_once()
            fail_args = module_instance.fail_json.call_args[1]
            self.assertIn('id parameter is required', fail_args['msg'])

    def test_save_without_required_params_fails(self):
        """Test that saving artifact without required parameters fails."""
        with patch('artifact.AnsibleModule') as mock_module:
            module_instance = MagicMock()
            mock_module.return_value = module_instance
            module_instance.params = {
                'state': 'save',
                'job_id': None,
                'id': None,  # Missing ID
                'file_path': '/tmp/test.txt',
                'fields': None
            }
            module_instance._verbosity = 0
            
            # Run the module
            run_module()
            
            # Verify failure
            module_instance.fail_json.assert_called_once()
            fail_args = module_instance.fail_json.call_args[1]
            self.assertIn('id parameter is required', fail_args['msg'])


if __name__ == '__main__':
    unittest.main()