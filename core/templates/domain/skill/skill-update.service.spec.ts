// Copyright 2018 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Unit tests for SkillUpdateService.
 */

// TODO(#7222): Remove the following block of unnnecessary imports once
// skill-update.service.ts is upgraded to Angular 8.
import { SubtitledHtml } from 'domain/exploration/SubtitledHtml.model';
import { Misconception } from 'domain/skill/Misconception.model';
import { Skill } from 'domain/skill/Skill.model'

import { UpgradedServices } from 'services/UpgradedServices';
import { WorkedExample } from 'domain/skill/WorkedExample.model';
// ^^^ This block is to be removed.

require('App.ts');
require('domain/editor/undo_redo/undo-redo.service.ts');
require('domain/skill/skill-update.service.ts');

describe('Skill update service', function() {
  var SkillUpdateService = null,
    skillDifficulties = null,
    UndoRedoService = null;
  var skillDict = null;

  beforeEach(angular.mock.module('oppia'));

  beforeEach(angular.mock.module('oppia', function($provide) {
    var ugs = new UpgradedServices();
    for (let [key, value] of Object.entries(ugs.getUpgradedServices())) {
      $provide.value(key, value);
    }
  }));

  beforeEach(angular.mock.inject(function($injector) {
    SkillUpdateService = $injector.get('SkillUpdateService');
    UndoRedoService = $injector.get('UndoRedoService');
    skillDifficulties = $injector.get('SKILL_DIFFICULTIES');

    var misconceptionDict1 = {
      id: '2',
      name: 'test name',
      notes: 'test notes',
      feedback: 'test feedback',
      must_be_addressed: true
    };

    var misconceptionDict2 = {
      id: '4',
      name: 'test name',
      notes: 'test notes',
      feedback: 'test feedback',
      must_be_addressed: true
    };

    var rubricDict = {
      difficulty: skillDifficulties[0],
      explanations: ['explanation']
    };

    var example1 = {
      question: {
        html: 'worked example question 1',
        content_id: 'worked_example_q_1'
      },
      explanation: {
        html: 'worked example explanation 1',
        content_id: 'worked_example_e_1'
      }
    };

    var example2 = {
      question: {
        html: 'worked example question 2',
        content_id: 'worked_example_q_2'
      },
      explanation: {
        html: 'worked example explanation 2',
        content_id: 'worked_example_e_2'
      }
    };

    var skillContentsDict = {
      explanation: {
        html: 'test explanation',
        content_id: 'explanation',
      },
      worked_examples: [example1, example2],
      recorded_voiceovers: {
        voiceovers_mapping: {
          explanation: {},
          worked_example_q_1: {},
          worked_example_e_1: {},
          worked_example_q_2: {},
          worked_example_e_2: {}
        }
      }
    };

    skillDict = {
      id: '1',
      description: 'test description',
      misconceptions: [misconceptionDict1, misconceptionDict2],
      rubrics: [rubricDict],
      skill_contents: skillContentsDict,
      language_code: 'en',
      version: 3,
      prerequisite_skill_ids: ['skill_1']
    };
  }));

  it('should set/unset the skill description', function() {
    var skill = Skill.createFromBackendDict(skillDict);
    SkillUpdateService.setSkillDescription(skill, 'new description');
    expect(UndoRedoService.getCommittableChangeList()).toEqual([{
      cmd: 'update_skill_property',
      property_name: 'description',
      old_value: 'test description',
      new_value: 'new description'
    }]);
    expect(skill.getDescription()).toEqual('new description');
    UndoRedoService.undoChange(skill);
    expect(skill.getDescription()).toEqual('test description');
  });

  it('should set/unset the concept card explanation', function() {
    var skill = Skill.createFromBackendDict(skillDict);
    SkillUpdateService.setConceptCardExplanation(
      skill, SubtitledHtml.createDefault(
        'new explanation', 'explanation'));
    expect(UndoRedoService.getCommittableChangeList()).toEqual([{
      cmd: 'update_skill_contents_property',
      property_name: 'explanation',
      old_value: {
        html: 'test explanation',
        content_id: 'explanation'
      },
      new_value: {
        html: 'new explanation',
        content_id: 'explanation'
      }
    }]);
    expect(skill.getConceptCard().getExplanation()).toEqual(
      SubtitledHtml.createDefault(
        'new explanation', 'explanation'));
    UndoRedoService.undoChange(skill);
    expect(skill.getConceptCard().getExplanation()).toEqual(
      SubtitledHtml.createDefault(
        'test explanation', 'explanation'));
  });

  it('should add a misconception', function() {
    var skill = Skill.createFromBackendDict(skillDict);
    var aNewMisconceptionDict = {
      id: '7',
      name: 'test name 3',
      notes: 'test notes 3',
      feedback: 'test feedback 3',
      must_be_addressed: true
    };
    var aNewMisconception = Misconception.createFromBackendDict(
      aNewMisconceptionDict);
    SkillUpdateService.addMisconception(skill, aNewMisconception);
    expect(UndoRedoService.getCommittableChangeList()).toEqual([{
      cmd: 'add_skill_misconception',
      new_misconception_dict: aNewMisconceptionDict
    }]);
    expect(skill.getMisconceptions().length).toEqual(3);
    UndoRedoService.undoChange(skill);
    expect(skill.getMisconceptions().length).toEqual(2);
  });

  it('should delete a misconception', function() {
    var skill = Skill.createFromBackendDict(skillDict);
    SkillUpdateService.deleteMisconception(skill, '2');
    expect(UndoRedoService.getCommittableChangeList()).toEqual([{
      cmd: 'delete_skill_misconception',
      misconception_id: '2'
    }]);
    expect(skill.getMisconceptions().length).toEqual(1);
    UndoRedoService.undoChange(skill);
    expect(skill.getMisconceptions().length).toEqual(2);
  });

  it('should add a prerequisite skill', function() {
    var skill = Skill.createFromBackendDict(skillDict);
    SkillUpdateService.addPrerequisiteSkill(skill, 'skill_2');
    expect(UndoRedoService.getCommittableChangeList()).toEqual([{
      cmd: 'add_prerequisite_skill',
      skill_id: 'skill_2'
    }]);
    expect(skill.getPrerequisiteSkillIds().length).toEqual(2);
    UndoRedoService.undoChange(skill);
    expect(skill.getPrerequisiteSkillIds().length).toEqual(1);
  });

  it('should delete a prerequisite skill', function() {
    var skill = Skill.createFromBackendDict(skillDict);
    SkillUpdateService.deletePrerequisiteSkill(skill, 'skill_1');
    expect(UndoRedoService.getCommittableChangeList()).toEqual([{
      cmd: 'delete_prerequisite_skill',
      skill_id: 'skill_1'
    }]);
    expect(skill.getPrerequisiteSkillIds().length).toEqual(0);
    UndoRedoService.undoChange(skill);
    expect(skill.getPrerequisiteSkillIds().length).toEqual(1);
  });

  it('should update a rubric', function() {
    var skill = Skill.createFromBackendDict(skillDict);
    expect(skill.getRubrics().length).toEqual(1);
    SkillUpdateService.updateRubricForDifficulty(
      skill, skillDifficulties[0], ['new explanation 1', 'new explanation 2']);
    expect(UndoRedoService.getCommittableChangeList()).toEqual([{
      cmd: 'update_rubrics',
      difficulty: skillDifficulties[0],
      explanations: ['new explanation 1', 'new explanation 2']
    }]);
    expect(skill.getRubrics().length).toEqual(1);
    expect(skill.getRubrics()[0].getExplanations()).toEqual([
      'new explanation 1', 'new explanation 2']);
    UndoRedoService.undoChange(skill);
    expect(skill.getRubrics().length).toEqual(1);
    expect(skill.getRubrics()[0].getExplanations()).toEqual(['explanation']);
  });

  it('should update the name of a misconception', function() {
    var skill = Skill.createFromBackendDict(skillDict);
    SkillUpdateService.updateMisconceptionName(
      skill, '2', skill.findMisconceptionById('2').getName(), 'new name');
    expect(UndoRedoService.getCommittableChangeList()).toEqual([{
      cmd: 'update_skill_misconceptions_property',
      property_name: 'name',
      old_value: 'test name',
      new_value: 'new name',
      misconception_id: '2'
    }]);
    expect(skill.findMisconceptionById('2').getName()).toEqual('new name');
    UndoRedoService.undoChange(skill);
    expect(skill.findMisconceptionById('2').getName()).toEqual('test name');
  });

  it('should update the notes of a misconception', function() {
    var skill = Skill.createFromBackendDict(skillDict);
    SkillUpdateService.updateMisconceptionNotes(
      skill, '2', skill.findMisconceptionById('2').getNotes(), 'new notes');
    expect(UndoRedoService.getCommittableChangeList()).toEqual([{
      cmd: 'update_skill_misconceptions_property',
      property_name: 'notes',
      old_value: 'test notes',
      new_value: 'new notes',
      misconception_id: '2'
    }]);
    expect(skill.findMisconceptionById('2').getNotes()).toEqual('new notes');
    UndoRedoService.undoChange(skill);
    expect(skill.findMisconceptionById('2').getNotes()).toEqual('test notes');
  });

  it('should update the feedback of a misconception', function() {
    var skill = Skill.createFromBackendDict(skillDict);
    SkillUpdateService.updateMisconceptionFeedback(
      skill,
      '2',
      skill.findMisconceptionById('2').getFeedback(),
      'new feedback');
    expect(UndoRedoService.getCommittableChangeList()).toEqual([{
      cmd: 'update_skill_misconceptions_property',
      property_name: 'feedback',
      old_value: 'test feedback',
      new_value: 'new feedback',
      misconception_id: '2'
    }]);
    expect(skill.findMisconceptionById('2').getFeedback())
      .toEqual('new feedback');
    UndoRedoService.undoChange(skill);
    expect(skill.findMisconceptionById('2').getFeedback())
      .toEqual('test feedback');
  });

  it('should update the feedback of a misconception', function() {
    var skill = Skill.createFromBackendDict(skillDict);
    SkillUpdateService.updateMisconceptionMustBeAddressed(
      skill,
      '2',
      skill.findMisconceptionById('2').isMandatory(),
      false);
    expect(UndoRedoService.getCommittableChangeList()).toEqual([{
      cmd: 'update_skill_misconceptions_property',
      property_name: 'must_be_addressed',
      old_value: true,
      new_value: false,
      misconception_id: '2'
    }]);
    expect(skill.findMisconceptionById('2').isMandatory())
      .toEqual(false);
    UndoRedoService.undoChange(skill);
    expect(skill.findMisconceptionById('2').isMandatory())
      .toEqual(true);
  });

  it('should add a worked example', function() {
    var skill = Skill.createFromBackendDict(skillDict);
    var example1 = {
      question: {
        html: 'worked example question 1',
        content_id: 'worked_example_q_1'
      },
      explanation: {
        html: 'worked example explanation 1',
        content_id: 'worked_example_e_1'
      }
    };
    var example2 = {
      question: {
        html: 'worked example question 2',
        content_id: 'worked_example_q_2'
      },
      explanation: {
        html: 'worked example explanation 2',
        content_id: 'worked_example_e_2'
      }
    };
    var newExample = {
      question: {
        html: 'worked example question 3',
        content_id: 'worked_example_q_3'
      },
      explanation: {
        html: 'worked example explanation 3',
        content_id: 'worked_example_e_3'
      }
    };
    SkillUpdateService.addWorkedExample(
      skill, WorkedExample.createFromBackendDict(newExample));
    expect(UndoRedoService.getCommittableChangeList()).toEqual([{
      cmd: 'update_skill_contents_property',
      property_name: 'worked_examples',
      old_value: [example1, example2],
      new_value: [example1, example2, newExample]
    }]);
    expect(skill.getConceptCard().getWorkedExamples()).toEqual([
      WorkedExample.createFromBackendDict(example1),
      WorkedExample.createFromBackendDict(example2),
      WorkedExample.createFromBackendDict(newExample)]);
    UndoRedoService.undoChange(skill);
    expect(skill.getConceptCard().getWorkedExamples()).toEqual([
      WorkedExample.createFromBackendDict(example1),
      WorkedExample.createFromBackendDict(example2)]);
  });

  it('should delete a worked example', function() {
    var skill = Skill.createFromBackendDict(skillDict);
    var example1 = {
      question: {
        html: 'worked example question 1',
        content_id: 'worked_example_q_1'
      },
      explanation: {
        html: 'worked example explanation 1',
        content_id: 'worked_example_e_1'
      }
    };
    var example2 = {
      question: {
        html: 'worked example question 2',
        content_id: 'worked_example_q_2'
      },
      explanation: {
        html: 'worked example explanation 2',
        content_id: 'worked_example_e_2'
      }
    };
    SkillUpdateService.deleteWorkedExample(skill, 0);
    expect(UndoRedoService.getCommittableChangeList()).toEqual([{
      cmd: 'update_skill_contents_property',
      property_name: 'worked_examples',
      old_value: [example1, example2],
      new_value: [example2]
    }]);
    expect(skill.getConceptCard().getWorkedExamples()).toEqual([
      WorkedExample.createFromBackendDict(example2)]);
    UndoRedoService.undoChange(skill);
    expect(skill.getConceptCard().getWorkedExamples()).toEqual([
      WorkedExample.createFromBackendDict(example1),
      WorkedExample.createFromBackendDict(example2)]);
  });

  it('should update a worked example', function() {
    var skill = Skill.createFromBackendDict(skillDict);
    var example1 = {
      question: {
        html: 'worked example question 1',
        content_id: 'worked_example_q_1'
      },
      explanation: {
        html: 'worked example explanation 1',
        content_id: 'worked_example_e_1'
      }
    };
    var example2 = {
      question: {
        html: 'worked example question 2',
        content_id: 'worked_example_q_2'
      },
      explanation: {
        html: 'worked example explanation 2',
        content_id: 'worked_example_e_2'
      }
    };
    var modifiedExample1 = {
      question: {
        html: 'new question 1',
        content_id: 'worked_example_q_1'
      },
      explanation: {
        html: 'new explanation 1',
        content_id: 'worked_example_e_1'
      }
    };
    SkillUpdateService.updateWorkedExample(
      skill, 0, 'new question 1', 'new explanation 1');
    expect(UndoRedoService.getCommittableChangeList()).toEqual([{
      cmd: 'update_skill_contents_property',
      property_name: 'worked_examples',
      old_value: [example1, example2],
      new_value: [modifiedExample1, example2]
    }]);
    expect(skill.getConceptCard().getWorkedExamples()).toEqual([
      WorkedExample.createFromBackendDict(modifiedExample1),
      WorkedExample.createFromBackendDict(example2)]);
    UndoRedoService.undoChange(skill);
    expect(skill.getConceptCard().getWorkedExamples()).toEqual([
      WorkedExample.createFromBackendDict(example1),
      WorkedExample.createFromBackendDict(example2)]);
  });
});
