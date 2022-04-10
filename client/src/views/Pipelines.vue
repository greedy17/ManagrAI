<template>
  <div class="pipelines">
    <Modal
      v-if="modalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetNotes()
        }
      "
    >
      <div v-if="notes.length" class="modal-container">
        <div class="flex-row-spread">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="height: 1.75rem; margin-left: 0.5rem; margin-right: 0.25rem"
              alt=""
            />
            <h2>Notes</h2>
          </div>

          <img
            src="@/assets/images/closer.png"
            style="height: 1.5rem; margin-top: -0.5rem; margin-right: 0.5rem; cursor: pointer"
            @click="resetNotes"
            alt=""
          />
        </div>
        <section class="note-section" :key="i" v-for="(note, i) in notes">
          <p class="note-section__title">
            {{ note.saved_data__meeting_type ? note.saved_data__meeting_type + ':' : 'Untitled:' }}
          </p>
          <p class="note-section__body">{{ note.saved_data__meeting_comments }}</p>
          <p class="note-section__date">{{ formatDateTime(note.submission_date) }}</p>
        </section>
      </div>
      <div v-else class="modal-container">
        <div class="flex-row-spread">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="height: 1.5rem; margin-left: 0.5rem; margin-right: 0.25rem"
              alt=""
            />
            <h2>Notes</h2>
          </div>
          <img
            src="@/assets/images/closer.png"
            style="height: 1.75rem; margin-top: -0.5rem; margin-right: 0.5rem; cursor: pointer"
            @click="resetNotes"
            alt=""
          />
        </div>
        <section class="note-section">
          <p class="note-section__title">No notes for this opportunity</p>
        </section>
      </div>
    </Modal>
    <Modal
      v-if="addOppModalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetAddOpp()
        }
      "
    >
      <div class="opp-modal-container">
        <div class="flex-row-spread header">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="height: 1.75rem; margin-left: 0.5rem; margin-right: 0.25rem"
              alt=""
            />
            <h2>Create Opportunity</h2>
          </div>

          <img
            src="@/assets/images/clear.png"
            class="invert"
            style="height: 1.25rem; margin-top: -1rem; margin-right: 0.75rem; cursor: pointer"
            @click="resetAddOpp"
            alt=""
          />
        </div>
        <div class="opp-modal">
          <section :key="field.id" v-for="field in createOppForm">
            <div
              v-if="
                field.dataType === 'TextArea' ||
                (field.dataType === 'String' && field.apiName === 'NextStep')
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <textarea
                id="user-input"
                ccols="30"
                rows="4"
                style="width: 30vw; border-radius: 0.4rem"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div v-else-if="field.dataType === 'String'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="user-input"
                type="text"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>

            <div v-else-if="field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <select
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                id="user-input"
              >
                <option v-for="(option, i) in picklistQueryOpts[field.apiName]" :key="i">
                  <p>{{ option.label }}</p>
                </option>
              </select>
            </div>
            <div v-else-if="field.dataType === 'Date'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                type="date"
                id="user-input"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div v-else-if="field.dataType === 'DateTime'">
              <p>
                {{ field.referenceDisplayLabel }}
              </p>
              <input
                type="datetime-local"
                id="start"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div
              v-else-if="
                field.dataType === 'Phone' ||
                field.dataType === 'Double' ||
                field.dataType === 'Currency'
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="user-input"
                type="number"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div v-else-if="apiName === 'OwnerId'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <select
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                id="user-input"
              >
                <option value="" disabled selected hidden>{{ currentVals[field.apiName] }}</option>
                <option
                  :value="
                    user.salesforce_account_ref ? user.salesforce_account_ref.salesforce_id : ''
                  "
                  v-for="(user, i) in allUsers"
                  :key="i"
                >
                  <p>{{ user.full_name }}</p>
                </option>
              </select>
            </div>

            <div v-else-if="apiName === 'AccountId'">
              <p>{{ field.referenceDisplayLabel }}:</p>

              <select
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                id="user-input"
              >
                <option value="" disabled selected hidden>{{ currentVals[field.apiName] }}</option>
                <option
                  :value="account.integration_id"
                  v-for="(account, i) in allAccounts"
                  :key="i"
                >
                  <p>{{ account.name }}</p>
                </option>
              </select>
            </div>
          </section>
        </div>
        <div class="flex-end">
          <button class="add-button" @click="createResource">Create Opportunity</button>
          <p @click="resetAddOpp" class="cancel">Cancel</p>
        </div>
      </div>
    </Modal>
    <Modal
      v-if="editOpModalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetEdit()
        }
      "
    >
      <div class="opp-modal-container">
        <div class="flex-row-spread header">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="height: 1.75rem; margin-left: 0.5rem; margin-right: 0.25rem"
              alt=""
            />
            <h2>Update Opportunity</h2>
          </div>
          <img
            src="@/assets/images/closer.png"
            style="height: 1.5rem; margin-top: -1rem; margin-right: 0.75rem; cursor: pointer"
            @click="resetEdit"
            alt=""
          />
        </div>
        <div class="opp-modal">
          <section :key="field.id" v-for="field in oppFormCopy">
            <div v-if="field.apiName === 'meeting_type'">
              <p>Note Title:</p>
              <textarea
                id="user-input"
                cols="30"
                rows="2"
                style="width: 29.5vw; border-radius: 0.2rem"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div v-else-if="field.apiName === 'meeting_comments'">
              <p>Notes:</p>
              <textarea
                id="user-input"
                ccols="30"
                rows="4"
                style="width: 29.5vw; border-radius: 0.2rem"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div
              v-else-if="
                field.dataType === 'TextArea' || (field.length > 250 && field.dataType === 'String')
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <textarea
                id="user-input"
                ccols="30"
                rows="4"
                :placeholder="currentVals[field.apiName]"
                style="width: 29.5vw; border-radius: 0.4rem; padding: 7px"
                v-model="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div
              v-else-if="
                (field.dataType === 'String' && field.apiName !== 'meeting_type') ||
                (field.dataType === 'String' && field.apiName !== 'meeting_comments') ||
                (field.dataType === 'String' && field.apiName !== 'NextStep')
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="user-input"
                type="text"
                :placeholder="currentVals[field.apiName]"
                v-model="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div v-else-if="field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <select
                v-model="currentVals[field.apiName]"
                @input="
                  ;(value = $event.target.value),
                    setUpdateValues(
                      field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                      value,
                    )
                "
                id="user-input"
              >
                <option value="" disabled selected hidden>{{ currentVals[field.apiName] }}</option>
                <option v-for="(option, i) in picklistQueryOpts[field.apiName]" :key="i">
                  <p>{{ option.label }}</p>
                </option>
              </select>
            </div>
            <div v-else-if="field.dataType === 'Date'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                type="text"
                onfocus="(this.type='date')"
                onblur="(this.type='text')"
                :placeholder="currentVals[field.apiName]"
                v-model="currentVals[field.apiName]"
                id="user-input"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div v-else-if="field.dataType === 'DateTime'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                type="datetime-local"
                id="start"
                v-model="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div
              v-else-if="
                field.dataType === 'Phone' ||
                field.dataType === 'Double' ||
                field.dataType === 'Currency'
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="user-input"
                type="number"
                v-model="currentVals[field.apiName]"
                :placeholder="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>

            <div v-else-if="field.apiName === 'OwnerId'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <select
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                id="user-input"
              >
                <option value="" disabled selected hidden>{{ currentVals[field.apiName] }}</option>
                <option
                  :value="
                    user.salesforce_account_ref ? user.salesforce_account_ref.salesforce_id : ''
                  "
                  v-for="(user, i) in allUsers"
                  :key="i"
                >
                  <p>{{ user.full_name }}</p>
                </option>
              </select>
            </div>

            <div v-else-if="field.apiName === 'AccountId'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <select
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                id="user-input"
              >
                <option value="" disabled selected hidden>{{ currentVals[field.apiName] }}</option>
                <option
                  :value="account.integration_id"
                  v-for="(account, i) in allAccounts"
                  :key="i"
                >
                  <p>{{ account.name }}</p>
                </option>
              </select>
            </div>
          </section>
        </div>
        <div class="flex-end-opp">
          <div style="display: flex; align-items: center">
            <button @click="updateResource()" class="add-button__">Update</button>
            <p @click="resetEdit" class="cancel">Cancel</p>
          </div>
        </div>
      </div>
    </Modal>
    <div ref="pipelines" v-if="!loading">
      <section class="flex-row-spread">
        <div v-if="!workflowCheckList.length && !primaryCheckList.length" class="flex-row">
          <button @click.stop="showList = !showList" class="select-btn">
            {{ currentList }}
            <img
              v-if="!showList"
              style="height: 1rem; margin-left: 0.5rem"
              src="@/assets/images/rightArrow.png"
              alt=""
            />
            <img
              v-else
              style="height: 1rem; margin-left: 0.5rem"
              src="@/assets/images/downArrow.png"
              alt=""
            />
          </button>
          <div v-outside-click="closeListSelect" v-show="showList" class="list-section">
            <div class="list-section__title flex-row-spread">
              <p>{{ currentList }}</p>
              <!-- <img
                @click="showList = !showList"
                class="exit"
                src="@/assets/images/close.png"
                alt=""
              /> -->
            </div>
            <p @click="showPopularList = !showPopularList" class="list-section__sub-title">
              Standard Lists
              <img v-if="showPopularList" src="@/assets/images/downArrow.png" alt="" /><img
                v-else
                src="@/assets/images/rightArrow.png"
                alt=""
              />
            </p>
            <button v-if="showPopularList" @click="allOpportunities" class="list-button">
              All Opportunities
              <span class="filter" v-if="currentList === 'AllOpportunities'"> active</span>
            </button>
            <button v-if="showPopularList" @click="closeDatesThisMonth" class="list-button">
              Closing this month
              <span class="filter" v-if="currentList === 'Closing this month'"> active</span>
            </button>
            <button v-if="showPopularList" @click="closeDatesNextMonth" class="list-button">
              Closing next month
              <span class="filter" v-if="currentList === 'Closing next month'"> active</span>
            </button>
            <p @click="showMeetingList = !showMeetingList" class="list-section__sub-title">
              Meetings
              <img v-if="showMeetingList" src="@/assets/images/downArrow.png" alt="" /><img
                v-else
                src="@/assets/images/rightArrow.png"
                alt=""
              />
            </p>
            <div style="width: 100%" v-if="showMeetingList">
              <button @click="selectMeeting('Today\'s meetings')" class="list-button">
                Today's meetings
                <span class="filter" v-if="currentList === 'Today\'s meetings'"> active</span>
              </button>
            </div>
            <p @click="showWorkflowList = !showWorkflowList" class="list-section__sub-title">
              Workflows
              <img v-if="showWorkflowList" src="@/assets/images/downArrow.png" alt="" /><img
                v-else
                src="@/assets/images/rightArrow.png"
                alt=""
              />
            </p>
            <div style="width: 100%" v-if="showWorkflowList">
              <button
                :key="i"
                v-for="(template, i) in templates.list"
                @click="selectList(template.title, template.id)"
                class="list-button"
              >
                {{ template.title }}
                <span class="filter" v-if="currentList === template.title"> active</span>
              </button>
            </div>
          </div>

          <div
            v-for="(filter, i) in activeFilters"
            :key="i"
            @mouseenter="hoveredIndex = i"
            @mouseleave="hoveredIndex = null"
            class="main"
          >
            <strong style="font-size: 14px">{{ filter }}</strong>
            <small style="font-weight: 400px; margin-left: 0.2rem">{{ currentOperators[i] }}</small>
            <small style="margin-left: 0.2rem">{{ filterValues[i] }}</small>
            <span v-if="hoveredIndex === i" class="selected-filters__close"
              ><img src="@/assets/images/close.png" @click="removeFilter(filter, i)" alt=""
            /></span>
          </div>

          <section v-if="filterSelected" style="position: relative">
            <main class="main__before">
              <small
                ><strong>{{ currentFilter }}</strong></small
              >
              <small style="margin-left: 0.2rem">{{ currentOperators[-1] }}</small>
            </main>
            <div>
              <FilterSelection
                @filter-added="applyFilter"
                @operator-selected="addOperator"
                @value-selected="valueSelected"
                @close-selection="closeFilterSelection"
                :type="filterType"
                :filterName="currentFilter"
                :dropdowns="picklistQueryOpts"
                :apiName="filterApiName"
                :accounts="allAccounts"
                :owners="allUsers"
              />
            </div>
          </section>

          <section style="position: relative">
            <button
              v-if="activeFilters.length < 4 && !selectedMeeting"
              @click.stop="addingFilter"
              class="add-filter-button"
            >
              <img
                src="@/assets/images/plusOne.png"
                style="height: 0.8rem; margin-right: 0.25rem"
                alt=""
              />Add filter
            </button>
            <div v-outside-click="closeFilters" v-if="filtering">
              <Filters @select-filter="selectFilter" :filterFields="filterFields" />
            </div>
          </section>
        </div>
        <div v-else>
          <div v-if="!updatingOpps" class="bulk-action">
            <div v-if="!closeDateSelected && !advanceStageSelected && !forecastSelected">
              <!-- <p class="bulk-action__title">Select Update or<span class="cancel">cancel</span></p> -->
              <div class="flex-row">
                <button @click="closeDateSelected = !closeDateSelected" class="select-btn">
                  Push Close Date
                  <img
                    src="@/assets/images/date.png"
                    style="height: 1.25rem; margin-left: 0.25rem"
                    alt=""
                  />
                </button>
                <button @click="advanceStageSelected = !advanceStageSelected" class="select-btn">
                  Advance Stage
                  <img
                    src="@/assets/images/stairs.png"
                    style="height: 1.25rem; margin-left: 0.25rem"
                    alt=""
                  />
                </button>
                <button @click="forecastSelected = !forecastSelected" class="select-btn">
                  Change Forecast
                  <img
                    src="@/assets/images/monetary.png"
                    style="height: 1.1rem; width: 1.35rem; margin-left: 0.25rem"
                    alt=""
                  />
                </button>
              </div>
            </div>
            <div class="flex-row-pad" v-if="closeDateSelected">
              <p style="font-size: 14px">How many days ?:</p>
              <input class="number-input" v-model="daysForward" type="number" />
              <button :disabled="!daysForward" class="add-button" @click="pushCloseDate">
                Push Close Date
              </button>
            </div>
            <div class="flex-row-pad" v-if="advanceStageSelected">
              <p style="font-size: 14px">Select Stage:</p>
              <select
                style="margin-left: 0.5rem; margin-right: 0.5rem"
                @input=";(value = $event.target.value), setStage(value)"
                id="update-input"
              >
                <option v-for="(stage, i) in allStages" :key="i" :value="stage.value">
                  <p>{{ stage.label }}</p>
                </option>
              </select>
              <button @click="advanceStage()" class="add-button">Advance Stage</button>
            </div>
            <div class="flex-row-pad" v-if="forecastSelected">
              <p style="font-size: 14px">Select Forecast:</p>
              <select
                style="margin-left: 0.5rem; margin-right: 0.5rem"
                @input=";(value = $event.target.value), setForecast(value)"
                id="update-input"
              >
                <option v-for="(forecast, i) in allForecasts" :key="i" :value="forecast.value">
                  <p>{{ forecast.label }}</p>
                </option>
              </select>
              <button @click="changeForecast(currentCheckList)" class="add-button">
                Change Forecast
              </button>
            </div>
          </div>
          <div class="bulk-action" v-else>
            <SkeletonBox width="400px" height="22px" />
          </div>
        </div>
        <div class="flex-row">
          <div v-if="!selectedWorkflow" class="search-bar">
            <input type="search" v-model="filterText" placeholder="search" />
            <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
          </div>
          <div v-else class="search-bar">
            <input type="search" v-model="workflowFilterText" placeholder="search" />
            <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
          </div>
          <button @click="createOppInstance()" class="add-button">
            <img src="@/assets/images/plusOne.png" style="height: 1rem" alt="" />
            Create Opportunity
          </button>
          <button @click="manualSync" class="select-btn">
            <img src="@/assets/images/refresh.png" class="invert" style="height: 1.15rem" alt="" />
          </button>
        </div>
      </section>
      <div class="results">
        <h6 style="color: #9b9b9b">
          {{ currentList }}:
          <span>{{
            selectedWorkflow
              ? currentWorkflow.length
              : selectedMeeting
              ? meetings.length
              : allOpps.length
          }}</span>
        </h6>
      </div>
      <!-- <p @click="tester">test</p> -->
      <section
        v-show="!selectedWorkflow && !selectedMeeting && !loadingWorkflows"
        class="table-section"
      >
        <div class="table">
          <PipelineHeader
            :oppFields="oppFields"
            @check-all="onCheckAll"
            @sort-opps="sortOpps"
            @set-opps="setOpps"
            @sort-opps-reverse="sortOppsReverse"
            :allSelected="allSelected"
          />
          <PipelineTableRow
            ref="pipelineTableChild"
            :key="i"
            v-for="(opp, i) in allOppsFiltered"
            @create-form="createFormInstance(opp.id)"
            @get-notes="getNotes(opp.id)"
            @checked-box="selectPrimaryCheckbox(opp.id)"
            :opp="opp"
            :index="i"
            :oppFields="oppFields"
            :primaryCheckList="primaryCheckList"
            :updateList="updateList"
            :stageData="newStage"
            :closeDateData="daysForward"
            :ForecastCategoryNameData="newForecast"
          />
        </div>
      </section>
      <section
        v-if="
          selectedWorkflow && currentWorkflow.length > 0 && !selectedMeeting && !loadingWorkflows
        "
        class="table-section"
      >
        <div class="table">
          <WorkflowHeader
            :oppFields="oppFields"
            @check-all="onCheckAllWorkflows"
            :allWorkflowsSelected="allWorkflowsSelected"
            @sort-opps-workflows="sortWorkflows"
            @sort-opps-reverse-workflows="sortWorkflowsReverse"
          />
          <WorkflowRow
            :key="i"
            ref="workflowTableChild"
            v-for="(workflow, i) in filteredWorkflows"
            @create-form="createFormInstance(workflow.id)"
            @get-notes="getNotes(workflow.id)"
            @checked-box="selectWorkflowCheckbox(workflow.id)"
            :workflow="workflow"
            :index="i + 1 * 1000"
            :oppFields="oppFields"
            :workflowCheckList="workflowCheckList"
            :updateWorkflowList="updateList"
            :stageData="newStage"
            :closeDateData="daysForward"
            :ForecastCategoryNameData="newForecast"
          />
        </div>
      </section>
      <section style="min-height: 74vh" v-if="selectedMeeting" class="table-section">
        <div class="table">
          <MeetingWorkflowHeader />
          <MeetingWorkflow
            v-for="(meeting, i) in meetings"
            :key="i"
            :meeting="meeting.meeting_ref"
            :resourceId="meeting.resource_id"
            :allOpps="allOpps"
          />
        </div>
      </section>
      <section
        v-if="
          currentWorkflow && currentWorkflow.length < 1 && selectedWorkflow && !loadingWorkflows
        "
        class="empty-table-section"
      >
        <div>
          <div class="empty-table">
            <div class="table-row">
              <div class="flex-row table-cell-header">
                <h5 style="margin-left: 1rem">No results for the {{ currentList }} workflow.</h5>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section v-if="loadingWorkflows" class="empty-table-section">
        <div>
          <PipelineLoader />
        </div>
      </section>
    </div>
    <div v-if="loading">
      <Loader loaderText="Pulling in your latest Salesforce data" />
    </div>
  </div>
