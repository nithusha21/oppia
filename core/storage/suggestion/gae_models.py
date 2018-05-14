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

"""Models for Oppia suggestions."""

from core.platform import models
import feconf

from google.appengine.ext import ndb

(base_models,) = models.Registry.import_models([models.NAMES.base_model])

# Constants defining the types of suggestions.
SUGGESTION_TYPE_ADD = 'add'
SUGGESTION_TYPE_EDIT = 'edit'

SUGGESTION_TYPE_CHOICES = [
    SUGGESTION_TYPE_ADD,
    SUGGESTION_TYPE_EDIT
]

# Constants defining types of entities to which suggestions can be created.
ENTITY_TYPE_EXPLORATION = 'exploration'
ENTITY_TYPE_QUESTION = 'question'
ENTITY_TYPE_SKILL = 'skill'
ENTITY_TYPE_TOPIC = 'topic'

ENTITY_TYPE_CHOICES = [
    ENTITY_TYPE_EXPLORATION,
    ENTITY_TYPE_QUESTION,
    ENTITY_TYPE_SKILL,
    ENTITY_TYPE_TOPIC
]

# Constants defining the different possible statuses of a suggestion.
STATUS_ACCEPTED = 'accepted'
STATUS_IN_REVIEW = 'review'
STATUS_INVALID = 'invalid'
STATUS_REJECTED = 'rejected'

STATUS_CHOICES = [
    STATUS_ACCEPTED,
    STATUS_IN_REVIEW,
    STATUS_INVALID,
    STATUS_REJECTED
]

# Constants defining suggestion sub-types for each of the above types.
SUGGESTION_EDIT_STATE_CONTENT = 'edit_exploration_state_content'

SUGGESTION_SUB_TYPES = {
    SUGGESTION_TYPE_ADD: [],
    SUGGESTION_TYPE_EDIT: [
        SUGGESTION_EDIT_STATE_CONTENT
    ]
}

SUGGESTION_SUB_TYPE_CHOICES = [
    SUGGESTION_EDIT_STATE_CONTENT
]

# Defines what is the minimum role required to review suggestions
# of a particular sub-type.
SUGGESTION_MINIMUM_ROLE_FOR_REVIEW = {
    SUGGESTION_EDIT_STATE_CONTENT: feconf.ROLE_ID_EXPLORATION_EDITOR
}


class SuggestionModel(base_models.BaseModel):
    """Model to store suggestions made by Oppia users."""

    # The type of suggestion.
    suggestion_type = ndb.StringProperty(
        required=True, indexed=True, choices=SUGGESTION_TYPE_CHOICES)
    # The type of entity which the suggestion is linked to.
    entity_type = ndb.StringProperty(
        required=True, indexed=True, choices=ENTITY_TYPE_CHOICES)
    # The sub-type of the suggestion.
    suggestion_sub_type = ndb.StringProperty(
        required=True, indexed=True, choices=SUGGESTION_SUB_TYPE_CHOICES)
    # Status of the suggestion.
    status = ndb.StringProperty(
        required=True, indexed=True, choices=STATUS_CHOICES)
    # Additional parameters to be stored. The parameters include:
    #   contribution_type: Either translation related or content related.
    #
    #   contribution_category: The content subject category
    #                          (like algebra, algorithms, etc)
    #   OR
    #
    #   contribution_language: The language of the translation submitted.
    suggestion_customization_args = ndb.JsonProperty(
        required=True, indexed=True)
    # The author of the suggestion.
    author_id = ndb.StringProperty(required=True, indexed=True)
    # The reviewer who accepted the suggestion.
    reviewer_id = ndb.StringProperty(required=False, indexed=True)
    # The thread linked to this suggestion.
    thread_id = ndb.StringProperty(required=True, indexed=True)
    # The reviewer assigned to review the suggestion.
    assigned_reviewer_id = ndb.StringProperty(required=True, indexed=True)
    # The suggestion payload. Stores the details specific to the suggestion.
    # The structure depends on the type of suggestion. For "edit" suggestions,
    # the required parameters are:
    #   entity_id: The ID of the entity being edited.
    #   entity_version_number: The version of the entity being edited.
    #   change_list: An appropriate changelist which needs to be applied to the
    #                entity.
    # For "add" suggestions, the required parameters are:
    #   entity_type: The type of entity being added.
    #   entity_data: The data that is needed to create the entity.
    payload = ndb.JsonProperty(required=True, indexed=False)
