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

# Constants defining various suggestion types.
SUGGESTION_EDIT_STATE_CONTENT = 'edit_exploration_state_content'

SUGGESTION_TYPE_CHOICES = [
    SUGGESTION_EDIT_STATE_CONTENT
]

# Defines what is the minimum role required to review suggestions
# of a particular type.
SUGGESTION_MINIMUM_ROLE_FOR_REVIEW = {
    SUGGESTION_EDIT_STATE_CONTENT: feconf.ROLE_ID_EXPLORATION_EDITOR
}

# Constants defining various contribution types.
CONTRIBUTION_TYPE_CONTENT = 'content'
CONTRIBUTION_TYPE_TRANSLATION = 'translation'

CONTRIBUTION_TYPE_CHOICES = [
    CONTRIBUTION_TYPE_CONTENT,
    CONTRIBUTION_TYPE_TRANSLATION
]

#The delimiter to be used in the suggestion ID.
SUGGESTION_ID_DELIMITER = '.'


class SuggestionParams(ndb.Model):
    """Model to store all the suggestion params for a suggestion."""

    # The contribution type.
    contribution_type = ndb.StringProperty(
        required=True, choices=CONTRIBUTION_TYPE_CHOICES)
    # The contribution domain. This parameter along with the above contribution
    # type will be used to determine the category to 'score' the suggester.
    contribution_domain = ndb.StringProperty(required=True)
    # The ID of the entity being suggested to.
    entity_id = ndb.StringProperty(required=True)
    # The version number of the entity being suggested to.
    entity_version = ndb.IntegerProperty(required=True)