</template>
<script>
import { SObjects, SObjectPicklist, MeetingWorkflows } from '@/services/salesforce'
import AlertTemplate from '@/services/alerts/'
import CollectionManager from '@/services/collectionManager'
import SlackOAuth from '@/services/slack'
import PipelineNameSection from '@/components/PipelineNameSection'
import PipelineField from '@/components/PipelineField'
import PipelineTableRow from '@/components/PipelineTableRow'
import PipelineHeader from '@/components/PipelineHeader'
import User from '@/services/users'
import WorkflowRow from '@/components/WorkflowRow'
import WorkflowHeader from '@/components/WorkflowHeader'
import Loader from '@/components/Loader'
// import MeetikngWorkflowHeader from '@/components/MeetingWorkflowHeader'
// import MeetingWorkflow from '@/components/MeetingWorkflow'

export default {
  name: 'Pipelines',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    SkeletonBox: () => import(/* webpackPrefetch: true */ '@/components/SkeletonBox'),
    PipelineNameSection,
    PipelineField,
    PipelineTableRow,
    PipelineHeader,
    WorkflowHeader,
    WorkflowRow,
    Loader,
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
    // Loader: () => import(/* webpackPrefetch: true */ '@/components/Loader'),
    Filters: () => import(/* webpackPrefetch: true */ '@/components/Filters'),
    FilterSelection: () => import(/* webpackPrefetch: true */ '@/components/FilterSelection'),
    MeetingWorkflowHeader: () =>
      import(/* webpackPrefetch: true */ '@/components/MeetingWorkflowHeader'),
    MeetingWorkflow: () => import(/* webpackPrefetch: true */ '@/components/MeetingWorkflow'),
  },
  data() {
    return {
      key: 0,
      updatingOpps: false,
      oppInstanceId: null,
      oppId: null,
      primaryCheckList: [],
      workflowCheckList: [],
      allSelected: false,
      allWorkflowsSelected: false,
      updateList: [],
      recapList: [],
      currentVals: [],
      closeDateSelected: false,
      advanceStageSelected: false,
      forecastSelected: false,
      selection: false,
      allStages: [],
      allForecasts: [],
      newStage: null,
      newForecast: null,
      originalList: null,
      daysForward: null,
      allOpps: null,
      loading: false,
      loadingWorkflows: false,
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
      users: CollectionManager.create({ ModelClass: User }),
      currentWorkflow: null,
      selectedWorkflow: false,
      modalOpen: false,
      editOpModalOpen: false,
      addOppModalOpen: false,
      refreshId: null,
      filterText: '',
      workflowFilterText: '',
      currentList: 'All Opportunities',
      alertInstanceId: null,
      showList: false,
      showWorkflowList: true,
      showPopularList: true,
      notes: [],
      updateOppForm: null,
      oppFormCopy: null,
      createOppForm: null,
      oppFields: [],
      instanceId: null,
      formData: {},
      noteTitle: '',
      noteInfo: '',
      picklistQueryOpts: {},
      instanceIds: [],
      allAccounts: null,
      allUsers: null,
      filtering: false,
      filterSelected: false,
      activeFilters: [],
      hoveredIndex: null,
      currentFilter: null,
      operatorValue: 'EQUALS',
      currentOperators: ['equals'],
      filterType: null,
      filterFields: [],
      filterApiName: null,
      filterValues: [],
      filters: [],
      operatorsLength: 0,
      showMeetingList: true,
      selectedMeeting: false,
      meetings: null,
      ladFilter: {
        apiName: 'LastActivityDate',
        dataType: 'Date',
        referenceDisplayLabel: 'Last Activity Date',
      },
      lmdFilter: {
        apiName: 'LastModifiedDate',
        dataType: 'DateTime',
        referenceDisplayLabel: 'Last Modified Date',
      },
    }
  },
  computed: {
    currentCheckList() {
      if (this.primaryCheckList.length > 0) {
        return this.primaryCheckList
      } else if (this.workflowCheckList.length > 0) {
        return this.workflowCheckList
      } else {
        return []
      }
    },
    user() {
      return this.$store.state.user
    },
    allOppsFiltered() {
      return this.allOpps.filter((opp) =>
        opp.name.toLowerCase().includes(this.filterText.toLowerCase()),
      )
    },
    filteredWorkflows() {
      return this.currentWorkflow.filter((opp) =>
        opp.name.toLowerCase().includes(this.workflowFilterText.toLowerCase()),
      )
    },
    currentMonth() {
      let date = new Date()
      return date.getMonth()
    },
    currentDay() {
      let date = new Date()
      date = date
        .toLocaleDateString()
        .substring(date.toLocaleDateString().indexOf('/') + 1)
        .substring(0, date.toLocaleDateString().indexOf('/') + 1)
      if (date.includes('/')) {
        date = date.slice(0, -1)
        return '0' + date
      } else {
        return date
      }
    },
    syncDay() {
      if (this.$store.state.user.salesforceAccountRef.lastSyncTime) {
        return this.formatDateTime(this.$store.state.user.salesforceAccountRef.lastSyncTime)
          .substring(
            this.formatDateTime(this.$store.state.user.salesforceAccountRef.lastSyncTime).indexOf(
              '/',
            ) + 1,
          )
          .substring(
            0,
            this.formatDateTime(this.$store.state.user.salesforceAccountRef.lastSyncTime).indexOf(
              '/',
            ),
          )
      } else {
        return null
      }
    },
  },
  created() {
    this.getMeetingList()
    this.getObjects()
    this.templates.refresh()
    this.getAllForms()
    this.listStages()
    this.listForecast()
    this.resourceSync()
    this.getAccounts()
    this.getUsers()
  },
  watch: {
    primaryCheckList: 'closeAll',
    workflowCheckList: 'closeAll',
    updateList: {
      async handler(currList) {
        if (currList.length === 0 && this.recapList.length) {
          console.log(this.recapList.length)
          let bulk = true ? this.recapList.length > 1 : false
          try {
            const res = await SObjects.api.sendRecap(bulk, this.recapList)
            console.log(res)
          } catch (e) {
            console.log(e)
          } finally {
            this.recapList = []
          }
        }
      },
    },
  },
  methods: {
    tester() {
      console.log(this.allOpps)
    },
    async getMeetingList() {
      try {
        const res = await MeetingWorkflows.api.getMeetingList()
        this.meetings = res.results
      } catch (e) {
        console.log(e)
      } finally {
      }
    },
    selectMeeting(name) {
      this.currentList = name
      this.showList = false
      this.selectedMeeting = true
      this.selectedWorkflow = false
      this.closeFilterSelection()
    },
    setOpps() {
      User.api.getUser(this.user.id).then((response) => {
        this.$store.commit('UPDATE_USER', response)
      })
    },
    closeFilters() {
      this.filtering = false
    },
    closeFilterSelection() {
      this.filterSelected = false
      this.activeFilters = []
      this.operatorValue = 'EQUALS'
      this.currentOperator = ['equals']
      this.filterValues = []
      this.filters = []
    },
    closeListSelect() {
      this.showList = false
    },
    async getFilteredObjects(value) {
      this.loadingWorkflows = true
      if (value) {
        this.filters.push([this.operatorValue, this.filterApiName, value])
      }
      try {
        const res = await SObjects.api.getObjects('Opportunity', true, this.filters)
        if (this.selectedWorkflow) {
          this.allOpps = res.results
          this.updateWorkflowList(this.currentList, this.refreshId)
        } else if (this.currentList === 'Closing this month') {
          this.allOpps = res.results
          this.allOpps = this.allOpps.filter(
            (opp) => new Date(opp.secondary_data.CloseDate).getUTCMonth() == this.currentMonth,
          )
        } else if (this.currentList === 'Closing next month') {
          this.allOpps = res.results
          this.allOpps = this.allOpps.filter(
            (opp) => new Date(opp.secondary_data.CloseDate).getUTCMonth() == this.currentMonth + 1,
          )
        } else {
          this.allOpps = res.results
        }
      } catch (e) {
        console.log(e)
      } finally {
        this.operatorValue = 'EQUALS'
        this.currentOperator = ['equals']
        this.loadingWorkflows = false
      }
    },
    addOperator(name) {
      this.operatorValue = name
      switch (name) {
        case 'EQUALS':
          this.currentOperators.length === 1
            ? (this.currentOperators = ['equals'])
            : this.currentOperators.push('equals')
          break
        case 'NOT_EQUALS':
          this.currentOperators.length === 1
            ? (this.currentOperators = ['not equals'])
            : this.currentOperators.push('not equals')
          break
        case 'GREATER_THAN':
          this.currentOperators.length === 1
            ? (this.currentOperators = ['greater than'])
            : this.currentOperators.push('greater than')
          break
        case 'GREATER_THAN_EQUALS':
          this.currentOperators.length === 1
            ? (this.currentOperators = ['greater or equal'])
            : this.currentOperators.push('greater or equal')
          break
        case 'LESS_THAN':
          this.currentOperators.length === 1
            ? (this.currentOperators = ['less than'])
            : this.currentOperators.push('less than')
          break
        case 'LESS_THAN_EQUALS':
          this.currentOperators.length === 1
            ? (this.currentOperators = ['less or equal'])
            : this.currentOperators.push('less or equal')
          break
        case 'CONTAINS':
          this.currentOperators.length === 1
            ? (this.currentOperators = ['contains'])
            : this.currentOperators.push('contains')
          break
        case 'RANGE':
          this.currentOperators.length === 1
            ? (this.currentOperators = ['range'])
            : this.currentOperators.push('range')
          break
        default:
          console.log('(0_o)')
      }
    },
    addingFilter() {
      if (this.filtering === true) {
        this.filtering = false
      } else {
        this.filtering = true
        this.filterSelected = false
      }
    },
    applyFilter(value) {
      this.updateFilterValue = value
      this.operatorsLength += 1
      if (this.currentOperators.length < this.operatorsLength) {
        this.currentOperators.push('equals')
      }
      this.getFilteredObjects(value)
      this.filterSelected = false
      this.activeFilters.push(this.currentFilter)
    },
    valueSelected(value, name) {
      let users = this.allUsers.filter((user) => user.salesforce_account_ref)
      let user = null
      if (name === 'OwnerId') {
        user = users.filter((user) => user.salesforce_account_ref.salesforce_id === value)
        this.filterValues.push(user[0].full_name)
      } else if (name === 'AccountId') {
        let account = this.allAccounts.filter((account) => account.integration_id === value)
        this.filterValues.push(account[0].name)
      } else {
        this.filterValues.push(value)
      }
    },
    selectFilter(name, type, label) {
      this.filtering = !this.filtering
      this.filterApiName = name
      this.filterType = type
      this.currentFilter = label
      this.filterSelected = true
    },
    removeFilter(name, index) {
      this.activeFilters.splice(index, 1)
      this.filters.splice(index, 1)
      this.filterValues.splice(index, 1)
      this.currentOperators.splice(index, 1)
      this.getFilteredObjects()
      this.filterSelected = false
      this.currentFilter = null
      this.operatorValue = 'EQUALS'
      this.filterApiName = null
    },
    capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1)
    },
    camelize(str) {
      return str.replace(/(?:^\w|[A-Z]|\b\w|\s+)/g, function (match, index) {
        if (+match === 0) return ''
        return index === 0 ? match.toLowerCase() : match.toUpperCase()
      })
    },
    sortOpps(dT, field, apiName) {
      let newField = this.capitalizeFirstLetter(this.camelize(field))

      if (field === 'Stage') {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data']['StageName']
          const nameB = b['secondary_data']['StageName']
          if (nameA < nameB) {
            return -1
          }
          if (nameA > nameB) {
            return 1
          }
          return 0
        })
      } else if (dT === 'TextArea') {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${newField}`]
          const nameB = b['secondary_data'][`${newField}`]
          if (nameA.length < nameB.length) {
            return -1
          }
          if (nameA.length > nameB.length) {
            return 1
          }
          return 0
        })
      } else if (apiName.includes('__c')) {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${apiName}`]
          const nameB = b['secondary_data'][`${apiName}`]
          if (nameA < nameB) {
            return -1
          }
          if (nameA > nameB) {
            return 1
          }
          return 0
        })
      } else {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${newField}`]
          const nameB = b['secondary_data'][`${newField}`]
          if (nameA < nameB) {
            return -1
          }
          if (nameA > nameB) {
            return 1
          }
          return 0
        })
      }
    },
    sortOppsReverse(dT, field, apiName) {
      let newField = this.capitalizeFirstLetter(this.camelize(field))

      if (field === 'Stage') {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data']['StageName']
          const nameB = b['secondary_data']['StageName']
          if (nameA < nameB) {
            return 1
          }
          if (nameA > nameB) {
            return -1
          }
          return 0
        })
      } else if (dT === 'TextArea') {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${newField}`]
          const nameB = b['secondary_data'][`${newField}`]
          if (nameA.length < nameB.length) {
            return 1
          }
          if (nameA.length > nameB.length) {
            return -1
          }
          return 0
        })
      } else if (apiName.includes('__c')) {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${apiName}`]
          const nameB = b['secondary_data'][`${apiName}`]
          if (nameA < nameB) {
            return 1
          }
          if (nameA > nameB) {
            return -1
          }
          return 0
        })
      } else {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${newField}`]
          const nameB = b['secondary_data'][`${newField}`]
          if (nameA < nameB) {
            return 1
          }
          if (nameA > nameB) {
            return -1
          }
          return 0
        })
      }
    },
    sortWorkflows(dT, field, apiName) {
      let newField = this.capitalizeFirstLetter(this.camelize(field))

      if (field === 'Stage') {
        this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
          const nameA = a['secondary_data']['StageName']
          const nameB = b['secondary_data']['StageName']
          if (nameA < nameB) {
            return -1
          }
          if (nameA > nameB) {
            return 1
          }
          return 0
        })
      } else if (dT === 'TextArea') {
        this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
          const nameA = a['secondary_data'][`${newField}`]
          const nameB = b['secondary_data'][`${newField}`]
          if (nameA.length < nameB.length) {
            return -1
          }
          if (nameA.length > nameB.length) {
            return 1
          }
          return 0
        })
      } else if (apiName.includes('__c')) {
        this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
          const nameA = a['secondary_data'][`${apiName}`]
          const nameB = b['secondary_data'][`${apiName}`]
          if (nameA < nameB) {
            return -1
          }
          if (nameA > nameB) {
            return 1
          }
          return 0
        })
      } else {
        this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
          const nameA = a['secondary_data'][`${newField}`]
          const nameB = b['secondary_data'][`${newField}`]
          if (nameA < nameB) {
            return -1
          }
          if (nameA > nameB) {
            return 1
          }
          return 0
        })
      }
    },
    sortWorkflowsReverse(dT, field, apiName) {
      let newField = this.capitalizeFirstLetter(this.camelize(field))

      if (field === 'Stage') {
        this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
          const nameA = a['secondary_data']['StageName']
          const nameB = b['secondary_data']['StageName']
          if (nameA < nameB) {
            return 1
          }
          if (nameA > nameB) {
            return -1
          }
          return 0
        })
      } else if (dT === 'TextArea') {
        this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
          const nameA = a['secondary_data'][`${newField}`]
          const nameB = b['secondary_data'][`${newField}`]
          if (nameA.length < nameB.length) {
            return 1
          }
          if (nameA.length > nameB.length) {
            return -1
          }
          return 0
        })
      } else if (apiName.includes('__c')) {
        this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
          const nameA = a['secondary_data'][`${apiName}`]
          const nameB = b['secondary_data'][`${apiName}`]
          if (nameA < nameB) {
            return 1
          }
          if (nameA > nameB) {
            return -1
          }
          return 0
        })
      } else {
        this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
          const nameA = a['secondary_data'][`${newField}`]
          const nameB = b['secondary_data'][`${newField}`]
          if (nameA < nameB) {
            return 1
          }
          if (nameA > nameB) {
            return -1
          }
          return 0
        })
      }
    },
    selectPrimaryCheckbox(id) {
      if (this.primaryCheckList.includes(id)) {
        this.primaryCheckList = this.primaryCheckList.filter((opp) => opp !== id)
      } else {
        this.primaryCheckList.push(id)
      }
    },
    selectWorkflowCheckbox(id) {
      if (this.workflowCheckList.includes(id)) {
        this.workflowCheckList = this.workflowCheckList.filter((opp) => opp !== id)
      } else {
        this.workflowCheckList.push(id)
      }
    },
    closeAll() {
      if (this.primaryCheckList.length === 0 || this.workflowCheckList.length === 0) {
        this.closeDateSelected = false
        this.advanceStageSelected = false
        this.forecastSelected = false
      }
    },
    setStage(val) {
      this.newStage = val
    },
    setForecast(val) {
      this.newForecast = val
    },
    onCheckAll() {
      if (this.primaryCheckList.length < 1) {
        for (let i = 0; i < this.allOppsFiltered.length; i++) {
          this.primaryCheckList.push(this.allOppsFiltered[i].id)
        }
      } else if (
        this.primaryCheckList.length > 0 &&
        this.primaryCheckList.length < this.allOppsFiltered.length
      ) {
        for (let i = 0; i < this.allOppsFiltered.length; i++) {
          !this.primaryCheckList.includes(this.allOppsFiltered[i].id)
            ? this.primaryCheckList.push(this.allOppsFiltered[i].id)
            : (this.primaryCheckList = this.primaryCheckList)
        }
      } else {
        this.primaryCheckList = []
      }
    },
    onCheckAllWorkflows() {
      if (this.workflowCheckList.length < 1) {
        for (let i = 0; i < this.filteredWorkflows.length; i++) {
          this.workflowCheckList.push(this.filteredWorkflows[i].id)
        }
      } else if (
        this.workflowCheckList.length > 0 &&
        this.workflowCheckList.length < this.filteredWorkflows.length
      ) {
        for (let i = 0; i < this.filteredWorkflows.length; i++) {
          !this.workflowCheckList.includes(this.filteredWorkflows[i].id)
            ? this.workflowCheckList.push(this.filteredWorkflows[i].id)
            : (this.workflowCheckList = this.workflowCheckList)
        }
      } else {
        this.workflowCheckList = []
      }
    },
    async listPicklists(type, query_params) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)
        this.picklistQueryOpts[type] = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    async listStages() {
      try {
        const res = await SObjectPicklist.api.listPicklists({
          salesforceObject: 'Opportunity',
          picklistFor: 'StageName',
        })
        this.allStages = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    async listForecast() {
      try {
        const res = await SObjectPicklist.api.listPicklists({
          salesforceObject: 'Opportunity',
          picklistFor: 'ForecastCategoryName',
        })
        this.allForecasts = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    async updateWorkflow(id) {
      try {
        await AlertTemplate.api.runAlertTemplateNow(id)
      } catch (e) {
        console.log(e)
      } finally {
      }
    },
    resetNotes() {
      this.modalOpen = !this.modalOpen
      this.notes = []
    },
    resetEdit() {
      this.editOpModalOpen = !this.editOpModalOpen
    },
    resetAddOpp() {
      this.addOppModalOpen = !this.addOppModalOpen
    },
    async createFormInstance(id, alertInstanceId = null) {
      this.currentVals = []
      this.editOpModalOpen = true
      this.alertInstanceId = alertInstanceId
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Opportunity',
          formType: 'UPDATE',
          resourceId: id,
        })
        this.currentVals = res.current_values
        this.oppId = id
        this.instanceId = res.form_id
      } catch (e) {
        console.log(e)
      }
    },
    async createOppInstance() {
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Opportunity',
          formType: 'CREATE',
        })
        this.addOppModalOpen = true
        this.oppInstanceId = res.form_id
      } catch (e) {
        console.log(e)
      }
    },
    pushCloseDate() {
      if (this.selectedWorkflow) {
        for (let i = 0; i < this.$refs.workflowTableChild.length; i++) {
          this.$refs.workflowTableChild[i].onPushCloseDate()
          this.updateOpps()
          this.updateWorkflowList(this.currentList, this.refreshId)
        }
        this.workflowCheckList = []
      } else {
        for (let i = 0; i < this.$refs.pipelineTableChild.length; i++) {
          this.$refs.pipelineTableChild[i].onPushCloseDate()
          this.updateOpps()
        }
        this.primaryCheckList = []
      }
    },
    advanceStage() {
      if (this.selectedWorkflow) {
        for (let i = 0; i < this.$refs.workflowTableChild.length; i++) {
          this.$refs.workflowTableChild[i].onAdvanceStage()
          this.updateOpps()
          this.updateWorkflowList(this.currentList, this.refreshId)
        }
        this.workflowCheckList = []
      } else {
        for (let i = 0; i < this.$refs.pipelineTableChild.length; i++) {
          this.$refs.pipelineTableChild[i].onAdvanceStage()
          this.updateOpps()
        }
        this.primaryCheckList = []
      }
    },
    changeForecast() {
      if (this.selectedWorkflow) {
        for (let i = 0; i < this.$refs.workflowTableChild.length; i++) {
          this.$refs.workflowTableChild[i].onChangeForecast()
          this.updateOpps()
          this.updateWorkflowList(this.currentList, this.refreshId)
        }
        this.workflowCheckList = []
      } else {
        for (let i = 0; i < this.$refs.pipelineTableChild.length; i++) {
          this.$refs.pipelineTableChild[i].onChangeForecast()
          this.updateOpps()
        }
        this.primaryCheckList = []
      }
    },
    setUpdateValues(key, val) {
      if (val) {
        this.formData[key] = val
      }
    },
    async updateOpps() {
      try {
        let updatedRes = await SObjects.api.getObjects('Opportunity')
        this.allOpps = updatedRes.results
        this.originalList = updatedRes.results
      } catch (e) {
        console.log(e)
      }
    },
    async resourceSync() {
      if (this.currentDay !== this.syncDay) {
        this.loading = true
        try {
          const res = await SObjects.api.resourceSync()
        } catch (e) {
          console.log(e)
        } finally {
          this.getObjects()
          User.api.getUser(this.user.id).then((response) => {
            this.$store.commit('UPDATE_USER', response)
          })
          this.loading = false
          this.$Alert.alert({
            type: 'success',
            timeout: 3000,
            message: 'Daily Sync complete',
            sub: 'All fields reflect your current SFDC data',
          })
        }
      }
    },
    async manualSync() {
      this.loading = true
      try {
        const res = await SObjects.api.resourceSync()
      } catch (e) {
        console.log(e)
      } finally {
        this.getObjects()
        this.loading = false
        this.$Alert.alert({
          type: 'success',
          timeout: 3000,
          message: 'Sync complete',
          sub: 'All fields reflect your current SFDC data',
        })
      }
    },
    async updateResource() {
      this.updateList.push(this.oppId)
      this.editOpModalOpen = false
      try {
        const res = await SObjects.api
          .updateResource({
            form_id: this.instanceId,
            form_data: this.formData,
          })
          .then(async () => {
            let updatedRes = await SObjects.api.getObjects('Opportunity')
            this.allOpps = updatedRes.results
            this.originalList = updatedRes.results
          })
        this.updateList = []
        this.formData = {}
        this.$Alert.alert({
          type: 'success',
          timeout: 1000,
          message: 'Salesforce update successful!',
        })
        this.closeFilterSelection()
        if (this.selectedWorkflow) {
          this.updateWorkflowList(this.currentList, this.refreshId)
        } else if (this.currentList === 'Closing this month') {
          this.stillThisMonth()
        } else if (this.currentList === 'Closing next month') {
          this.stillNextMonth()
        }
      } catch (e) {
        console.log(e)
      }
    },
    async createResource() {
      this.addOppModalOpen = false
      try {
        const res = await SObjects.api
          .createResource({
            form_id: this.oppInstanceId,
            form_data: this.formData,
          })
          .then(async () => {
            let updatedRes = await SObjects.api.getObjects('Opportunity')
            this.allOpps = updatedRes.results
            this.originalList = updatedRes.results
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.$Alert.alert({
          type: 'success',
          timeout: 1000,
          message: 'Opportunity created successfully!',
        })
      }
      this.getAllForms()
    },
    async selectList(title, id) {
      this.loadingWorkflows = true
      this.allOpps = this.originalList
      this.selectedMeeting = false
      this.closeFilterSelection()
      this.showList = false
      this.refreshId = id
      this.currentList = title
      try {
        let res = await AlertTemplate.api.runAlertTemplateNow(id, {
          fromWorkflow: true,
        })
        this.currentWorkflow = this.allOpps.filter((opp) =>
          res.data.ids.includes(opp.integration_id),
        )
        if (this.currentWorkflow.length < 1) {
          this.updateWorkflow(id)
        }
      } catch (error) {
        console.log(error)
      } finally {
        this.selectedWorkflow = true
        this.loadingWorkflows = false
      }
    },
    async updateWorkflowList(title, id) {
      this.refreshId = id
      this.currentList = title
      try {
        let res = await AlertTemplate.api.runAlertTemplateNow(id, {
          fromWorkflow: true,
        })
        this.currentWorkflow = this.allOpps.filter((opp) =>
          res.data.ids.includes(opp.integration_id),
        )
      } catch (error) {
        console.log(error)
      } finally {
        this.selectedWorkflow = true
        this.showList = false
      }
    },
    async getAllForms() {
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()
        this.updateOppForm = res.filter(
          (obj) => obj.formType === 'UPDATE' && obj.resource === 'Opportunity',
        )
        this.createOppForm = res.filter(
          (obj) => obj.formType === 'CREATE' && obj.resource === 'Opportunity',
        )
        this.oppFormCopy = this.updateOppForm[0].fieldsRef
        this.createOppForm = this.createOppForm[0].fieldsRef
        for (let i = 0; i < this.oppFormCopy.length; i++) {
          if (
            this.oppFormCopy[i].dataType === 'Picklist' ||
            this.oppFormCopy[i].dataType === 'MultiPicklist'
          ) {
            this.picklistQueryOpts[this.oppFormCopy[i].apiName] = this.oppFormCopy[i].apiName
          } else if (this.oppFormCopy[i].dataType === 'Reference') {
            this.picklistQueryOpts[this.oppFormCopy[i].referenceDisplayLabel] =
              this.oppFormCopy[i].referenceDisplayLabel
          }
        }
        for (let i in this.picklistQueryOpts) {
          this.picklistQueryOpts[i] = this.listPicklists(i, { picklistFor: i })
        }
        this.filterFields = this.updateOppForm[0].fieldsRef.filter(
          (field) =>
            field.apiName !== 'meeting_type' &&
            field.apiName !== 'meeting_comments' &&
            !field.apiName.includes('__c'),
        )
        this.filterFields = [...this.filterFields, this.ladFilter, this.lmdFilter]
        this.oppFields = this.updateOppForm[0].fieldsRef.filter(
          (field) =>
            field.apiName !== 'meeting_type' &&
            field.apiName !== 'meeting_comments' &&
            field.apiName !== 'Name' &&
            field.apiName !== 'AccountId' &&
            field.apiName !== 'OwnerId',
        )
      } catch (error) {
        console.log(error)
      }
    },
    async getUsers() {
      try {
        const res = await SObjects.api.getObjects('User')
        this.allUsers = res.results
      } catch (e) {
        console.log(e)
      }
    },
    async getAccounts() {
      try {
        const res = await SObjects.api.getObjects('Account')
        this.allAccounts = res.results
      } catch (e) {
        console.log(e)
      }
    },
    async getObjects() {
      this.loading = true
      try {
        const res = await SObjects.api.getObjects('Opportunity')
        this.allOpps = res.results
        this.originalList = res.results
      } catch (e) {
        console.log(e)
      } finally {
        this.loading = false
      }
    },
    async getNotes(id) {
      try {
        const res = await SObjects.api.getNotes({
          resourceId: id,
        })
        this.modalOpen = true
        if (res.length) {
          for (let i = 0; i < res.length; i++) {
            this.notes.push(res[i])
            this.notes = this.notes.filter((note) => note.saved_data__meeting_comments !== null)
          }
        }
      } catch (e) {
        console.log(e)
      }
    },
    addOpp() {
      this.addOppModalOpen = true
    },
    closeDatesThisMonth() {
      this.allOpps = this.originalList
      this.selectedWorkflow = false
      this.selectedMeeting = false
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.secondary_data.CloseDate).getUTCMonth() == this.currentMonth,
      )
      this.currentList = 'Closing this month'
      this.showList = !this.showList
      this.closeFilterSelection()
    },
    stillThisMonth() {
      this.allOpps = this.originalList
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.secondary_data.CloseDate).getUTCMonth() == this.currentMonth,
      )
      this.currentList = 'Closing this month'
    },
    closeDatesNextMonth() {
      this.allOpps = this.originalList
      this.selectedWorkflow = false
      this.selectedMeeting = false
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.secondary_data.CloseDate).getUTCMonth() == this.currentMonth + 1,
      )
      this.currentList = 'Closing next month'
      this.showList = !this.showList
      this.closeFilterSelection()
    },
    stillNextMonth() {
      this.allOpps = this.originalList
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.secondary_data.CloseDate).getUTCMonth() == this.currentMonth + 1,
      )
      this.currentList = 'Closing next month'
    },
    allOpportunities() {
      this.selectedWorkflow = false
      this.selectedMeeting = false
      this.allOpps = this.originalList
      this.currentList = 'All Opportunities'
      this.showList = !this.showList
      this.closeFilterSelection()
    },
    formatDateTime(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      let newDate = input.replace(pattern, '$2/$3/$1')
      return newDate.split('T')[0]
    },
  },
}
</script>
<style lang="scss">
@import '@/styles/variables';
@import '@/styles/buttons';

