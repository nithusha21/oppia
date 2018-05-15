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

"""Commands that can be used on suggestions."""

from core.domain import exp_services
from core.domain import feedback_services
from core.domain import suggestion_domain
from core.platform import models

(feedback_models, suggestion_models) = models.Registry.import_models([
    models.NAMES.feedback, models.NAMES.suggestion])

DEFAULT_SUGGESTION_THREAD_SUBJECT = 'Suggestion from a learner'
DEFAULT_SUGGESTION_THREAD_INITIAL_MESSAGE = ''

def validate_suggestion_payload(suggestion_type, payload):
    """Checks whether the suggestion payload has all the necessary content for
    the given type of suggestion.

    Args:
        suggestion_type: str. The type of the suggestion.
        payload: dict. The actual content of the suggestion.

    Returns:
        bool. The validity of the given payload.
    """

    if suggestion_type == suggestion_models.SUGGESTION_TYPE_ADD:
        if not ('entity_type' in payload and 'entity_data' in payload):
            return False
    elif suggestion_type == suggestion_models.SUGGESTION_TYPE_EDIT:
        if not (
            'entity_id' in payload and'entity_version_number' in payload and
            'change_list' in payload):
            return False
    return True


def create_suggestion(
        suggestion_type, entity_type, suggestion_sub_type,
        suggestion_customization_args, author_id, payload, description,
        reviewer_id="", assigned_reviewer_id=""):
    """Creates a new SuggestionModel and the corresponding FeedbackThread.

    Args:
        suggestion_type: str. The type of the suggestion.
        entity_type: str. The entity being edited/added.
        suggestion_sub_type: str. The sub type of the suggestion.

        (The above 3 parameters Should be one of the constants defined in
        storage/suggestion/gae_models.py.)

        suggestion_customization_args: dict. Additional parameters to know the
            category of the contributions.
        author_id: str. The ID of the user who submitted the suggestion.
        payload: dict. The actual content of the suggestion. The contents depend
            on the type of suggestion.
        description: str. The description of the changes provided by the author.
        reviewer_id: str(optional). The ID of the reviewer who has accepted the
            suggestion.
        assigned_reviewer_id: str(optional). The ID of the user assigned to
            review the suggestion.
            TODO(nithesh): Make this assignment automatic.
    """
    if validate_suggestion_payload(suggestion_type, payload):
        thread_id = ''
        if entity_type == suggestion_models.ENTITY_TYPE_EXPLORATION:
            if suggestion_type == suggestion_models.SUGGESTION_TYPE_EDIT:
                # TODO (nithesh): Delink feedback threads from explorations.
                thread_id = feedback_services._create_models_for_thread_and_first_message( # pylint: disable=line-too-long
                    payload['entity_id'], None, author_id, description,
                    DEFAULT_SUGGESTION_THREAD_SUBJECT, True)
        suggestion_models.SuggestionModel.create(
            suggestion_type, entity_type, suggestion_sub_type,
            suggestion_models.STATUS_IN_REVIEW, suggestion_customization_args,
            author_id, reviewer_id, thread_id, assigned_reviewer_id, payload)
    else:
        raise Exception('Cannot create suggestion as invalid suggestion payload'
            ' is provided')

def get_suggestion_from_model(suggestion_model):
    """Converts the given SuggestionModel to a Suggestion object

    Args:
        suggestion_model: SuggestionModel.

    Returns:
        Suggestion. The corresponding Suggestion domain object.
    """
    return suggestion_domain.Suggestion(
        suggestion_model.suggestion_type, suggestion_model.entity_type,
        suggestion_model.suggestion_sub_type, suggestion_model.status,
        suggestion_model.suggestion_customization_args,
        suggestion_model.author_id, suggestion_model.reviewer_id,
        suggestion_model.thread_id, suggestion_model.assigned_reviewer_id,
        suggestion_model.payload)

