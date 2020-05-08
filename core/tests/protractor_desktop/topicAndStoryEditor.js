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
 * @fileoverview End-to-end tests for the topic editor page.
 */

var forms = require('../protractor_utils/forms.js');
var general = require('../protractor_utils/general.js');
var users = require('../protractor_utils/users.js');
var waitFor = require('../protractor_utils/waitFor.js');
var workflow = require('../protractor_utils/workflow.js');

var AdminPage = require('../protractor_utils/AdminPage.js');
var TopicsAndSkillsDashboardPage =
  require('../protractor_utils/TopicsAndSkillsDashboardPage.js');
var TopicEditorPage = require('../protractor_utils/TopicEditorPage.js');
var StoryEditorPage = require('../protractor_utils/StoryEditorPage.js');
var SkillEditorPage = require('../protractor_utils/SkillEditorPage.js');
var ExplorationEditorPage =
  require('../protractor_utils/ExplorationEditorPage.js');
var ExplorationPlayerPage =
  require('../protractor_utils/ExplorationPlayerPage.js');

describe('Topic editor functionality', function() {
  var topicsAndSkillsDashboardPage = null;
  var topicEditorPage = null;
  var storyEditorPage = null;
  var topicId = null;
  var skillEditorPage = null;
  var explorationEditorPage = null;
  var explorationEditorMainTab = null;

  beforeAll(async function() {
    topicsAndSkillsDashboardPage =
      new TopicsAndSkillsDashboardPage.TopicsAndSkillsDashboardPage();
    topicEditorPage = new TopicEditorPage.TopicEditorPage();
    storyEditorPage = new StoryEditorPage.StoryEditorPage();
    skillEditorPage = new SkillEditorPage.SkillEditorPage();
    explorationEditorPage = new ExplorationEditorPage.ExplorationEditorPage();
    explorationEditorMainTab = explorationEditorPage.getMainTab();
    await users.createAndLoginAdminUser(
      'creator@topicEditor.com', 'creatorTopicEditor');
    var handle = await browser.getWindowHandle();
    topicsAndSkillsDashboardPage.get();
    topicsAndSkillsDashboardPage.createTopic('Topic 1', false);
    var url = await browser.getCurrentUrl();
    topicId = url.split('/')[4];
    general.closeCurrentTabAndSwitchTo(handle);
  });

  beforeEach(async function() {
    await users.login('creator@topicEditor.com');
    topicEditorPage.get(topicId);
  });

  it('should add and delete subtopics correctly', async function() {
    topicEditorPage.moveToSubtopicsTab();
    topicEditorPage.addSubtopic('Subtopic 1');
    topicEditorPage.expectNumberOfSubtopicsToBe(1);
    topicEditorPage.saveTopic('Added subtopic.');

    topicEditorPage.get(topicId);
    topicEditorPage.moveToSubtopicsTab();
    topicEditorPage.expectNumberOfSubtopicsToBe(1);
    topicEditorPage.deleteSubtopicWithIndex(0);
    topicEditorPage.expectNumberOfSubtopicsToBe(0);
  });

  it('should create a question for a skill in the topic', async function() {
    var skillId = null;
    var handle = await browser.getWindowHandle();
    topicsAndSkillsDashboardPage.get();
    topicsAndSkillsDashboardPage.createSkillWithDescriptionAndExplanation(
      'Skill 1', 'Concept card explanation', false);
    var url = await browser.getCurrentUrl();
    skillId = url.split('/')[4];
    general.closeCurrentTabAndSwitchTo(handle);
    topicsAndSkillsDashboardPage.get();
    topicsAndSkillsDashboardPage.navigateToUnusedSkillsTab();
    topicsAndSkillsDashboardPage.assignSkillWithIndexToTopic(0, 0);

    topicEditorPage.get(topicId);
    topicEditorPage.moveToQuestionsTab();
    topicEditorPage.createQuestionForSkillWithIndex(0);
    explorationEditorMainTab.setContent(forms.toRichText('Question 1'));
    explorationEditorMainTab.setInteraction('TextInput', 'Placeholder', 5);
    explorationEditorMainTab.addResponse(
      'TextInput', forms.toRichText('Correct Answer'), null, false,
      'FuzzyEquals', 'correct');
    explorationEditorMainTab.getResponseEditor(0).markAsCorrect();
    explorationEditorMainTab.addHint('Hint 1');
    explorationEditorMainTab.addSolution('TextInput', {
      correctAnswer: 'correct',
      explanation: 'It is correct'
    });
    topicEditorPage.saveQuestion();

    topicEditorPage.get(topicId);
    topicEditorPage.moveToQuestionsTab();
    topicEditorPage.expectNumberOfQuestionsForSkillWithDescriptionToBe(
      1, 'Skill 1');

    skillEditorPage.get(skillId);
    skillEditorPage.moveToQuestionsTab();
    skillEditorPage.expectNumberOfQuestionsToBe(1);
  });

  it('should add a canonical story to topic correctly', async function() {
    topicEditorPage.expectNumberOfStoriesToBe(0);
    topicEditorPage.createStory('Story Title');
    storyEditorPage.returnToTopic();

    topicEditorPage.expectNumberOfStoriesToBe(1);
  });

  it('should edit story title, description and notes correctly',
    async function() {
      topicEditorPage.navigateToStoryWithIndex(0);
      storyEditorPage.changeStoryNotes(forms.toRichText('Story notes'));
      storyEditorPage.changeStoryTitle('Story Title Edited');
      storyEditorPage.changeStoryDescription('Story Description');
      storyEditorPage.saveStory('Changed story title, description and notes');

      storyEditorPage.returnToTopic();
      topicEditorPage.expectStoryTitleToBe('Story Title Edited', 0);
      topicEditorPage.navigateToStoryWithIndex(0);

      storyEditorPage.expectTitleToBe('Story Title Edited');
      storyEditorPage.expectDescriptionToBe('Story Description');
      storyEditorPage.expectNotesToBe(forms.toRichText('Story notes'));
    });

  it('should add and remove nodes (chapters) from a story', async function() {
    topicEditorPage.navigateToStoryWithIndex(0);
    storyEditorPage.expectNumberOfChaptersToBe(0);
    storyEditorPage.createInitialChapter('Chapter 1');
    storyEditorPage.expectNumberOfChaptersToBe(1);

    storyEditorPage.createNewDestinationChapter('Chapter 2');
    storyEditorPage.expectNumberOfChaptersToBe(2);
    storyEditorPage.deleteChapterWithIndex(1);
    storyEditorPage.expectNumberOfChaptersToBe(1);
  });

  it('should publish and unpublish a story correctly', async function() {
    topicEditorPage.expectStoryPublicationStatusToBe('No', 0);
    topicEditorPage.navigateToStoryWithIndex(0);
    storyEditorPage.publishStory();
    storyEditorPage.returnToTopic();

    topicEditorPage.expectStoryPublicationStatusToBe('Yes', 0);
    topicEditorPage.navigateToStoryWithIndex(0);
    storyEditorPage.unpublishStory();
    storyEditorPage.returnToTopic();

    topicEditorPage.expectStoryPublicationStatusToBe('No', 0);
  });

  it('should assign a skill to, between, and from subtopics', async function() {
    topicsAndSkillsDashboardPage.get();
    topicsAndSkillsDashboardPage.createSkillWithDescriptionAndExplanation(
      'Skill 2', 'Concept card explanation', true);
    var TOPIC_NAME = 'TASE2';
    topicsAndSkillsDashboardPage.get();
    topicsAndSkillsDashboardPage.createTopic(TOPIC_NAME, false);
    topicsAndSkillsDashboardPage.get();
    topicsAndSkillsDashboardPage.navigateToUnusedSkillsTab();
    topicsAndSkillsDashboardPage.assignSkillWithIndexToTopicByTopicName(
      0, TOPIC_NAME);

    topicsAndSkillsDashboardPage.get();
    topicsAndSkillsDashboardPage.editTopic(TOPIC_NAME);
    topicEditorPage.moveToSubtopicsTab();
    topicEditorPage.addSubtopic('Subtopic 1');
    topicEditorPage.addSubtopic('Subtopic 2');
    topicEditorPage.saveTopic('Added subtopics.');

    topicEditorPage.expectSubtopicToHaveSkills(0, []);
    topicEditorPage.expectSubtopicToHaveSkills(1, []);

    topicEditorPage.dragSkillToSubtopic(0, 0);
    topicEditorPage.expectSubtopicToHaveSkills(0, ['Skill 2']);
    topicEditorPage.expectSubtopicToHaveSkills(1, []);

    topicEditorPage.dragSkillBetweenSubtopics(0, 0, 1);
    topicEditorPage.expectSubtopicToHaveSkills(0, []);
    topicEditorPage.expectSubtopicToHaveSkills(1, ['Skill 2']);

    topicEditorPage.dragSkillFromSubtopicToUncategorized(1, 0);
    topicEditorPage.expectSubtopicToHaveSkills(0, []);
    topicEditorPage.expectSubtopicToHaveSkills(1, []);
  });

  afterEach(async function() {
    general.checkForConsoleErrors([]);
    await users.logout();
  });
});