.results {
  margin: 0;
  width: 100%;
  display: flex;
  padding-left: 1rem;
  margin-bottom: -1.25rem;
  margin-top: -0.75rem;
  justify-content: flex-start;
}
select {
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  background-color: #fafafa;
  height: 40px;
  width: 100%;
  background-image: url('../assets/images/dropdown.png');
  background-size: 1rem;
  background-position: 100%;
  background-repeat: no-repeat;
  border: 1px solid #ccc;
  padding-left: 0.75rem;
  border-radius: 0;
}
.select-btn {
  border: none;
  min-height: 4.5vh;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 1px 1px 2px $very-light-gray;
  border-radius: 0.25rem;
  background-color: white;
  cursor: pointer;
  color: $dark-green;
  letter-spacing: 0.2px;
  margin-right: 0.5rem;
  transition: all 0.25s;

  img {
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
  }
}
.select-btn:hover {
  transform: scale(1.02);
  box-shadow: 1px 2px 3px $very-light-gray;
}
input[type='checkbox']:checked + label::after {
  content: '';
  position: absolute;
  width: 1ex;
  height: 0.3ex;
  background: rgba(0, 0, 0, 0);
  top: 0.9ex;
  left: 0.4ex;
  border: 2px solid $dark-green;
  border-top: none;
  border-right: none;
  -webkit-transform: rotate(-45deg);
  -moz-transform: rotate(-45deg);
  -o-transform: rotate(-45deg);
  -ms-transform: rotate(-45deg);
  transform: rotate(-45deg);
}
input[type='checkbox'] {
  line-height: 2.1ex;
}
input[type='checkbox'] {
  position: absolute;
  left: -999em;
}
input[type='checkbox'] + label {
  position: relative;
  overflow: hidden;
  cursor: pointer;
}
input[type='checkbox'] + label::before {
  content: '';
  display: inline-block;
  vertical-align: -22%;
  height: 1.75ex;
  width: 1.75ex;
  background-color: white;
  border: 1px solid rgb(182, 180, 180);
  border-radius: 4px;
  margin-right: 0.5em;
}
input[type='date']::-webkit-datetime-edit-text,
input[type='date']::-webkit-datetime-edit-month-field,
input[type='date']::-webkit-datetime-edit-day-field,
input[type='date']::-webkit-datetime-edit-year-field {
  color: #888;
  cursor: pointer;
  padding-left: 0.5rem;
}
input {
  padding: 7px;
}
h3 {
  font-size: 22px;
}
.table-section {
  margin: 0;
  padding: 0;
  max-height: 76vh;
  overflow: scroll;
  margin-top: 0.5rem;
  border-radius: 5px;
  box-shadow: 2px 2px 20px 2px $soft-gray;
  background-color: $off-white;
}
.empty-table-section {
  height: 30vh;
  margin-top: 2rem;
  border-radius: 5px;
  box-shadow: 1px 1px 20px 1px $soft-gray;
  background-color: $off-white;
}
.table {
  display: table;
  overflow: scroll;
  width: 100vw;
}
.empty-table {
  display: table;
  width: 98vw;
}
.table-row {
  display: table-row;
}
.table-cell {
  display: table-cell;
  position: sticky;
  min-width: 12vw;
  background-color: $off-white;
  padding: 2vh 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  font-size: 13px;
}
.table-cell-wide {
  display: table-cell;
  position: sticky;
  min-width: 26vw;
  background-color: $off-white;
  padding: 2vh 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  font-size: 13px;
  overflow: scroll;
}
.table-cell:hover {
  cursor: text;
  background-color: white;
}
.modal-container {
  background-color: $white;
  overflow: hidden;
  width: 30vw;
  min-height: 60vh;
  align-items: center;
  border-radius: 0.3rem;
  padding: 0.25rem;
  box-shadow: 2px 2px 10px 2px $base-gray;
}
.close-button {
  border-radius: 50%;
  background-color: white;
  box-shadow: 1px 1px 1px 1px $very-light-gray;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: -1rem;
  padding: 0.25rem;
  cursor: pointer;
  img {
    filter: invert(80%);
  }
}
.opp-modal-container {
  overflow: hidden;
  background-color: white;
  min-height: 80vh;
  width: 34vw;
  align-items: center;
  border-radius: 0.6rem;
  padding: 1rem;
  box-shadow: 1px 3px 7px $base-gray;
}
.opp-modal {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  padding: 0.5rem;
  overflow-y: scroll;
  height: 56vh;
  border-radius: 0.25rem;
  border-bottom: 3px solid $white;
  color: $base-gray;
  font-size: 16px;
  letter-spacing: 0.75px;
  div {
    margin-right: 1rem;
  }
}
.note-section {
  padding: 0.5rem 1rem;
  margin-bottom: 0.25rem;
  background-color: white;
  border-bottom: 1px solid $soft-gray;
  overflow: scroll;
  &__title {
    font-size: 16px;
    font-weight: bold;
    color: $dark-green;
    letter-spacing: 1px;
  }
  &__body {
    color: $base-gray;
  }
  &__date {
    color: $mid-gray;
    font-size: 11px;
  }
}
.table-cell-checkbox {
  display: table-cell;
  padding: 2vh;
  width: 3.75vw;
  border: none;
  left: 0;
  position: sticky;
  z-index: 1;
  border-bottom: 1px solid $soft-gray;
  background-color: $off-white;
}
.table-cell-header {
  display: table-cell;
  padding: 1.25vh 3vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  border-radius: 2px;
  z-index: 2;
  top: 0;
  position: sticky;
  background-color: $off-white;
  font-weight: bold;
  font-size: 13px;
  letter-spacing: 0.5px;
  color: $base-gray;
}
.table-cell-header-wide {
  display: table-cell;
  padding: 0.25rem;
  padding: 1.25vh 2.5vh;
  min-width: 3rem;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  border-radius: 2px;
  z-index: 2;
  top: 0;
  position: sticky;
  background-color: $off-white;
  font-weight: bold;
  font-size: 13px;
  letter-spacing: 0.5px;
  color: $base-gray;
}
.limit-cell-height {
  max-height: 4rem;
  width: 110%;
  overflow: auto;
  direction: rtl;
  padding: 0px 0.25rem;
}
.centered {
  display: flex;
  justify-content: center;
  align-items: center;
}
.cell-name-header {
  display: table-cell;
  padding: 1.25vh 3vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  border-radius: 2px;
  z-index: 3;
  left: 3.5vw;
  top: 0;
  position: sticky;
  background-color: $off-white;
  font-weight: bold;
  font-size: 13px;
  letter-spacing: 0.5px;
  color: $base-gray;
}
.table-cell-checkbox-header {
  display: table-cell;
  padding: 1.25vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  z-index: 3;
  width: 4vw;
  top: 0;
  left: 0;
  position: sticky;
  background-color: $off-white;
}
.cell-name {
  background-color: white;
  color: $base-gray;
  letter-spacing: 0.25px;
  position: sticky;
  left: 3.5vw;
  z-index: 2;
}
input[type='search'] {
  border: none;
  background-color: $off-white;
  padding: 4px;
  margin: 0;
}
input[type='search']:focus {
  outline: none;
}
input[type='text']:focus {
  outline: none;
  cursor: text;
}
input[type='checkbox'] {
  cursor: pointer;
}
select {
  cursor: pointer;
}
option:not(:first-of-type) {
  color: black;
}
header,
section {
  margin: 0;
  padding: 0px;
}
.flex-row {
  // position: relative;
  display: flex;
  flex-direction: row;
  align-items: center;
}
.flex-row-pad {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0rem 0.5rem;
}
.bulk-action {
  margin: 0.75rem 0rem;
  &__title {
    font-weight: bold;
    font-size: 14px;
    color: $base-gray;
    margin-left: 0.5rem;
  }
}

