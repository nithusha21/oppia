# Copyright 2018 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for suggestion related services."""

from core.domain import exp_services
from core.domain import feedback_services
from core.domain import suggestion_services
from core.platform import models
from core.tests import test_utils

(suggestion_models, feedback_models) = models.Registry.import_models([
    models.NAMES.suggestion, models.NAMES.feedback])


class SuggestionServicesUnitTests(test_utils.GenericTestBase):
    """Test the functions in suggestion_services."""

    customization_args = {
        'contribution_type': 'translation',
        'contribution_language': 'English'
    }

    payload = {
        'entity_id': 'exp1',
        'entity_version_number': 1,
        'change_list': {}
    }


    AUTHOR_EMAIL = 'author@example.com'
    REVIEWER_EMAIL = 'reviewer@example.com'
    ASSIGNED_REVIEWER_EMAIL = 'assigned_reviewer@example.com'

    THREAD_ID = 'thread_1'

    COMMIT_MESSAGE = 'commit message'
    EMPTY_COMMIT_MESSAGE = ' '

    def setUp(self):
        super(SuggestionServicesUnitTests, self).setUp()

        self.signup(self.AUTHOR_EMAIL, 'author')
        self.author_id = self.get_user_id_from_email(self.AUTHOR_EMAIL)
        self.signup(self.REVIEWER_EMAIL, 'reviewer')
        self.reviewer_id = self.get_user_id_from_email(self.REVIEWER_EMAIL)
        self.signup(self.ASSIGNED_REVIEWER_EMAIL, 'assignedReviewer')
        self.assigned_reviewer_id = self.get_user_id_from_email(
            self.ASSIGNED_REVIEWER_EMAIL)

    def test_validate_suggestion_payload(self):
        edit_suggestion_payload = {
            'entity_id': 'sample_id',
            'entity_version_number': '1',
            'change_list': {}
        }
        add_suggestion_payload = {
            'entity_type': 'entity1',
            'entity_data': {}
        }
        self.assertTrue(suggestion_services.validate_suggestion_payload(
            suggestion_models.SUGGESTION_TYPE_ADD, add_suggestion_payload))

        self.assertTrue(suggestion_services.validate_suggestion_payload(
            suggestion_models.SUGGESTION_TYPE_EDIT, edit_suggestion_payload))

        self.assertFalse(suggestion_services.validate_suggestion_payload(
            suggestion_models.SUGGESTION_TYPE_ADD, edit_suggestion_payload))

        self.assertFalse(suggestion_services.validate_suggestion_payload(
            suggestion_models.SUGGESTION_TYPE_EDIT, add_suggestion_payload))

    def generate_thread_id(self, unused_exp_id):
        return self.THREAD_ID

    def return_true(self, unused_suggestion, unused_reviewer_id):
        return True

    def return_false(self, unused_suggestion, unused_reviewer_id):
        return False

    def test_create_new_suggestion_successfully(self):
        expected_suggestion_dict = {
            'suggestion_type': suggestion_models.SUGGESTION_TYPE_EDIT,
            'entity_type': suggestion_models.ENTITY_TYPE_EXPLORATION,
            'suggestion_sub_type': suggestion_models.SUGGESTION_EDIT_STATE_CONTENT, # pylint: disable=line-too-long
            'status': suggestion_models.STATUS_IN_REVIEW,
            'customization_args': self.customization_args,
            'author_name': 'author',
            'reviewer_name': 'reviewer',
            'thread_id': self.THREAD_ID,
            'assigned_reviewer_name': 'assignedReviewer',
            'payload': self.payload
        }
        with self.swap(
            feedback_models.FeedbackThreadModel,
            'generate_new_thread_id', self.generate_thread_id):
            suggestion_services.create_suggestion(
                suggestion_models.SUGGESTION_TYPE_EDIT,
                suggestion_models.ENTITY_TYPE_EXPLORATION,
                suggestion_models.SUGGESTION_EDIT_STATE_CONTENT,
                self.customization_args, self.author_id, self.payload,
                'test description', self.reviewer_id, self.assigned_reviewer_id)
            observed_suggestion = suggestion_services.get_suggestion(
                suggestion_models.SUGGESTION_TYPE_EDIT,
                suggestion_models.ENTITY_TYPE_EXPLORATION,
                self.THREAD_ID, self.payload['entity_id'])
            self.assertDictEqual(
                expected_suggestion_dict, observed_suggestion.to_dict())

    def check_commit_message(
            self, unused_user_id, unused_exploration_id, unused_change_list,
            commit_message, is_suggestion):
        self.assertTrue(is_suggestion)
        self.assertEqual(
            commit_message, 'Accepted suggestion by %s: %s' % (
                'author', self.COMMIT_MESSAGE))

    def test_accept_suggestion_successfully(self):
        with self.swap(
            feedback_models.FeedbackThreadModel,
            'generate_new_thread_id', self.generate_thread_id):
            suggestion_services.create_suggestion(
                suggestion_models.SUGGESTION_TYPE_EDIT,
                suggestion_models.ENTITY_TYPE_EXPLORATION,
                suggestion_models.SUGGESTION_EDIT_STATE_CONTENT,
                self.customization_args, self.author_id, self.payload,
                'test description', self.reviewer_id,
                self.assigned_reviewer_id)
        suggestion = suggestion_services.get_suggestion(
            suggestion_models.SUGGESTION_TYPE_EDIT,
            suggestion_models.ENTITY_TYPE_EXPLORATION,
            self.THREAD_ID, self.payload['entity_id'])

        with self.swap(
            suggestion_services, 'is_suggestion_valid', self.return_true):
            with self.swap(
                exp_services, 'update_exploration', self.check_commit_message):
                suggestion_services.accept_suggestion(
                    suggestion, self.reviewer_id, self.COMMIT_MESSAGE)
                suggestion = suggestion_services.get_suggestion(
                    suggestion_models.SUGGESTION_TYPE_EDIT,
                    suggestion_models.ENTITY_TYPE_EXPLORATION,
                    self.THREAD_ID, self.payload['entity_id'])
                self.assertEqual(
                    suggestion.status, suggestion_models.STATUS_ACCEPTED)
                self.assertEqual(
                    suggestion.reviewer_id, self.reviewer_id)
                thread_messages = feedback_services.get_messages(
                    self.payload['entity_id'], self.THREAD_ID)
                last_message = thread_messages[len(thread_messages) - 1]
                self.assertEqual(
                    last_message.text, 'Accepted by %s' % self.reviewer_id)

    def test_accept_suggestion_handled_suggestion_failure(self):
        with self.swap(
            feedback_models.FeedbackThreadModel,
            'generate_new_thread_id', self.generate_thread_id):
            suggestion_services.create_suggestion(
                suggestion_models.SUGGESTION_TYPE_EDIT,
                suggestion_models.ENTITY_TYPE_EXPLORATION,
                suggestion_models.SUGGESTION_EDIT_STATE_CONTENT,
                self.customization_args, self.author_id, self.payload,
                'test description', self.reviewer_id,
                self.assigned_reviewer_id)
        suggestion = suggestion_services.get_suggestion(
            suggestion_models.SUGGESTION_TYPE_EDIT,
            suggestion_models.ENTITY_TYPE_EXPLORATION,
            self.THREAD_ID, self.payload['entity_id'])

        with self.swap(
            suggestion_services, 'is_suggestion_valid', self.return_true):
            with self.swap(
                exp_services, 'update_exploration', self.check_commit_message):
                suggestion.status = suggestion_models.STATUS_ACCEPTED
                suggestion_services.update_suggestion(suggestion)
                with self.assertRaisesRegexp(
                    Exception,
                    'The suggestion has already been accepted/rejected.'):
                    suggestion_services.accept_suggestion(
                        suggestion, self.reviewer_id, self.COMMIT_MESSAGE)
                suggestion = suggestion_services.get_suggestion(
                    suggestion_models.SUGGESTION_TYPE_EDIT,
                    suggestion_models.ENTITY_TYPE_EXPLORATION,
                    self.THREAD_ID, self.payload['entity_id'])
                self.assertEqual(
                    suggestion.status, suggestion_models.STATUS_ACCEPTED)
                suggestion.status = suggestion_models.STATUS_REJECTED
                suggestion_services.update_suggestion(suggestion)

                with self.assertRaisesRegexp(
                    Exception,
                    'The suggestion has already been accepted/rejected.'):
                    suggestion_services.accept_suggestion(
                        suggestion, self.reviewer_id, self.COMMIT_MESSAGE)
                suggestion = suggestion_services.get_suggestion(
                    suggestion_models.SUGGESTION_TYPE_EDIT,
                    suggestion_models.ENTITY_TYPE_EXPLORATION,
                    self.THREAD_ID, self.payload['entity_id'])
                self.assertEqual(
                    suggestion.status, suggestion_models.STATUS_REJECTED)

    def test_accept_suggestion_invalid_suggestion_failure(self):
        with self.swap(
            feedback_models.FeedbackThreadModel,
            'generate_new_thread_id', self.generate_thread_id):
            suggestion_services.create_suggestion(
                suggestion_models.SUGGESTION_TYPE_EDIT,
                suggestion_models.ENTITY_TYPE_EXPLORATION,
                suggestion_models.SUGGESTION_EDIT_STATE_CONTENT,
                self.customization_args, self.author_id, self.payload,
                'test description', self.reviewer_id,
                self.assigned_reviewer_id)
        suggestion = suggestion_services.get_suggestion(
            suggestion_models.SUGGESTION_TYPE_EDIT,
            suggestion_models.ENTITY_TYPE_EXPLORATION,
            self.THREAD_ID, self.payload['entity_id'])

        with self.swap(
            suggestion_services, 'is_suggestion_valid', self.return_false):
            with self.swap(
                exp_services, 'update_exploration', self.check_commit_message):
                with self.assertRaisesRegexp(
                    Exception, 'The suggestion is not valid.'):
                    suggestion_services.accept_suggestion(
                        suggestion, self.reviewer_id, self.COMMIT_MESSAGE)

    def test_accept_suggestion_no_commit_message_failure(self):
        with self.swap(
            feedback_models.FeedbackThreadModel,
            'generate_new_thread_id', self.generate_thread_id):
            suggestion_services.create_suggestion(
                suggestion_models.SUGGESTION_TYPE_EDIT,
                suggestion_models.ENTITY_TYPE_EXPLORATION,
                suggestion_models.SUGGESTION_EDIT_STATE_CONTENT,
                self.customization_args, self.author_id, self.payload,
                'test description', self.reviewer_id,
                self.assigned_reviewer_id)

        suggestion = suggestion_services.get_suggestion(
            suggestion_models.SUGGESTION_TYPE_EDIT,
            suggestion_models.ENTITY_TYPE_EXPLORATION,
            self.THREAD_ID, self.payload['entity_id'])

        with self.swap(
            suggestion_services, 'is_suggestion_valid', self.return_true):
            with self.swap(
                exp_services, 'update_exploration', self.check_commit_message):
                with self.assertRaisesRegexp(
                    Exception, 'Commit message cannot be empty.'):
                    suggestion_services.accept_suggestion(
                        suggestion, self.reviewer_id, self.EMPTY_COMMIT_MESSAGE)

    def test_reject_suggestion_successfully(self):
        with self.swap(
            feedback_models.FeedbackThreadModel,
            'generate_new_thread_id', self.generate_thread_id):
            suggestion_services.create_suggestion(
                suggestion_models.SUGGESTION_TYPE_EDIT,
                suggestion_models.ENTITY_TYPE_EXPLORATION,
                suggestion_models.SUGGESTION_EDIT_STATE_CONTENT,
                self.customization_args, self.author_id, self.payload,
                'test description', self.reviewer_id,
                self.assigned_reviewer_id)
        suggestion = suggestion_services.get_suggestion(
            suggestion_models.SUGGESTION_TYPE_EDIT,
            suggestion_models.ENTITY_TYPE_EXPLORATION,
            self.THREAD_ID, self.payload['entity_id'])

        suggestion_services.reject_suggestion(
            suggestion, self.reviewer_id)
        suggestion = suggestion_services.get_suggestion(
            suggestion_models.SUGGESTION_TYPE_EDIT,
            suggestion_models.ENTITY_TYPE_EXPLORATION,
            self.THREAD_ID, self.payload['entity_id'])
        self.assertEqual(
            suggestion.status, suggestion_models.STATUS_REJECTED)
        self.assertEqual(
            suggestion.reviewer_id, self.reviewer_id)
        thread_messages = feedback_services.get_messages(
            self.payload['entity_id'], self.THREAD_ID)
        last_message = thread_messages[len(thread_messages) - 1]
        self.assertEqual(last_message.text, 'Rejected by %s' % self.reviewer_id)

    def test_reject_suggestion_handled_suggestion_failure(self):
        with self.swap(
            feedback_models.FeedbackThreadModel,
            'generate_new_thread_id', self.generate_thread_id):
            suggestion_services.create_suggestion(
                suggestion_models.SUGGESTION_TYPE_EDIT,
                suggestion_models.ENTITY_TYPE_EXPLORATION,
                suggestion_models.SUGGESTION_EDIT_STATE_CONTENT,
                self.customization_args, self.author_id, self.payload,
                'test description', self.reviewer_id,
                self.assigned_reviewer_id)
        suggestion = suggestion_services.get_suggestion(
            suggestion_models.SUGGESTION_TYPE_EDIT,
            suggestion_models.ENTITY_TYPE_EXPLORATION,
            self.THREAD_ID, self.payload['entity_id'])

        suggestion.status = suggestion_models.STATUS_ACCEPTED
        suggestion_services.update_suggestion(suggestion)
        with self.assertRaisesRegexp(
            Exception,
            'The suggestion has already been accepted/rejected.'):
            suggestion_services.reject_suggestion(
                suggestion, self.reviewer_id)

        suggestion = suggestion_services.get_suggestion(
            suggestion_models.SUGGESTION_TYPE_EDIT,
            suggestion_models.ENTITY_TYPE_EXPLORATION,
            self.THREAD_ID, self.payload['entity_id'])
        self.assertEqual(
            suggestion.status, suggestion_models.STATUS_ACCEPTED)

        suggestion.status = suggestion_models.STATUS_REJECTED
        suggestion_services.update_suggestion(suggestion)

        with self.assertRaisesRegexp(
            Exception,
            'The suggestion has already been accepted/rejected.'):
            suggestion_services.reject_suggestion(
                suggestion, self.reviewer_id)
        suggestion = suggestion_services.get_suggestion(
            suggestion_models.SUGGESTION_TYPE_EDIT,
            suggestion_models.ENTITY_TYPE_EXPLORATION,
            self.THREAD_ID, self.payload['entity_id'])
        self.assertEqual(
            suggestion.status, suggestion_models.STATUS_REJECTED)


