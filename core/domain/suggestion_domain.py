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

"""Domain object for Oppia suggestions."""

from core.domain import user_services


class Suggestion(object):
    """Domain object for a suggestion.

    Attributes:
        suggestion_type: str. The type of suggestion.
        entity_type: str. The type of entity which the suggestion is linked to.
        suggestion_sub_type: str. The sub-type of the suggestion.
        status: str. The status of the suggestion.
        suggestion_customization_args: dict. Additional customization args for
            the suggestion. Should contain a 'contribution_type' key. One more
            key is needed and it's value depends on the contribution_type.
            If contribution_type is translation, a 'contribution_language' key
            is needed, else if contribution_type is content, a
            'contribution_category' key is needed.
        author_id: str. The ID of the author of the suggestion.
        reviewer_id: str. Optional. The ID of the reviewer who accepted the
            suggestion.
        thread_id: str. The thread linked to this suggestion.
        assigned_reviewer_id: str. The ID of the reviewer assigned to review
            the suggestion.
        payload: dict. The suggestion payload. Stores the details specific
            to the suggestion. The structure depends on the type of suggestion.
            For "edit" suggestions, the required parameters are:
                entity_id: The ID of the entity being edited.
                entity_version_number: The version of the entity being edited.
                change_list: An appropriate change list which needs to be
                    applied to the entity.
            For "add" suggestions, the required parameters are:
                entity_type: The type of entity being added.
                entity_data: The data that is needed to create the entity.
    """

    def __init__(
        self, suggestion_type, entity_type, suggestion_sub_type, status,
        suggestion_customization_args, author_id, reviewer_id, thread_id,
        assigned_reviewer_id, payload):
        """Initializes a suggestion object."""

        self.suggestion_type = suggestion_type
        self.entity_type = entity_type
        self.suggestion_sub_type = suggestion_sub_type
        self.status = status
        self.suggestion_customization_args = suggestion_customization_args
        self.author_id = author_id
        self.reviewer_id = reviewer_id
        self.thread_id = thread_id
        self.assigned_reviewer_id = assigned_reviewer_id
        self.payload = payload

    def get_author_name(self):
        """Returns the author's username.

        Returns:
            str. The username of the author of the suggestion.
        """
        return user_services.get_username(self.author_id)

    def get_reviewer_name(self):
        """Returns the reviewer's username.

        Returns:
            str. The username of the reviewer of the suggestion.
        """
        if self.reviewer_id:
            return user_services.get_username(self.reviewer_id)
        return ''

    def get_assigned_reviewer_name(self):
        """Returns the assigned reviewer's username.

        Returns:
            str. The username of the assigned reviewer of the suggestion.
        """
        return user_services.get_username(self.assigned_reviewer_id)

    def to_dict(self):
        """Returns a dict representation of a suggestion object.

        Returns:
            dict. A dict representation of a suggestion object.
        """
        return {
            'suggestion_type': self.suggestion_type,
            'entity_type': self.entity_type,
            'suggestion_sub_type': self.suggestion_sub_type,
            'status': self.status,
            'customization_args': self.suggestion_customization_args,
            'author_name': self.get_author_name(),
            'reviewer_name': self.get_reviewer_name(),
            'thread_id': self.thread_id,
            'assigned_reviewer_name': self.get_assigned_reviewer_name(),
            'payload': self.payload
        }