describe('Chapter editor functionality', function() {
  var topicsAndSkillsDashboardPage = null;
  var topicEditorPage = null;
  var storyEditorPage = null;
  var storyId = null;
  var explorationEditorPage = null;
  var dummyExplorationIds = [];
  var dummyExplorationInfo = [
    'Dummy exploration', 'Algorithm', 'Learn more about oppia', 'English'];
  var dummySkills = [];
  var allowedErrors = [];
  var topicName = 'Topic 0';
  var userEmail = 'creator@chapterTest.com';

  var createDummyExplorations = async function(numExplorations) {
    var ids = [];
    for (var i = 0; i < numExplorations; i++) {
      var info = dummyExplorationInfo.slice();
      info[0] += i.toString();
      workflow.createAndPublishExploration.apply(workflow, info);
      var url = await browser.getCurrentUrl();
      var id = url.split('/')[4].replace('#', '');
      ids.push(id);
    }
    return ids;
  };

  var createDummySkills = function(numSkills) {
    var skills = [];
    for (var i = 0; i < numSkills; i++) {
      var skillName = 'skillFromChapterEditor' + i.toString();
      var material = 'reviewMaterial' + i.toString();
      workflow.createSkillAndAssignTopic(skillName, material, topicName);
      skills.push(skillName);
    }
    return skills;
  };

  beforeAll(async function() {
    topicsAndSkillsDashboardPage =
      new TopicsAndSkillsDashboardPage.TopicsAndSkillsDashboardPage();
    topicEditorPage = new TopicEditorPage.TopicEditorPage();
    storyEditorPage = new StoryEditorPage.StoryEditorPage();
    skillEditorPage = new SkillEditorPage.SkillEditorPage();
    explorationEditorPage = new ExplorationEditorPage.ExplorationEditorPage();
    explorationPlayerPage = new ExplorationPlayerPage.ExplorationPlayerPage();
    explorationEditorMainTab = explorationEditorPage.getMainTab();
    await users.createAndLoginAdminUser(
      userEmail, 'creatorChapterTest');
    var handle = await browser.getWindowHandle();
    dummyExplorationIds = await createDummyExplorations(3);
    topicsAndSkillsDashboardPage.get();
    topicsAndSkillsDashboardPage.createTopic(topicName, false);
    topicEditorPage.createStory('Story 0');
    var url = await browser.getCurrentUrl();
    storyId = url.split('/')[4];
    general.closeCurrentTabAndSwitchTo(handle);
    dummySkills = createDummySkills(2);
  });

  beforeEach(async function() {
    await users.login(userEmail);
    storyEditorPage.get(storyId);
  });

  it('should create a basic chapter.', async function() {
    storyEditorPage.createInitialChapter('Chapter 1');
    storyEditorPage.setChapterExplorationId(dummyExplorationIds[0]);
    storyEditorPage.changeNodeOutline(forms.toRichText('First outline'));
    storyEditorPage.saveStory('First save');
  });

  it(
    'should check presence of skillreview RTE element in exploration ' +
    'linked to story', async function() {
      await browser.get('/create/' + dummyExplorationIds[0]);
      waitFor.pageToFullyLoad();
      explorationEditorMainTab.setContent(function(richTextEditor) {
        richTextEditor.addRteComponent(
          'Skillreview', 'Description', 'skillFromChapterEditor0');
      });
      explorationEditorPage.navigateToPreviewTab();
      explorationPlayerPage.expectContentToMatch(function(richTextChecker) {
        richTextChecker.readRteComponent(
          'Skillreview', 'Description', forms.toRichText('reviewMaterial0'));
      });
    });

  it('should add one more chapter to the story', async function() {
    storyEditorPage.createNewDestinationChapter('Chapter 2');
    storyEditorPage.navigateToChapterByIndex(1);
    storyEditorPage.changeNodeOutline(forms.toRichText('Second outline'));
    storyEditorPage.setChapterExplorationId(dummyExplorationIds[1]);
    storyEditorPage.saveStory('Second save');
  });

  it('should fail to add one more chapter with existing exploration',
    async function() {
      storyEditorPage.navigateToChapterByIndex(1);
      storyEditorPage.createNewDestinationChapter('Chapter 3');
      storyEditorPage.navigateToChapterByIndex(2);
      storyEditorPage.setChapterExplorationId(dummyExplorationIds[1]);
      storyEditorPage.expectExplorationIdAlreadyExistWarningAndCloseIt();
      allowedErrors.push('The given exploration already exists in the story.');
    }
  );

  it('should add one more chapter and change the chapters sequences',
    async function() {
      storyEditorPage.navigateToChapterByIndex(1);
      storyEditorPage.createNewDestinationChapter('Chapter 3');
      storyEditorPage.navigateToChapterByIndex(2);
      storyEditorPage.setChapterExplorationId(dummyExplorationIds[2]);
      storyEditorPage.selectInitialChapterByName('Chapter 2');

      // Now Chapter 2 is the initial chapter and its destination is
      // Chapter 3. Make Chapter 2's destination to be Chapter 1
      storyEditorPage.navigateToChapterByIndex(0);
      storyEditorPage.removeDestination();
      storyEditorPage.selectDestinationChapterByName('Chapter 1');
      storyEditorPage.expectDestinationToBe('Chapter 1');

      // Make chapter 1's destination to be Chapter 3
      storyEditorPage.navigateToChapterByIndex(1);
      storyEditorPage.selectDestinationChapterByName('Chapter 3');
      storyEditorPage.expectDestinationToBe('Chapter 3');
    }
  );

  it('should add one prerequisite and acquired skill to chapter 1',
    async function() {
      storyEditorPage.expectAcquiredSkillDescriptionCardCount(0);
      storyEditorPage.expectPrerequisiteSkillDescriptionCardCount(0);
      storyEditorPage.addAcquiredSkill(dummySkills[0]);
      storyEditorPage.expectAcquiredSkillDescriptionCardCount(1);
      storyEditorPage.addPrerequisiteSkill(dummySkills[1]);
      storyEditorPage.expectPrerequisiteSkillDescriptionCardCount(1);
      storyEditorPage.saveStory('Save');
    });

  it('should fail to add one prerequisite skill which is already added as' +
    ' acquired skill', async function() {
    storyEditorPage.addAcquiredSkill(dummySkills[1]);
    storyEditorPage.expectSaveStoryDisabled();
    var warningRegex = new RegExp(
      'The skill with id [a-zA-Z0-9]+ is common to both the acquired and ' +
      'prerequisite skill id ' +
      'list in .*');
    storyEditorPage.expectWarningInIndicator(warningRegex);
  });

  it('should delete prerequisite skill and acquired skill', async function() {
    storyEditorPage.deleteAcquiredSkillByIndex(0);
    storyEditorPage.expectAcquiredSkillDescriptionCardCount(0);
    storyEditorPage.deletePrerequisiteSkillByIndex(0);
    storyEditorPage.expectPrerequisiteSkillDescriptionCardCount(0);
  });

  it('should select the "Chapter 2" as initial chapter and get unreachable' +
    ' error', async function() {
    storyEditorPage.selectInitialChapterByName('Chapter 2');
    storyEditorPage.expectDisplayUnreachableChapterWarning();
  });

  it('should delete one chapter and save', async function() {
    storyEditorPage.expectNumberOfChaptersToBe(2);
    storyEditorPage.deleteChapterWithIndex(1);
    storyEditorPage.expectNumberOfChaptersToBe(1);
    storyEditorPage.saveStory('Last');
  });

  afterEach(function() {
    general.checkForConsoleErrors(allowedErrors);
    while (allowedErrors.length !== 0) {
      allowedErrors.pop();
    }
  });

  afterAll(async function() {
    await users.logout();
  });
});