class SuggestionValidationUnitTests(test_utils.GenericTestBase):
    """Tests the is_suggestion_valid function in suggestion_services.py

    This is an important function with a lot of conditions and needs to be
    tested thoroughly.

    The tests in this suite use the MockExploration class defined inside as
    exploration objects. Swap out the function in exp_services with a mock
    function to test the suggestion validity.
    """
    customization_args = {
        'contribution_type': 'translation',
        'contribution_language': 'English'
    }

    payload = {
        'entity_id': 'exp1',
        'entity_version_number': 1,
        'change_list': {}
    }


    AUTHOR_EMAIL = 'author@example.com'
    REVIEWER_EMAIL = 'reviewer@example.com'
    ASSIGNED_REVIEWER_EMAIL = 'assigned_reviewer@example.com'

    THREAD_ID = 'thread_1'

    def setUp(self):
        super(SuggestionValidationUnitTests, self).setUp()

        self.signup(self.AUTHOR_EMAIL, 'author')
        self.author_id = self.get_user_id_from_email(self.AUTHOR_EMAIL)
        self.signup(self.REVIEWER_EMAIL, 'reviewer')
        self.reviewer_id = self.get_user_id_from_email(self.REVIEWER_EMAIL)
        self.signup(self.ASSIGNED_REVIEWER_EMAIL, 'assignedReviewer')
        self.assigned_reviewer_id = self.get_user_id_from_email(
            self.ASSIGNED_REVIEWER_EMAIL)

    def generate_thread_id(self, unused_exp_id):
        return self.THREAD_ID

    class MockExploration(object):
        """Mocks an exploration. To be used only for testing."""
        def __init__(self, exploration_id, states):
            self.id = exploration_id
            self.states = states

    # All mock explorations created for testing.
    explorations = [
        MockExploration('exp1', ['state_1', 'state_2'])
    ]

    def mock_get_exploration_by_id(self, exp_id):
        for exp in self.explorations:
            if exp.id == exp_id:
                return exp
        return None

    def test_is_suggestion_valid_edit_state_content_success(self):

        payload = {
            'entity_id': 'exp1',
            'entity_version_number': 1,
            'change_list': {
                'state_name': 'state_1'
            }
        }

        with self.swap(
            feedback_models.FeedbackThreadModel,
            'generate_new_thread_id', self.generate_thread_id):
            suggestion_services.create_suggestion(
                suggestion_models.SUGGESTION_TYPE_EDIT,
                suggestion_models.ENTITY_TYPE_EXPLORATION,
                suggestion_models.SUGGESTION_EDIT_STATE_CONTENT,
                self.customization_args, self.author_id, payload,
                'test description', self.reviewer_id,
                self.assigned_reviewer_id)
        suggestion = suggestion_services.get_suggestion(
            suggestion_models.SUGGESTION_TYPE_EDIT,
            suggestion_models.ENTITY_TYPE_EXPLORATION,
            self.THREAD_ID, self.payload['entity_id'])
        with self.swap(
            exp_services, 'get_exploration_by_id',
            self.mock_get_exploration_by_id):
            self.assertTrue(suggestion_services.is_suggestion_valid(
                suggestion, self.reviewer_id))
            suggestion = suggestion_services.get_suggestion(
                suggestion_models.SUGGESTION_TYPE_EDIT,
                suggestion_models.ENTITY_TYPE_EXPLORATION,
                self.THREAD_ID, self.payload['entity_id'])
            self.assertEqual(
                suggestion.status, suggestion_models.STATUS_IN_REVIEW)

    def test_is_suggestion_valid_edit_state_content_failure(self):

        payload = {
            'entity_id': 'exp1',
            'entity_version_number': 1,
            'change_list': {
                'state_name': 'state_unknown'
            }
        }

        with self.swap(
            feedback_models.FeedbackThreadModel,
            'generate_new_thread_id', self.generate_thread_id):
            suggestion_services.create_suggestion(
                suggestion_models.SUGGESTION_TYPE_EDIT,
                suggestion_models.ENTITY_TYPE_EXPLORATION,
                suggestion_models.SUGGESTION_EDIT_STATE_CONTENT,
                self.customization_args, self.author_id, payload,
                'test description', self.reviewer_id,
                self.assigned_reviewer_id)
        suggestion = suggestion_services.get_suggestion(
            suggestion_models.SUGGESTION_TYPE_EDIT,
            suggestion_models.ENTITY_TYPE_EXPLORATION,
            self.THREAD_ID, self.payload['entity_id'])
        with self.swap(
            exp_services, 'get_exploration_by_id',
            self.mock_get_exploration_by_id):
            self.assertFalse(suggestion_services.is_suggestion_valid(
                suggestion, self.reviewer_id))
            suggestion = suggestion_services.get_suggestion(
                suggestion_models.SUGGESTION_TYPE_EDIT,
                suggestion_models.ENTITY_TYPE_EXPLORATION,
                self.THREAD_ID, self.payload['entity_id'])
            self.assertEqual(
                suggestion.status, suggestion_models.STATUS_INVALID)
