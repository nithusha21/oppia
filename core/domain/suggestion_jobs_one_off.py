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

"""One-off jobs relating to suggestions."""

from core import jobs
from core.platform import models

(suggestion_models, user_models) = models.Registry.import_models(
    [models.NAMES.suggestion, models.NAMES.user])


class PopulateUserContributionsScoringModel(jobs.BaseMapReduceOneOffJobManager):
    """One-off job to populate scores for contributions of users in the old
    system.
    """
    @classmethod
    def entity_classes_to_map_over(cls):
        return [suggestion_models.GeneralSuggestionModel]

    @staticmethod
    def map(suggestion):
        if suggestion.status == suggestion_models.STATUS_ACCEPTED:
            user_contribution_scoring_model_id = '%s.%s' % (
                suggestion.score_category, suggestion.author_id)
            yield (user_contribution_scoring_model_id, 1)

    @staticmethod
    def reduce(key, value):
        score = len(value)
        score_category = key[: key.rfind('.')]
        user_id = key[key.rfind('.') + 1:]
        user_models.UserContributionScoringModel.create(
            user_id, score_category, score)