def get_suggestion(suggestion_type, entity_type, thread_id, entity_id=''):
    """Finds a suggestion by the instance ID which is created as a combination
    of suggestion_type, entity_type, thread_id and entity_id.

    Args:
        suggestion_type: str. The type of the suggestion.
        entity_type: str. The type of entity being edited/added.
        thread_id: str. The ID of the feedback thread linked to the
            suggestion.
        entity_id: str(optional). The ID of the entity being edited. If a
            new entity is being added, '' is passed.

    Returns:
        Suggestion, or None if no suggestion is found.
    """
    suggestion_id = suggestion_models.SuggestionModel.get_instance_id(
        suggestion_type, entity_type, thread_id, entity_id)
    model = suggestion_models.SuggestionModel.get_by_id(suggestion_id)

    return get_suggestion_from_model(model) if model else None

def update_suggestion(suggestion):
    """Updates the given sugesstion. The properties that can be edited are the
    following:
        status, reviewer_id, assigned_reviewer_id, payload['change_list'] or
        payload['entity_data']
    """
    if suggestion.suggestion_type == suggestion_models.SUGGESTION_TYPE_EDIT:
        suggestion_model = suggestion_models.SuggestionModel.get_instance_id(
            suggestion.suggestion_type, suggestion.entity_type,
            suggestion.thread_id, suggestion.payload['entity_id'])
    else:
        suggestion_model = suggestion_models.SuggestionModel.get_instance_id(
            suggestion.suggestion_type, suggestion.entity_type,
            suggestion.thread_id)

    suggestion_model.status = suggestion.status
    suggestion_model.reviewer_id = suggestion.reviewer_id
    suggestion_model.assigned_reviewer_id = suggestion.assigned_reviewer_id

    if suggestion.suggestion_type == suggestion_models.SUGGESTION_TYPE_EDIT:
        suggestion_model.payload['change_list'] = suggestion.payload[
            'change_list']
    elif suggestion.suggestion_type == suggestion_models.SUGGESTION_TYPE_ADD:
        suggestion_model.payload['entity_data'] = suggestion.payload[
        'entity_data']
    suggestion_model.save()

def validate_suggestion(suggestion, reviewer_id):
    """Validates a suggestion. This function should be called before accepting
    the suggestion.

    Args:
        suggestion: Suggestion. The domain object of the suggestion to be
            validated.
        reviewer_id: str. The ID of the reviewer who is reviewing the
            suggestion.

    Returns:
        bool. The validity of the suggestion.
    """

    if suggestion.status == suggestion_models.STATUS_IN_REVIEW:
        if (
            suggestion.suggestion_type ==
            suggestion_models.SUGGESTION_TYPE_EDIT):
            if (
                suggestion.suggestion_sub_type ==
                suggestion_models.SUGGESTION_EDIT_STATE_CONTENT):
                states = exp_services.get_exploration_by_id(
                    suggestion.payload['entity_id'])
                state = suggestion.payload['change_list']['state_name']
                if state not in states:
                    suggestion.status = suggestion_models.STATUS_INVALID
                    update_suggestion(suggestion)
                    feedback_services.create_message(
                        suggestion_model.payload['entity_id'],
                        suggestion_model.thread_id, reviewer_id,
                        feedback_models.STATUS_CHOICES_IGNORED)
                    return False
    return True

def is_suggestion_handled(suggestion):
    """Checks if the suggestion has been handled.

    Args:
        suggestion: Suggestion. The domain object of the suggestion to be
            checked.

    Returns:
        bool. Whether the suggestion has been handled or not.
    """
    return not (suggestion.status == suggestion_models.STATUS_IN_REVIEW)

def accept_suggestion(suggestion, reviewer_id, commit_message):
    """Accepts the given suggestion after validating it.

    Args:
        suggestion: Suggestion. The domain object of the suggestion to be
            accepted.
        reviewer_id: str. The ID of the reviewer accepting the suggestion.
        commit_message: str. The commit message.

    Raises:
        Exception: The suggestion is already handled.
        Exception: The suggestion is not valid.
        Exception: The commit message is empty.
    """
    pass