.flex-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.pipelines {
  padding-top: 5rem;
  color: $base-gray;
}
.invert {
  filter: invert(80%);
}
.add-button:disabled {
  display: flex;
  align-items: center;
  border: none;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $gray;
  cursor: text;
  color: white;
}
.add-button:disabled:hover {
  transform: none;
}
.add-filter-button {
  display: flex;
  align-items: center;
  border: none;
  height: 4.5vh;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: transparent;
  cursor: pointer;
  color: $dark-green;

  img {
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
  }
}
.add-button {
  display: flex;
  align-items: center;
  border: none;
  height: 4.5vh;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
}
.add-button__ {
  display: flex;
  align-items: center;
  border: none;
  min-height: 4.5vh;
  padding: 0.5rem 1rem;
  font-size: 16px;
  border-radius: 0.2rem;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
}
.soon-button {
  display: flex;
  align-items: center;
  border: none;
  height: 4.5vh;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $very-light-gray;
  cursor: text;
  color: $base-gray;
  font-weight: bold;
  font-size: 11px;

  img {
    filter: invert(80%);
  }
}

.add-button:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
}
.add-button__:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
}
.search-bar {
  height: 4.5vh;
  background-color: $off-white;
  box-shadow: 1px 1px 1px $very-light-gray;
  border: 1px solid $soft-gray;
  display: flex;
  align-items: center;
  padding: 2px;
  border-radius: 5px;
  margin-right: 0.5rem;
}
#update-input {
  border: none;
  border-radius: 0.25rem;
  box-shadow: 1px 1px 1px 1px $very-light-gray;
  background-color: white;
  min-height: 2.5rem;
  width: 14vw;
}
#user-input {
  border: 1px solid $theme-gray;
  border-radius: 0.3rem;
  background-color: white;
  min-height: 2.5rem;
  width: 14vw;
}
#user-input:focus {
  outline: 1px solid $lighter-green;
}
.number-input {
  background-color: $off-white;
  box-shadow: 1px 1px 1px $gray;
  border: 2px solid $light-orange-gray;
  border-radius: 5px;
  min-height: 4vh;
  margin-right: 1rem;
  margin-left: 0.5rem;
  width: 6vw;
}
#update-input:focus,
.number-input:focus {
  outline: 1px solid $lighter-green;
}
.loader {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60vh;
  filter: invert(99%);
}
.invert {
  filter: invert(99%);
}
.gray {
  filter: invert(44%);
}
.header {
  font-size: 18px;
  padding: 0;
  letter-spacing: 0.5px;
  margin-bottom: 0.2rem;
}
.selected-filters {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  max-width: 50vw;
  margin-top: 1rem;
  overflow: scroll;
  padding: 0;

  &__close {
    background-color: $white-green;
    backdrop-filter: blur(0.5px);
    opacity: 4;
    border: none;
    margin-left: -1rem;
    padding: 0rem 0.1rem 0rem 0.1rem;
    min-height: 3vh;

    img {
      height: 0.9rem;
      filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
    }
  }
}
.main {
  border: none;
  height: 5vh;
  max-width: 10vw;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $white-green;
  cursor: pointer;
  color: $dark-green;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.main:hover {
  overflow: visible;
  white-space: normal;
  max-width: none;
}

main > span {
  display: none;
}
main:hover > span {
  display: block;
}
.main__before {
  display: flex;
  align-items: center;
  flex-direction: row;
  border: none;
  min-height: 5vh;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  font-weight: bold;
}
.list-section {
  z-index: 4;
  position: absolute;
  top: 20vh;
  left: 1rem;
  border-radius: 0.33rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $white;
  min-width: 20vw;
  max-height: 70vh;
  overflow: scroll;
  margin-right: 0.5rem;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
  &__title {
    position: sticky;
    top: 0;
    z-index: 5;
    color: $base-gray;
    background-color: $off-white;
    letter-spacing: 0.25px;
    padding-left: 0.75rem;
    font-weight: bold;
    font-size: 15px;
    width: 100%;
  }
  &__sub-title {
    font-size: 12px;
    font-weight: bold;
    display: flex;
    align-items: center;
    margin-left: 0.75rem;
    color: $base-gray;
    cursor: pointer;
    width: 100%;
    img {
      margin: 2px 0px 0px 3px;
      height: 0.75rem;
      filter: invert(70%);
    }
  }
}
.list-button {
  display: flex;
  align-items: center;
  height: 4.5vh;
  width: 100%;
  background-color: transparent;
  border: none;
  padding: 0.75rem;
  border-radius: 0.2rem;
  color: $mid-gray;
  cursor: pointer;
  font-size: 11px;
  font-weight: bold;
}
.list-button:hover {
  color: $dark-green;
  background-color: $off-white;
}
.filter {
  color: #199e54;
  margin-left: 0.2rem;
}
.exit {
  padding-right: 0.75rem;
  margin-top: -0.5rem;
  height: 1rem;
  cursor: pointer;
}
.cancel {
  color: $dark-green;
  font-weight: bold;
  margin-left: 1rem;
  cursor: pointer;
}
.flex-end {
  width: 100%;
  padding: 2rem 0.25rem;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
.flex-end-opp {
  width: 100%;
  padding: 0.5rem 1.5rem;
  height: 5rem;
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
}
textarea {
  resize: none;
}
</style>