# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
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

"""Tests for feedback-related jobs."""

import ast

from core.domain import feedback_jobs_one_off
from core.domain import feedback_services
from core.domain import subscription_services
from core.platform import models
from core.tests import test_utils

(feedback_models,) = models.Registry.import_models([models.NAMES.feedback])
taskqueue_services = models.Registry.import_taskqueue_services()


class FeedbackThreadMessagesCountOneOffJobTest(test_utils.GenericTestBase):
    """Tests for the one-off feedback thread message counter job."""

    EXP_ID_1 = 'eid1'
    EXP_ID_2 = 'eid2'

    EXPECTED_THREAD_DICT = {
        'status': u'open',
        'state_name': u'a_state_name',
        'summary': None,
        'original_author_username': None,
        'subject': u'a subject'
    }

    USER_EMAIL = 'user@example.com'
    USER_USERNAME = 'user'

    def setUp(self):
        super(FeedbackThreadMessagesCountOneOffJobTest, self).setUp()

        self.signup(self.USER_EMAIL, self.USER_USERNAME)
        self.user_id = self.get_user_id_from_email(self.USER_EMAIL)
        self.signup(self.OWNER_EMAIL, self.OWNER_USERNAME)
        self.owner_id = self.get_user_id_from_email(self.OWNER_EMAIL)

        self.save_new_valid_exploration(
            self.EXP_ID_1, self.owner_id, title='Bridges in England',
            category='Architecture', language_code='en')
        self.save_new_valid_exploration(
            self.EXP_ID_2, self.owner_id, title='Sillat Suomi',
            category='Architecture', language_code='fi')

    def _run_one_off_job(self):
        """Runs the one-off MapReduce job."""
        job_id = feedback_jobs_one_off.FeedbackThreadMessagesCountOneOffJob.create_new() # pylint: disable=line-too-long
        feedback_jobs_one_off.FeedbackThreadMessagesCountOneOffJob.enqueue(
            job_id)
        self.assertEqual(
            self.count_jobs_in_taskqueue(
                taskqueue_services.QUEUE_NAME_ONE_OFF_JOBS), 1)
        self.process_and_flush_pending_tasks()
        stringified_output = (
            feedback_jobs_one_off.FeedbackThreadMessagesCountOneOffJob.get_output( # pylint: disable=line-too-long
                job_id))

        eval_output = [ast.literal_eval(stringified_item)
                       for stringified_item in stringified_output]
        return eval_output

    def test_message_count(self):
        """Test if the job returns the correct message count."""
        feedback_services.create_thread(
            self.EXP_ID_1, self.EXPECTED_THREAD_DICT['state_name'],
            self.user_id, self.EXPECTED_THREAD_DICT['subject'],
            'not used here')
        feedback_services.create_thread(
            self.EXP_ID_2, self.EXPECTED_THREAD_DICT['state_name'],
            self.user_id, self.EXPECTED_THREAD_DICT['subject'],
            'not used here')

        thread_ids = subscription_services.get_all_threads_subscribed_to(
            self.user_id)

        self._run_one_off_job()

        thread_summaries, _ = feedback_services.get_thread_summaries(
            self.user_id, thread_ids)

        # Check that the first message has only one message.
        self.assertEqual(thread_summaries[0]['total_message_count'], 1)
        # Check that the second message has only one message.
        self.assertEqual(thread_summaries[1]['total_message_count'], 1)

        feedback_services.create_message(
            self.EXP_ID_1, thread_ids[0].split('.')[1], self.user_id, None,
            None, 'editor message')

        self._run_one_off_job()

        thread_summaries, _ = feedback_services.get_thread_summaries(
            self.user_id, thread_ids)

        # Check that the first message has two messages.
        self.assertEqual(thread_summaries[0]['total_message_count'], 2)

        # Get the first message so that we can delete it and check the error
        # case.
        first_message_model = (
            feedback_models.FeedbackMessageModel.get(
                self.EXP_ID_1, thread_ids[0].split('.')[1], 0))

        first_message_model.delete()

        output = self._run_one_off_job()
        # Check if the quantities have the correct values.
        self.assertEqual(output[0][1]['message_count'], 1)
        self.assertEqual(output[0][1]['next_message_id'], 2)


