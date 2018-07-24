# coding: utf-8
#
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

"""Tests for One-off jobs relating to suggestions."""

from core.domain import suggestion_jobs_one_off
from core.platform import models
from core.tests import test_utils

(suggestion_models, user_models) = models.Registry.import_models([
    models.NAMES.suggestion, models.NAMES.user])
taskqueue_services = models.Registry.import_taskqueue_services()


class PopulateUserContributionsScoringModelOneOffJobTest(
        test_utils.GenericTestBase):
    """Tests for the one-off job to populate scores of users."""

    def _run_one_off_job(self):
        """Runs the one-off MapReduce job."""
        job_id = (
            suggestion_jobs_one_off.PopulateUserContributionsScoringModel
            .create_new())
        suggestion_jobs_one_off.PopulateUserContributionsScoringModel.enqueue(
            job_id)
        self.assertEqual(
            self.count_jobs_in_taskqueue(
                taskqueue_services.QUEUE_NAME_ONE_OFF_JOBS), 1)
        self.process_and_flush_pending_tasks()

    def test_migration_function(self):
        suggestion_models.GeneralSuggestionModel.create(
            suggestion_models.SUGGESTION_TYPE_EDIT_STATE_CONTENT,
            suggestion_models.TARGET_TYPE_EXPLORATION,
            'exp1', 1, suggestion_models.STATUS_IN_REVIEW, 'author_1',
            'reviewer_1', {}, 'content.Algebra', 'exploration.exp1.thread_1')
        suggestion_models.GeneralSuggestionModel.create(
            suggestion_models.SUGGESTION_TYPE_EDIT_STATE_CONTENT,
            suggestion_models.TARGET_TYPE_EXPLORATION,
            'exp1', 1, suggestion_models.STATUS_ACCEPTED, 'author_1',
            'reviewer_1', {}, 'content.Algebra', 'exploration.exp1.thread_2')
        suggestion_models.GeneralSuggestionModel.create(
            suggestion_models.SUGGESTION_TYPE_EDIT_STATE_CONTENT,
            suggestion_models.TARGET_TYPE_EXPLORATION,
            'exp1', 1, suggestion_models.STATUS_ACCEPTED, 'author_1',
            'reviewer_1', {}, 'content.Algorithms', 'exploration.exp1.thread_3')
        suggestion_models.GeneralSuggestionModel.create(
            suggestion_models.SUGGESTION_TYPE_EDIT_STATE_CONTENT,
            suggestion_models.TARGET_TYPE_EXPLORATION,
            'exp1', 1, suggestion_models.STATUS_ACCEPTED, 'author_2',
            'reviewer_1', {}, 'content.Algebra', 'exploration.exp1.thread_4')
        suggestion_models.GeneralSuggestionModel.create(
            suggestion_models.SUGGESTION_TYPE_EDIT_STATE_CONTENT,
            suggestion_models.TARGET_TYPE_EXPLORATION,
            'exp1', 1, suggestion_models.STATUS_ACCEPTED, 'author_2',
            'reviewer_1', {}, 'content.Algebra', 'exploration.exp1.thread_5')
        suggestion_models.GeneralSuggestionModel.create(
            suggestion_models.SUGGESTION_TYPE_EDIT_STATE_CONTENT,
            suggestion_models.TARGET_TYPE_EXPLORATION,
            'exp1', 1, suggestion_models.STATUS_ACCEPTED, 'author_2',
            'reviewer_1', {}, 'content.Algorithms', 'exploration.exp1.thread_6')
        suggestion_models.GeneralSuggestionModel.create(
            suggestion_models.SUGGESTION_TYPE_EDIT_STATE_CONTENT,
            suggestion_models.TARGET_TYPE_EXPLORATION,
            'exp1', 1, suggestion_models.STATUS_ACCEPTED, 'author_2',
            'reviewer_1', {}, 'content.Algebra', 'exploration.exp1.thread_7')

        self._run_one_off_job()
        self.assertEqual(
            user_models.UserContributionScoringModel
            .get_score_of_user_for_category('author_1', 'content.Algebra'), 1)
        self.assertEqual(
            user_models.UserContributionScoringModel
            .get_score_of_user_for_category('author_1', 'content.Algorithms'),
            1)
        self.assertEqual(
            user_models.UserContributionScoringModel
            .get_score_of_user_for_category('author_2', 'content.Algebra'), 3)
        self.assertEqual(
            user_models.UserContributionScoringModel
            .get_score_of_user_for_category('author_2', 'content.Algorithms'),
            1)