class SuggestionModel(base_models.BaseModel):
    """Model to store suggestions made by Oppia users."""

    # The type of suggestion.
    suggestion_type = ndb.StringProperty(
        required=True, indexed=True, choices=SUGGESTION_TYPE_CHOICES)
    # The type of entity which the suggestion is linked to.
    entity_type = ndb.StringProperty(
        required=True, indexed=True, choices=ENTITY_TYPE_CHOICES)
    # Status of the suggestion.
    status = ndb.StringProperty(
        required=True, indexed=True, choices=STATUS_CHOICES)
    # Additional parameters to be stored.
    suggestion_params = ndb.StructuredProperty(SuggestionParams)
    # The author of the suggestion.
    author_id = ndb.StringProperty(required=True, indexed=True)
    # The reviewer who accepted the suggestion.
    reviewer_id = ndb.StringProperty(required=False, indexed=True)
    # The thread linked to this suggestion.
    thread_id = ndb.StringProperty(required=True, indexed=True)
    # The reviewer assigned to review the suggestion.
    assigned_reviewer_id = ndb.StringProperty(required=True, indexed=True)
    # The suggestion payload. Contains the data of the suggestion. For "edit"
    # suggestions, this contains the change_list. For "add" suggestions, this
    # contains the data necessary to add the new entity.
    payload = ndb.JsonProperty(required=True, indexed=False)

    @classmethod
    def get_instance_id(
            cls, entity_type, thread_id, entity_id):
        """Concatenates various parameters and gives the ID of the suggestion
        model.

        Args:
            entity_type: str. The type of entity being edited/added.
            thread_id: str. The ID of the feedback thread linked to the
                suggestion.
            entity_id: str. The ID of the entity being edited.

        Returns:
            str. The full instance ID for the suggestion.
        """
        return SUGGESTION_ID_DELIMITER.join([entity_type, thread_id, entity_id])

    @classmethod
    def create(
            cls, suggestion_type, entity_type, status,
            suggestion_params, author_id, reviewer_id, thread_id,
            assigned_reviewer_id, payload):
        """Creates a new SuggestionModel entry.

        Args:
            suggestion_type: str. The type of the suggestion.
            entity_type: str. The type of entity being edited/added.
            status: str. The status of the suggestion.
            suggestion_params: dict. Additional parameters for the suggestion
            author_id: str. The ID of the user who submitted the suggestion.
            reviewer_id: str. The ID of the reviewer who has accepted the
                suggestion.
            thread_id: str. The ID of the feedback thread linked to the
                suggestion.
            assigned_reviewer_id: str. The ID of the user assigned to
                review the suggestion.
            payload: dict. The actual content of the suggestion.

        Raises:
            Exception: There is already a suggestion with the given id.
        """
        instance_id = cls.get_instance_id(
            entity_type, thread_id, suggestion_params['entity_id'])
        suggestion_params = SuggestionParams(
            contribution_type=suggestion_params['contribution_type'],
            contribution_domain=suggestion_params['contribution_domain'],
            entity_id=suggestion_params['entity_id'],
            entity_version=suggestion_params['entity_version'])

        if cls.get_by_id(instance_id):
            raise Exception('There is already a suggestion with the given'
                            ' id: %s' % instance_id)

        cls(id=instance_id, suggestion_type=suggestion_type,
            entity_type=entity_type, status=status,
            suggestion_params=suggestion_params, author_id=author_id,
            reviewer_id=reviewer_id, thread_id=thread_id,
            assigned_reviewer_id=assigned_reviewer_id, payload=payload).put()

    @classmethod
    def get_suggestions_by_type(cls, suggestion_type):
        """Gets all suggestions of a particular type

        Args:
            suggestion_type: str. The sub type of the suggestions.

        Returns:
            list(SuggestionModel). A list of suggestions of the given
                sub type, upto a maximum of feconf.DEFAULT_QUERY_LIMIT
                suggestions.
        """
        return cls.get_all().filter(
            cls.suggestion_type == suggestion_type).fetch(
                feconf.DEFAULT_QUERY_LIMIT)

    @classmethod
    def get_suggestions_by_author(cls, author_id):
        """Gets all suggestions created by the given author.

        Args:
            author_id: str. The author of the suggestion.

        Returns:
            list(SuggestionModel). A list of suggestions by the given author,
            upto a maximum of feconf.DEFAULT_QUERY_LIMIT suggestions.
        """
        return cls.get_all().filter(
            cls.author_id == author_id).fetch(feconf.DEFAULT_QUERY_LIMIT)

    @classmethod
    def get_suggestions_assigned_to_reviewer(cls, assigned_reviewer_id):
        """Gets all suggestions assigned to the given user for review.

        Args:
            assigned_reviewer_id: str. The reviewer assigned to review the
                suggestion.

        Returns:
            list(SuggestionModel). A list of suggestions assigned to the given
                user for review, upto a maximum of feconf.DEFAULT_QUERY_LIMIT
                suggestions.
        """
        return cls.get_all().filter(
            cls.assigned_reviewer_id == assigned_reviewer_id).fetch(
                feconf.DEFAULT_QUERY_LIMIT)

    @classmethod
    def get_suggestions_reviewed_by(cls, reviewer_id):
        """Gets all suggestions that have been reviewed by the given user.

        Args:
            reviewer_id: str. The reviewer of the suggestion.

        Returns:
            list(SuggestionModel). A list of suggestions reviewed by the given
                user, upto a maximum of feconf.DEFAULT_QUERY_LIMIT
                suggestions.
        """
        return cls.get_all().filter(
            cls.reviewer_id == reviewer_id).fetch(feconf.DEFAULT_QUERY_LIMIT)

    @classmethod
    def get_suggestions_by_status(cls, status):
        """Gets all suggestions with the given status.

        Args:
            status: str. The status of the suggestion.

        Returns:
            list(SuggestionModel). A list of suggestions with the given status,
            upto a maximum of feconf.DEFAULT_QUERY_LIMIT suggestions.
        """
        return cls.get_all().filter(
            cls.status == status).fetch(feconf.DEFAULT_QUERY_LIMIT)

    @classmethod
    def get_suggestions_by_entity_id(cls, entity_id, entity_type):
        """Gets all suggestions to the entity with the given ID.

        Args:
            entity_id: str. The ID of the entity.
            entity_type: str. The type of entity.

        Returns:
            list(SuggestionModel). A list of suggestions to the entity with the
            given id, upto a maximum of feconf.DEFAULT_QUERY_LIMIT suggestions.
        """
        return cls.get_all().filter(cls.entity_type == entity_type).filter(
            cls.suggestion_params.entity_id == entity_id).fetch(
                feconf.DEFAULT_QUERY_LIMIT)