class FeedbackSubjectOneOffJobTest(test_utils.GenericTestBase):
    """Tests for the one-off feedback subject update job."""
    EXP_ID_1 = 'eid1'

    EXPECTED_THREAD_DICT1 = {
        'text': u'a small summary',
        'subject': u'(Feedback from a learner)'
    }

    EXPECTED_THREAD_DICT2 = {
        'text': u'a small text',
        'subject': u'Some subject'
    }

    EXPECTED_THREAD_DICT3 = {
        'text': (
            u'It has to convert to a substring as it exceeds the '
            u'character limit.'),
        'subject': u'(Feedback from a learner)'
    }

    EXPECTED_THREAD_DICT4 = {
        'text': (
            u'Itisjustaverylongsinglewordfortestingget'
            u'AbbreviatedText.'),
        'subject': u'(Feedback from a learner)'
    }

    EXPECTED_THREAD_DICT5 = {
        'text': '',
        'subject': u'(Feedback from a learner)'
    }

    EXPECTED_THREAD_DICT6 = {
        'text': 'Itisjustaverylongsinglewordfortesting',
        'subject': u'(Feedback from a learner)'
    }

    EXPECTED_THREAD_DICT7 = {
        'text': (u'â, ??î or ôu🕧� n☁i✑💴++$-💯 ♓!🇪🚑🌚‼⁉4⃣od; /⏬®;😁☕😁:☝)'
                 u'😁😁😍1!@#'),
        'subject': u'(Feedback from a learner)'
    }

    USER_EMAIL = 'user@example.com'
    USER_USERNAME = 'user'

    def setUp(self):
        super(FeedbackSubjectOneOffJobTest, self).setUp()

        self.signup(self.USER_EMAIL, self.USER_USERNAME)
        self.user_id = self.get_user_id_from_email(self.USER_EMAIL)
        self.signup(self.OWNER_EMAIL, self.OWNER_USERNAME)
        self.owner_id = self.get_user_id_from_email(self.OWNER_EMAIL)

        self.save_new_valid_exploration(
            self.EXP_ID_1, self.owner_id, title='Bridges in England',
            category='Architecture', language_code='en')

    def _run_one_off_job(self):
        """Runs the one-off MapReduce job."""
        job_id = (
            feedback_jobs_one_off.FeedbackSubjectOneOffJob.create_new())
        feedback_jobs_one_off.FeedbackSubjectOneOffJob.enqueue(
            job_id)
        self.assertEqual(
            self.count_jobs_in_taskqueue(
                taskqueue_services.QUEUE_NAME_ONE_OFF_JOBS), 1)
        self.process_and_flush_pending_tasks()

    def test_that_job_returns_correct_feedback_subject(self):
        """Test if the job returns the correct feedback subject."""
        feedback_services.create_thread(
            self.EXP_ID_1, 'unused_state_name', self.user_id,
            self.EXPECTED_THREAD_DICT1['subject'],
            self.EXPECTED_THREAD_DICT1['text'])
        feedback_services.create_thread(
            self.EXP_ID_1, 'unused_state_name', self.user_id,
            self.EXPECTED_THREAD_DICT2['subject'],
            self.EXPECTED_THREAD_DICT2['text'])
        feedback_services.create_thread(
            self.EXP_ID_1, 'unused_state_name', self.user_id,
            self.EXPECTED_THREAD_DICT3['subject'],
            self.EXPECTED_THREAD_DICT3['text'])
        feedback_services.create_thread(
            self.EXP_ID_1, 'unused_state_name', self.user_id,
            self.EXPECTED_THREAD_DICT4['subject'],
            self.EXPECTED_THREAD_DICT4['text'])
        feedback_services.create_thread(
            self.EXP_ID_1, 'unused_state_name', self.user_id,
            self.EXPECTED_THREAD_DICT5['subject'],
            self.EXPECTED_THREAD_DICT5['text'])
        feedback_services.create_thread(
            self.EXP_ID_1, 'unused_state_name', self.user_id,
            self.EXPECTED_THREAD_DICT6['subject'],
            self.EXPECTED_THREAD_DICT6['text'])
        feedback_services.create_thread(
            self.EXP_ID_1, 'unused_state_name', self.user_id,
            self.EXPECTED_THREAD_DICT7['subject'],
            self.EXPECTED_THREAD_DICT7['text'])
        threads_old = feedback_services.get_threads(self.EXP_ID_1)

        self._run_one_off_job()

        threads = feedback_services.get_threads(self.EXP_ID_1)

        self.assertEqual(threads[0].subject, u'a small summary')
        self.assertEqual(threads[1].subject, u'Some subject')
        self.assertEqual(
            threads[2].subject,
            u'It has to convert to a substring as it exceeds...')
        self.assertEqual(
            threads[3].subject,
            u'ItisjustaverylongsinglewordfortestinggetAbbreviate...')
        self.assertEqual(threads[4].subject, u'(Feedback from a learner)')
        self.assertEqual(
            threads[5].subject,
            u'Itisjustaverylongsinglewordfortesting')
        self.assertEqual(
            threads[6].subject,
            u'â, ??î or ôu🕧� n☁i✑💴++$-💯 ♓!🇪🚑🌚‼⁉4⃣od;...')

        self.assertEqual(threads[0].last_updated, threads_old[0].last_updated)
        self.assertEqual(threads[1].last_updated, threads_old[1].last_updated)
        self.assertEqual(threads[2].last_updated, threads_old[2].last_updated)
        self.assertEqual(threads[3].last_updated, threads_old[3].last_updated)
        self.assertEqual(threads[4].last_updated, threads_old[4].last_updated)
        self.assertEqual(threads[5].last_updated, threads_old[5].last_updated)
