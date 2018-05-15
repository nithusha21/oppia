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

"""Tests for suggestion domain objects."""

from core.domain import suggestion_domain
from core.platform import models
from core.tests import test_utils

(suggestion_models,) = models.Registry.import_models([models.NAMES.suggestion])


class SuggestionDomainUnitTests(test_utils.GenericTestBase):
    """Tests for the suggestion class."""

    AUTHOR_EMAIL = 'author@example.com'
    REVIEWER_EMAIL = 'reviewer@example.com'
    ASSIGNED_REVIEWER_EMAIL = 'assigned_reviewer@example.com'

    THREAD_ID = 'thread_0'

    def setUp(self):
        super(SuggestionDomainUnitTests, self).setUp()

        self.signup(self.AUTHOR_EMAIL, 'author')
        self.author_id = self.get_user_id_from_email(self.AUTHOR_EMAIL)
        self.signup(self.REVIEWER_EMAIL, 'reviewer')
        self.reviewer_id = self.get_user_id_from_email(self.REVIEWER_EMAIL)
        self.signup(self.ASSIGNED_REVIEWER_EMAIL, 'assignedReviewer')
        self.assigned_reviewer_id = self.get_user_id_from_email(
            self.ASSIGNED_REVIEWER_EMAIL)

    def test_to_dict(self):
        expected_suggestion_dict = {
            'suggestion_type': suggestion_models.SUGGESTION_TYPE_EDIT,
            'entity_type': suggestion_models.ENTITY_TYPE_EXPLORATION,
            'suggestion_sub_type': suggestion_models.SUGGESTION_EDIT_STATE_CONTENT, # pylint: disable=line-too-long
            'status': suggestion_models.STATUS_ACCEPTED,
            'customization_args': {
                'contribution_type': 'translation',
                'contribution_language': 'English'
            },
            'author_name': 'author',
            'reviewer_name': 'reviewer',
            'thread_id': self.THREAD_ID,
            'assigned_reviewer_name': 'assignedReviewer',
            'payload': {}
        }

        observed_suggestion = suggestion_domain.Suggestion(
            expected_suggestion_dict['suggestion_type'],
            expected_suggestion_dict['entity_type'],
            expected_suggestion_dict['suggestion_sub_type'],
            expected_suggestion_dict['status'],
            expected_suggestion_dict['customization_args'], self.author_id,
            self.reviewer_id, self.THREAD_ID, self.assigned_reviewer_id,
            expected_suggestion_dict['payload'])

        self.assertDictEqual(
            observed_suggestion.to_dict(), expected_suggestion_dict)
