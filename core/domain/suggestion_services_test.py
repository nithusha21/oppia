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

"""Tests for suggestion related services"""

from core.domain import feedback_services
from core.domain import suggestion_domain
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

    THREAD_ID = 'thread_1'
    def generate_thread_id(self, unused_exp_id):
        return self.THREAD_ID

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

