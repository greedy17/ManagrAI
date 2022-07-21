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
      <div v-if="notes.length" class="modal-container rel">
        <div class="flex-row-spread sticky border-bottom">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h4>Notes</h4>
          </div>

          <div class="flex-row">
            <small class="note-border">Total: {{ notesLength }}</small>
            <small class="note-border light-green-bg"
              >Most recent: {{ formatMostRecent(notes[0].submission_date) }} days</small
            >
            <small class="note-border"
              >Oldest: {{ formatMostRecent(notes[notes.length - 1].submission_date) }} days</small
            >
          </div>
        </div>
        <section class="note-section" :key="i" v-for="(note, i) in notes">
          <p class="note-section__title">
            {{ note.saved_data__meeting_type ? note.saved_data__meeting_type : 'Untitled' }}
          </p>
          <p class="note-section__date">{{ formatDateTime(note.submission_date) }}</p>
          <pre class="note-section__body">{{ note.saved_data__meeting_comments }}</pre>
        </section>
      </div>
      <div v-else class="modal-container">
        <div class="flex-row-spread sticky border-bottom">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h4>Notes</h4>
          </div>

          <div class="flex-row">
            <small class="note-border">Total: {{ notesLength }}</small>
            <small class="note-border light-green-bg">Most recent: 0 days</small>
            <small class="note-border">Oldest: 0 days</small>
          </div>
        </div>
        <section class="note-section">
          <p class="note-section__body">No notes for this opportunity</p>
        </section>
      </div>
    </Modal>
    <Modal v-if="editOpModalOpen" dimmed>
      <div class="opp-modal-container">
        <div class="flex-row-spread header">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="height: 1.75rem; margin-left: 0.5rem; margin-right: 0.25rem"
              alt=""
            />
            <h3>Update Opportunity</h3>
          </div>
          <img
            src="@/assets/images/close.svg"
            style="height: 1.5rem; margin-top: -1rem; margin-right: 0.75rem; cursor: pointer"
            @click="resetEdit"
            alt=""
          />
        </div>
        <div class="opp-modal">
          <section :key="field.id" v-for="field in oppFormCopy">
            <div v-if="field.apiName === 'meeting_type'">
              <span class="input-container">
                <input
                  class="basic-slide"
                  id="Title"
                  type="text"
                  @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                  placeholder="Title"
                /><label for="Title">Title</label>
              </span>
              <!-- <p>Note Title:</p>
              <textarea
                id="user-input"
                cols="30"
                rows="2"
                style="width: 36.5vw; border-radius: 0.2rem"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea> -->
            </div>
            <div v-else-if="field.apiName === 'meeting_comments'">
              <span class="input-container">
                <textarea
                  class="basic-slide"
                  id="notes"
                  type="text"
                  cols="30"
                  rows="4"
                  placeholder="Note"
                  style="line-height: 2rem"
                  @input=";(value = $event.target.value), setUpdateValues(value, field.apiName)"
                /><label for="Note">Note</label>
              </span>
              <!-- <p>Notes:</p>
              <textarea
                id="user-input"
                ccols="30"
                rows="8"
                style="width: 36.5vw; border-radius: 0.2rem"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea> -->
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
                style="width: 26.25vw; border-radius: 0.4rem; padding: 7px"
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
            <div v-else-if="field.apiName === 'AccountId'">
              <p>{{ field.referenceDisplayLabel }}</p>
              <Multiselect
                v-model="selectedAccount"
                :options="allAccounts"
                @search-change="getAccounts($event)"
                @select="
                  setUpdateValues(
                    field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                    field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                      ? $event.value
                      : $event.id,
                    field.dataType === 'MultiPicklist' ? true : false,
                  )
                "
                openDirection="below"
                style="width: 18vw"
                selectLabel="Enter"
                track-by="integration_id"
                label="name"
                :loading="dropdownLoading || loadingAccounts"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results.</p>
                </template>

                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    {{ currentAccount }}
                  </p>
                </template>
              </Multiselect>
            </div>
            <div
              v-else-if="
                field.dataType === 'Picklist' ||
                field.dataType === 'MultiPicklist' ||
                (field.dataType === 'Reference' && field.apiName !== 'AccountId')
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <Multiselect
                v-model="dropdownVal[field.apiName]"
                :options="
                  field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                    ? picklistQueryOpts[field.apiName]
                    : referenceOpts[field.apiName]
                "
                @select="
                  setUpdateValues(
                    field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                    field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                      ? $event.value
                      : $event.id,
                    field.dataType === 'MultiPicklist' ? true : false,
                  )
                "
                @search-change="
                  field.dataType === 'Reference'
                    ? getReferenceFieldList(field.apiName, field.id, $event)
                    : null
                "
                :multiple="field.dataType === 'MultiPicklist' ? true : false"
                openDirection="below"
                :loading="dropdownLoading"
                style="width: 18vw"
                selectLabel="Enter"
                :track-by="
                  field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                    ? 'value'
                    : 'id'
                "
                :label="
                  field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                    ? 'label'
                    : 'name'
                "
              >
                <template slot="noResult">
                  <p class="multi-slot">No results ? Try loading more</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    {{
                      field.apiName === 'AccountId'
                        ? currentAccount
                        : field.apiName === 'OwnerId'
                        ? currentOwner
                        : `${currentVals[field.apiName]}` !== 'null'
                        ? `${currentVals[field.apiName]}`
                        : `${field.referenceDisplayLabel}`
                    }}
                  </p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more">
                    Load more <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                  </p>
                </template>
              </Multiselect>

              <div
                :class="stageGateField ? 'adding-stage-gate' : 'hide'"
                v-if="field.apiName === 'StageName'"
              >
                <div class="adding-stage-gate__header">
                  <img src="@/assets/images/warning.svg" alt="" />
                  <p>This Stage has validation rules</p>
                </div>

                <div class="adding-stage-gate__body">
                  <div v-for="(field, i) in stageValidationFields[stageGateField]" :key="i">
                    <div v-if="field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'">
                      <p>{{ field.referenceDisplayLabel }}*</p>
                      <Multiselect
                        :options="stagePicklistQueryOpts[field.apiName]"
                        @select="
                          setUpdateValidationValues(
                            field.apiName === 'ForecastCategory'
                              ? 'ForecastCategoryName'
                              : field.apiName,
                            $event.value,
                          )
                        "
                        v-model="dropdownVal[field.apiName]"
                        openDirection="below"
                        :loading="dropdownLoading"
                        style="width: 18vw"
                        selectLabel="Enter"
                        track-by="value"
                        label="label"
                      >
                        <template slot="noResult">
                          <p class="multi-slot">No results.</p>
                        </template>

                        <template slot="placeholder">
                          <p class="slot-icon">
                            <img src="@/assets/images/search.svg" alt="" />
                            {{
                              `${currentVals[field.apiName]}` !== 'null'
                                ? `${currentVals[field.apiName]}`
                                : `${field.referenceDisplayLabel}`
                            }}
                          </p>
                        </template>
                      </Multiselect>
                    </div>
                    <div v-else-if="field.dataType === 'String' && field.apiName !== 'NextStep'">
                      <p>{{ field.referenceDisplayLabel }}*</p>
                      <input
                        id="user-input"
                        type="text"
                        :placeholder="currentVals[field.apiName]"
                        v-model="currentVals[field.apiName]"
                        @input="
                          ;(value = $event.target.value),
                            setUpdateValidationValues(field.apiName, value)
                        "
                      />
                    </div>

                    <div
                      v-else-if="
                        field.dataType === 'TextArea' ||
                        (field.length > 250 && field.dataType === 'String')
                      "
                    >
                      <p>{{ field.referenceDisplayLabel }}*</p>
                      <textarea
                        id="user-input"
                        ccols="30"
                        rows="2"
                        :placeholder="currentVals[field.apiName]"
                        style="width: 20vw; border-radius: 0.2rem; padding: 7px"
                        v-model="currentVals[field.apiName]"
                        @input="
                          ;(value = $event.target.value),
                            setUpdateValidationValues(field.apiName, value)
                        "
                      >
                      </textarea>
                    </div>
                    <div v-else-if="field.dataType === 'Date'">
                      <p>{{ field.referenceDisplayLabel }}*</p>
                      <input
                        type="text"
                        onfocus="(this.type='date')"
                        onblur="(this.type='text')"
                        :placeholder="currentVals[field.apiName]"
                        v-model="currentVals[field.apiName]"
                        id="user-input"
                        @input="
                          ;(value = $event.target.value),
                            setUpdateValidationValues(field.apiName, value)
                        "
                      />
                    </div>
                    <div v-else-if="field.dataType === 'DateTime'">
                      <p>{{ field.referenceDisplayLabel }}*</p>
                      <input
                        type="datetime-local"
                        id="start"
                        v-model="currentVals[field.apiName]"
                        @input="
                          ;(value = $event.target.value),
                            setUpdateValidationValues(field.apiName, value)
                        "
                      />
                    </div>
                    <div
                      v-else-if="
                        field.dataType === 'Phone' ||
                        field.dataType === 'Double' ||
                        field.dataType === 'Currency'
                      "
                    >
                      <p>{{ field.referenceDisplayLabel }}*</p>
                      <input
                        id="user-input"
                        type="number"
                        v-model="currentVals[field.apiName]"
                        :placeholder="currentVals[field.apiName]"
                        @input="
                          ;(value = $event.target.value),
                            setUpdateValidationValues(field.apiName, value)
                        "
                      />
                    </div>

                    <div v-else-if="field.apiName === 'OwnerId'">
                      <p>{{ field.referenceDisplayLabel }}*</p>

                      <Multiselect
                        v-model="selectedOwner"
                        :options="allUsers"
                        @select="
                          setUpdateValidationValues(
                            field.apiName,
                            $event.salesforce_account_ref.salesforce_id,
                          )
                        "
                        openDirection="below"
                        style="width: 18vw"
                        selectLabel="Enter"
                        track-by="salesforce_account_ref.salesforce_id"
                        label="full_name"
                        :loading="dropdownLoading"
                      >
                        <template slot="noResult">
                          <p class="multi-slot">No results.</p>
                        </template>
                        <template slot="placeholder">
                          <p class="slot-icon">
                            <img src="@/assets/images/search.svg" alt="" />
                            {{ currentOwner }}
                          </p>
                        </template>
                      </Multiselect>
                    </div>

                    <div v-else-if="field.apiName === 'AccountId'">
                      <p>{{ field.referenceDisplayLabel }}*</p>
                      <Multiselect
                        v-model="selectedAccount"
                        :options="allAccounts"
                        @search-change="getAccounts($event)"
                        @select="setUpdateValidationValues(field.apiName, $event.id)"
                        openDirection="below"
                        style="width: 18vw"
                        selectLabel="Enter"
                        track-by="integration_id"
                        label="name"
                        :loading="dropdownLoading || loadingAccounts"
                      >
                        <template slot="noResult">
                          <p class="multi-slot">No results.</p>
                        </template>

                        <template slot="placeholder">
                          <p class="slot-icon">
                            <img src="@/assets/images/search.svg" alt="" />
                            {{ currentAccount }}
                          </p>
                        </template>
                      </Multiselect>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else-if="field.dataType === 'Date'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                type="date"
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

            <div v-else-if="field.dataType === 'Boolean'">
              <p>{{ field.referenceDisplayLabel }}:</p>

              <Multiselect
                v-model="dropdownVal[field.apiName]"
                :options="booleans"
                @select="setUpdateValues(field.apiName, $event)"
                openDirection="below"
                style="width: 18vw"
                selectLabel="Enter"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results.</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    {{ currentVals[field.apiName] }}
                  </p>
                </template>
              </Multiselect>
            </div>
          </section>
          <!-- <button>Add product</button> -->
        </div>
        <div class="flex-end-opp">
          <div v-if="updatingMeeting" style="display: flex; align-items: center">
            <button @click="onMakeMeetingUpdate" class="add-button__">Update</button>
            <p @click="resetEdit" class="cancel">Cancel</p>
          </div>
          <div v-else style="display: flex; align-items: center">
            <button @click="updateResource()" class="add-button__">Update</button>
            <p @click="resetEdit" class="cancel">Cancel</p>
          </div>
        </div>
      </div>
    </Modal>
    <Modal
      v-if="meetingOpen"
      dimmed
      @close-modal="
        () => {
          //$emit('cancel'), resetMeeting()
        }
      "
    >
      <div class="create-modal">
        <header class="create-modal__header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" height="28px" alt="" />
            <h3>Create Zoom Meeting</h3>
          </div>

          <img
            src="@/assets/images/close.svg"
            style="height: 1.5rem; margin-top: -0.5rem; margin-right: 0.5rem; cursor: pointer"
            @click="resetMeeting()"
            alt=""
          />
        </header>
        <section class="create-modal__body">
          <span>
            <input
              v-model="meetingTitle"
              class="zoom-input"
              type="text"
              placeholder="Meeting Title"
            />
          </span>

          <span>
            <textarea
              v-model="description"
              class="zoom-input-ta"
              type="text"
              placeholder="Meeting Description"
            />
          </span>

          <span>
            <label for="startDate">Date</label>
            <input id="startDate" v-model="startDate" class="zoom-input" type="date" />
          </span>

          <span>
            <label for="startTime">Time</label>
            <input id="startTime" v-model="startTime" class="zoom-input" type="time" />
          </span>

          <span>
            <label>Duration</label>
            <Multiselect
              placeholder="Duration"
              style="width: 32vw"
              v-model="meetingDuration"
              :options="fiveMinuteIntervals"
              openDirection="below"
              :multiple="false"
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>
            </Multiselect>
          </span>

          <!-- <div style="text-align: center">
            <h3>Add Participants</h3>
          </div> -->

          <span>
            <label>Internal Participants</label>
            <Multiselect
              placeholder="Internal Users"
              style="width: 32vw"
              v-model="internalParticipantsSelected"
              :options="internalParticipants"
              openDirection="below"
              selectLabel="Enter"
              track-by="id"
              :custom-label="internalCustomLabel"
              :multiple="true"
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>
            </Multiselect>
          </span>

          <span>
            <label>External Participants</label>
            <Multiselect
              placeholder="External Users"
              style="width: 32vw; margin-bottom: 1rem"
              v-model="externalParticipantsSelected"
              :options="externalParticipants"
              openDirection="below"
              selectLabel="Enter"
              track-by="id"
              :custom-label="externalCustomLabel"
              :multiple="true"
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>
            </Multiselect>
          </span>

          <span>
            <label class="label">Additional Users</label>
            <input
              :class="
                extraParticipantsSelected.length
                  ? 'zoom-input'
                  : 'light-gray-placeholder zoom-input'
              "
              v-model="extraParticipantsSelected"
              type="text"
              placeholder="Separate emails by commas"
            />
          </span>

          <div class="create-modal__footer">
            <button class="green_button" @click="submitZoomMeeting">Submit</button>
          </div>
        </section>
      </div>
    </Modal>
    <div ref="pipelines" v-if="!loading">
      <div class="results">
        <h6 style="color: #9b9b9b">
          Today's Meetings:
          <span>{{ meetings ? meetings.length : 0 }}</span>
        </h6>
        <div class="flex-row">
          <div v-if="!hasZoomIntegration" class="tooltip">
            <button class="select-btn" :disabled="!hasZoomIntegration">
              Create Meeting <img src="@/assets/images/zoom.png" alt="" style="height: 1rem" />
            </button>
            <span class="tooltiptext">Connect Zoom</span>
          </div>
          <div v-else>
            <button @click="resetMeeting()" class="select-btn" :disabled="!hasZoomIntegration">
              Create Meeting <img src="@/assets/images/zoom.png" alt="" style="height: 1rem" />
            </button>
          </div>

          <div class="tooltip">
            <button @click="refreshCalEvents" class="select-btn cloud">
              <img src="@/assets/images/eventRepeat.svg" style="height: 26px" alt="" />
            </button>
            <span class="tooltiptext">Sync Calendar</span>
          </div>
        </div>
      </div>

      <section class="table-section">
        <div class="table">
          <MeetingWorkflowHeader />
          <MeetingWorkflow
            v-for="(meeting, i) in meetings"
            :key="i"
            @map-opp="mapOpp"
            @update-Opportunity="updateMeeting"
            @no-update="NoMeetingUpdate"
            @remove-participant="removeParticipant"
            @add-participant="addParticipant"
            @get-notes="getNotes"
            @filter-accounts="getAccounts"
            :dropdowns="picklistQueryOptsContacts"
            :contactFields="createContactForm"
            :meeting="meeting.meeting_ref"
            :participants="meeting.meeting_ref.participants"
            :workflowId="meeting.id"
            :resourceId="meeting.resource_id"
            :resourceType="meeting.resource_type"
            :meetingUpdated="meeting.is_completed"
            :allOpps="allOpps"
            :owners="allUsers"
            :accounts="allAccounts"
            :meetingLoading="meetingLoading"
            :index="i"
          />
        </div>
      </section>
    </div>
    <div v-if="loading">
      <Loader :loaderText="loaderText" />
    </div>
  </div>
</template>
<script>
import { SObjects, SObjectPicklist, MeetingWorkflows } from '@/services/salesforce'
import AlertTemplate from '@/services/alerts/'
import CollectionManager from '@/services/collectionManager'
import SlackOAuth from '@/services/slack'
import Zoom from '@/services/zoom/account'
import MeetingWorkflow from '@/components/MeetingWorkflow'
import MeetingWorkflowHeader from '@/components/MeetingWorkflowHeader'
import User from '@/services/users'

export default {
  name: 'Meetings',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    SkeletonBox: () => import(/* webpackPrefetch: true */ '@/components/SkeletonBox'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    MeetingWorkflowHeader,
    MeetingWorkflow,
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
    Loader: () => import(/* webpackPrefetch: true */ '@/components/Loader'),
  },
  data() {
    return {
      meetingOpen: false,
      integrationId: null,
      stageGateField: null,
      stageValidationFields: {},
      stagesWithForms: [],
      dropdownVal: {},
      key: 0,
      meetingKey: 0,
      dropdownLoading: false,
      updatingMeeting: false,
      meetingWorkflowId: null,
      meetingLoading: null,
      updatingOpps: false,
      oppInstanceId: null,
      oppId: null,
      primaryCheckList: [],
      workflowCheckList: [],
      allSelected: false,
      allWorkflowsSelected: false,
      createQueryOpts: {},
      updateList: [],
      recapList: [],
      currentVals: [],
      closeDateSelected: false,
      advanceStageSelected: false,
      forecastSelected: false,
      selection: false,
      allStages: [],
      allForecasts: [],
      originalList: null,
      daysForward: null,
      allOpps: null,
      loading: false,
      loadingWorkflows: false,
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
      users: CollectionManager.create({ ModelClass: User }),
      stagePicklistQueryOpts: {},
      currentWorkflow: null,
      selectedWorkflow: false,
      modalOpen: false,
      editOpModalOpen: false,
      addOppModalOpen: false,
      refreshId: null,
      currentList: "Today's Meetings",
      alertInstanceId: null,
      showList: false,
      showWorkflowList: true,
      loadingAccounts: false,
      accountSobjectId: null,
      currentOwner: null,
      currentAccount: null,
      selectedAccount: null,
      selectedOwner: null,
      showPopularList: true,
      updateOppForm: null,
      oppFormCopy: null,
      createOppForm: null,
      createContactForm: null,
      instanceId: null,
      contactInstanceId: null,
      formData: {},
      picklistQueryOpts: {},
      picklistQueryOptsContacts: {},
      allAccounts: null,
      allUsers: null,
      showMeetingList: true,
      selectedMeeting: false,
      meetings: null,
      referenceOpts: {},
      fiveMinuteIntervals: [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55],
      meetingTitle: '',
      description: '',
      startDate: null,
      startTime: null,
      meetingDuration: 30,
      internalParticipants: null,
      externalParticipants: null,
      internalParticipantsSelected: [],
      externalParticipantsSelected: [],
      extraParticipantsSelected: '',
      stageGateId: null,
      booleans: ['true', 'false'],
      notes: [],
      notesLength: 0,
      days: {
        0: 'Sunday',
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
      },
      loaderText: "Pulling in your meetings",
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    hasZoomIntegration() {
      return !!this.$store.state.user.zoomAccount && this.$store.state.user.hasZoomIntegration
    },
  },
  created() {
    this.getMeetingList()
    this.getObjects()
    this.templates.refresh()
    this.getAllForms()
  },
  beforeMount() {
    this.getUsers()
    this.getExternalParticipants()
  },
  watch: {
    accountSobjectId: 'getInitialAccounts',
    updateOppForm: 'setForms',
    stageGateField: 'stageGateInstance',
    // updateList: {
    //   async handler(currList) {
    //     if (currList.length === 0 && this.recapList.length) {
    //       let bulk = true ? this.recapList.length > 1 : false
    //       try {
    //         const res = await SObjects.api.sendRecap(bulk, this.recapList)
    //       } catch (e) {
    //         console.log(e)
    //       } finally {
    //         this.recapList = []
    //       }
    //     }
    //   },
    // },
  },
  methods: {
    resetMeeting() {
      this.clearData()
      this.meetingOpen = !this.meetingOpen
    },
    async submitZoomMeeting() {
      if (
        !this.meetingTitle ||
        !this.startDate ||
        !this.startTime ||
        !this.meetingDuration ||
        !this.externalParticipantsSelected
      ) {
        console.log('Please input all information')
        this.$toast('Please input all information', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      let noSpacesExtra = ''
      for (let i = 0; i < this.extraParticipantsSelected.length; i++) {
        this.extraParticipantsSelected[i] !== ' '
          ? (noSpacesExtra += this.extraParticipantsSelected[i])
          : null
      }
      let extraParticipants = []
      if (noSpacesExtra) {
        extraParticipants = noSpacesExtra.split(',')
      }
      let extra_participants = []
      for (let i = 0; i < extraParticipants.length; i++) {
        const participant = extraParticipants[i]
        if (participant.length) {
          extra_participants.push(participant)
        }
      }
      if (
        !(
          this.internalParticipantsSelected.length ||
          this.externalParticipantsSelected.length ||
          extra_participants.length
        )
      ) {
        console.log('Please add participants to the meeting')
        this.$toast('Please add participants to the meeting', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      const hourMinute = this.startTime.split(':')
      const contacts = this.externalParticipantsSelected.map((contact) => contact.id)
      const internal = this.internalParticipantsSelected.map((internal) => internal.id)
      const data = {
        meeting_topic: this.meetingTitle,
        meeting_description: this.description,
        meeting_date: this.startDate,
        meeting_hour: hourMinute[0],
        meeting_minute: hourMinute[1],
        meeting_time: this.startTime,
        meeting_duration: this.meetingDuration,
        contacts,
        internal,
        extra_participants,
      }

      try {
        const res = await Zoom.api.createZoomMeeting(data)
        if (res.status === 200) {
          this.$toast('Meeting Scheduled', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.resetMeeting()
        } else {
          this.$toast('Error Scheduling Meeting', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      } catch (e) {
        console.log(e)
      }
    },
    resetNotes() {
      this.modalOpen = !this.modalOpen
      this.notes = []
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
            this.notesLength = this.notes.length
          }
        }
      } catch (e) {
        this.$toast('Error gathering Notes!', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    clearData() {
      this.meetingTitle = ''
      this.description = ''
      this.startDate = null
      this.startTime = null
      this.meetingDuration = 30
      this.internalParticipantsSelected = []
      this.externalParticipantsSelected = []
      this.extraParticipantsSelected = ''
    },
    async stageGateInstance(field) {
      this.stageGateId = null
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Opportunity',
          formType: 'STAGE_GATING',
          stageName: field ? field : this.stageGateField,
        })
        this.stageGateId = res.form_id
      } catch (e) {
        this.$toast('Error creating stage form instance', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getReferenceFieldList(key, val, eventVal) {
      try {
        const res = await SObjects.api.getSobjectPicklistValues({
          sobject_id: val,
          value: eventVal ? eventVal : '',
        })
        this.referenceOpts[key] = res
      } catch (e) {
        this.$toast('Error gathering reference fields', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async refreshCalEvents() {
      let response
      try {
        response = await User.api.refreshCalendarEvents()        
      } catch (e) {
        console.log('Error in refreshCalEvents: ', e)
      } finally {
        this.loading = true
        this.loaderText = "Pulling your calendar events..."
        setTimeout(() => {
          this.loaderText = "Mapping to Salesforce..."
          this.getMeetingList()
          setTimeout(() => {
            this.loading = false
            this.loaderText = "Pulling in your meetings"
            this.getMeetingList()
            if (response.status === 200) {
              this.$toast('Calendar Successfully Synced', {
                timeout: 2000,
                position: 'top-left',
                type: 'success',
                toastClassName: 'custom',
                bodyClassName: ['custom'],
              })
            } else {
              this.$toast('Error Syncing Calendar', {
                timeout: 2000,
                position: 'top-left',
                type: 'error',
                toastClassName: 'custom',
                bodyClassName: ['custom'],
              })
            }
          }, 3000);
        }, 2000);
        
      }
    },
    async getMeetingList() {
      try {
        const res = await MeetingWorkflows.api.getMeetingList()
        this.meetings = res.results
      } catch (e) {
        this.$toast('Error gathering Meetings!', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
      }
    },
    async mapOpp(workflow, resource, resourceType) {
      this.meetingLoading = true
      try {
        const res = await MeetingWorkflows.api
          .mapMeeting(workflow, resource, resourceType)
          .then(() => {
            this.getMeetingList()
          })
      } catch (e) {
        this.$toast('Error mapping Opportunity', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        setTimeout(() => {
          this.meetingLoading = false
        }, 500)
      }
    },
    async removeParticipant(workflow, participant) {
      this.meetingLoading = true
      try {
        const res = await MeetingWorkflows.api.removeParticipant(workflow, participant).then(() => {
          this.getMeetingList()
        })
      } catch (e) {
        this.$toast('Error removing participant', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        setTimeout(() => {
          this.meetingLoading = false
        }, 500)
      }
    },
    async addParticipant(workflow, participant, data) {
      this.meetingLoading = true
      try {
        const res = await MeetingWorkflows.api
          .updateParticipant({
            workflow_id: workflow,
            tracking_id: participant,
            form_data: data,
          })
          .then(() => {
            this.getMeetingList()
          })
      } catch (e) {
        console.log(e)
        // this.$toast('Error adding contact', {
        //   timeout: 2000,
        //   position: 'top-left',
        //   type: 'error',
        //   toastClassName: 'custom',
        //   bodyClassName: ['custom'],
        // })
      } finally {
        setTimeout(() => {
          this.meetingLoading = false
          this.$toast('Contact Added Successfully', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }, 500)
      }
    },
    selectMeeting(name) {
      this.currentList = name
      this.showList = false
      this.selectedMeeting = true
      this.selectedWorkflow = false
    },
    closeListSelect() {
      this.showList = false
    },
    async listPicklists(type, query_params) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)
        this.picklistQueryOpts[type] = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    async listStagePicklists(type, query_params) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)
        this.stagePicklistQueryOpts[type] = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    async listCreatePicklists(type, query_params) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)
        this.createQueryOpts[type] = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    resetEdit() {
      this.editOpModalOpen = !this.editOpModalOpen
    },
    resetAddOpp() {
      this.addOppModalOpen = !this.addOppModalOpen
    },
    async updateContactInstance() {
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Contact',
          formType: 'UPDATE',
        })
        this.contactInstanceId = res.form_id
      } catch (e) {
        console.log(e)
      }
    },
    async NoMeetingUpdate(meetingWorkflow) {
      this.meetingLoading = true
      try {
        const res = await MeetingWorkflows.api
          .updateWorkflow({
            workflow_id: meetingWorkflow,
            form_data: {
              meeting_type: 'No Update',
              meeting_comments: 'No Update',
            },
            stage_form_id: [],
          })
          .then(() => {
            this.getMeetingList()
          })
      } catch (e) {
        this.$toast('Meeting log unsuccessful, error with no update', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.meetingLoading = false
        this.$toast('Meeting logged Successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async updateMeeting(meetingWorkflow, id, integrationId) {
      this.dropdownLoading = true
      this.currentVals = []
      this.editOpModalOpen = true
      this.updatingMeeting = true
      this.meetingWorkflowId = meetingWorkflow
      this.dropdownVal = {}
      this.formData = {}
      this.oppId = id
      this.integrationId = integrationId
      try {
        const res = await SObjects.api.getCurrentValues({
          resourceType: 'Opportunity',
          resourceId: id,
        })
        this.currentVals = res.current_values
        this.currentOwner = this.allUsers.filter(
          (user) => user.salesforce_account_ref.salesforce_id === this.currentVals['OwnerId'],
        )[0].full_name
        this.allOpps.filter((opp) => opp.id === this.oppId)[0].account_ref
          ? (this.currentAccount = this.allOpps.filter(
              (opp) => opp.id === this.oppId,
            )[0].account_ref.name)
          : (this.currentAccount = 'Account')
      } catch (e) {
        // this.$toast('Error creating update form', {
        //   timeout: 2000,
        //   position: 'top-left',
        //   type: 'error',
        //   toastClassName: 'custom',
        //   bodyClassName: ['custom'],
        // })
      } finally {
        this.dropdownLoading = false
      }
    },
    async onMakeMeetingUpdate() {
      this.meetingLoading = true
      this.editOpModalOpen = false
      try {
        const res = await MeetingWorkflows.api
          .updateWorkflow({
            workflow_id: this.meetingWorkflowId,
            stage_form_id: this.stageGateId ? [this.stageGateId] : [],
            form_data: this.formData,
          })
          .then((res) => {
            this.getMeetingList()
          })
      } catch (e) {
        this.$toast('Error updating opportunity', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.updatingMeeting = false
        this.meetingLoading = false
        this.$toast('Meeting logged Successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async createFormInstance(id, integrationId, alertInstanceId = null) {
      this.stageGateField = null
      this.integrationId = integrationId
      this.dropdownLoading = true
      this.editOpModalOpen = true
      this.currentVals = []
      this.updatingMeeting = false
      this.currentOwner = null
      this.currentAccount = null
      this.alertInstanceId = alertInstanceId
      this.oppId = id
      try {
        const res = await SObjects.api.getCurrentValues({
          resourceType: 'Opportunity',
          resourceId: id,
        })
        this.currentVals = res.current_values
        this.currentOwner = this.allUsers.filter(
          (user) => user.salesforce_account_ref.salesforce_id === this.currentVals['OwnerId'],
        )[0].full_name
        this.allOpps.filter((opp) => opp.id === this.oppId)[0].account_ref
          ? (this.currentAccount = this.allOpps.filter(
              (opp) => opp.id === this.oppId,
            )[0].account_ref.name)
          : (this.currentAccount = 'Account')
      } catch (e) {
        console.log(e)
      } finally {
        this.dropdownLoading = false
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
    setUpdateValues(key, val, multi) {
      if (multi) {
        this.formData[key] = this.formData[key]
          ? this.formData[key] + ';' + val
          : val.split(/&#39;/g)[0]
      }
      if (val && !multi) {
        this.formData[key] = val
      }
      if (key === 'StageName') {
        this.stagesWithForms.includes(val)
          ? (this.stageGateField = val)
          : (this.stageGateField = null)
      }
    },
    setUpdateValidationValues(key, val) {
      if (val) {
        this.formData[key] = val
      }
    },

    async updateResource() {
      this.updateList.push(this.oppId)
      this.editOpModalOpen = false
      try {
        const res = await SObjects.api.updateResource({
          form_data: this.formData,
          stage_name: this.stageGateField ? this.stageGateField : null,
          integration_ids: [this.integrationId],
          resource_type: 'Opportunity',
          form_type: 'UPDATE',
          resource_id: this.oppId,
        })
        // .then(async () => {
        //   let updatedRes = await SObjects.api.getObjects('Opportunity')
        //   this.allOpps = updatedRes.results
        //   this.originalList = updatedRes.results
        // })
        this.updateList = []
        this.formData = {}
        this.$toast('Salesforce Update Successful', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        this.$toast('Error updating opportunity', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    setForms() {
      for (let i = 0; i < this.createContactForm.length; i++) {
        if (
          this.createContactForm[i].dataType === 'Picklist' ||
          this.createContactForm[i].dataType === 'MultiPicklist'
        ) {
          this.picklistQueryOptsContacts[this.createContactForm[i].apiName] =
            this.createContactForm[i].apiName
        } else if (this.createContactForm[i].dataType === 'Reference') {
          this.picklistQueryOptsContacts[this.createContactForm[i].referenceDisplayLabel] =
            this.createContactForm[i].referenceDisplayLabel
        }
      }
      for (let i in this.picklistQueryOptsContacts) {
        this.picklistQueryOptsContacts[i] = this.listPicklists(i, {
          picklistFor: i,
          salesforceObject: 'Opportunity',
        })
      }

      for (let i = 0; i < this.oppFormCopy.length; i++) {
        if (
          this.oppFormCopy[i].dataType === 'Picklist' ||
          this.oppFormCopy[i].dataType === 'MultiPicklist'
        ) {
          this.picklistQueryOpts[this.oppFormCopy[i].apiName] = this.oppFormCopy[i].apiName
        } else if (this.oppFormCopy[i].dataType === 'Reference') {
          this.referenceOpts[this.oppFormCopy[i].apiName] = this.oppFormCopy[i].id
        }
      }

      for (let i in this.picklistQueryOpts) {
        this.picklistQueryOpts[i] = this.listPicklists(i, {
          picklistFor: i,
          salesforceObject: 'Opportunity',
        })
      }

      for (let i in this.referenceOpts) {
        this.referenceOpts[i] = this.getReferenceFieldList(i, this.referenceOpts[i])
      }

      for (let i = 0; i < this.createOppForm.length; i++) {
        if (
          this.createOppForm[i].dataType === 'Picklist' ||
          this.createOppForm[i].dataType === 'MultiPicklist'
        ) {
          this.createQueryOpts[this.createOppForm[i].apiName] = this.createOppForm[i].apiName
        } else if (this.createOppForm[i].dataType === 'Reference') {
          this.createQueryOpts[this.createOppForm[i].referenceDisplayLabel] =
            this.createOppForm[i].referenceDisplayLabel
        }
      }

      for (let i in this.createQueryOpts) {
        this.createQueryOpts[i] = this.listCreatePicklists(i, {
          picklistFor: i,
          salesforceObject: 'Opportunity',
        })
      }

      this.filterFields = this.updateOppForm[0].fieldsRef.filter(
        (field) =>
          field.apiName !== 'meeting_type' &&
          field.apiName !== 'meeting_comments' &&
          !field.apiName.includes('__c'),
      )
      this.filterFields = [...this.filterFields, this.ladFilter, this.lmdFilter]

      this.updateOppForm[0].fieldsRef.filter((field) => field.apiName === 'AccountId').length
        ? (this.accountSobjectId = this.updateOppForm[0].fieldsRef.filter(
            (field) => field.apiName === 'AccountId',
          )[0].id)
        : this.createOppForm.filter((field) => field.apiName === 'AccountId').length
        ? (this.accountSobjectId = this.createOppForm.filter(
            (field) => field.apiName === 'AccountId',
          )[0].id)
        : (this.accountSobjectId = null)

      this.oppFields = this.updateOppForm[0].fieldsRef.filter(
        (field) =>
          field.apiName !== 'meeting_type' &&
          field.apiName !== 'meeting_comments' &&
          field.apiName !== 'Name' &&
          field.apiName !== 'AccountId' &&
          field.apiName !== 'OwnerId',
      )

      for (let i in this.stagePicklistQueryOpts) {
        this.stagePicklistQueryOpts[i] = this.listStagePicklists(i, {
          picklistFor: i,
          salesforceObject: 'Opportunity',
        })
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
        let stageGateForms = res.filter(
          (obj) => obj.formType === 'STAGE_GATING' && obj.resource === 'Opportunity',
        )
        this.createContactForm = res.filter(
          (obj) => obj.formType === 'CREATE' && obj.resource === 'Contact',
        )

        let stages = stageGateForms.map((field) => field.stage)
        this.stagesWithForms = stages
        this.oppFormCopy = this.updateOppForm[0].fieldsRef
        this.createOppForm = this.createOppForm[0].fieldsRef
        this.createContactForm = this.createContactForm[0].fieldsRef.filter(
          (f) => f.apiName !== 'meeting_type' && f.apiName !== 'meeting_comments',
        )

        for (const field of stageGateForms) {
          this.stageValidationFields[field.stage] = field.fieldsRef
        }
        let stageArrayOfArrays = stageGateForms.map((field) => field.fieldsRef)
        let allStageFields = [].concat.apply([], stageArrayOfArrays)
        let dupeStagesRemoved = [
          ...new Map(allStageFields.map((v) => [v.referenceDisplayLabel, v])).values(),
        ]

        for (let i = 0; i < dupeStagesRemoved.length; i++) {
          if (
            dupeStagesRemoved[i].dataType === 'Picklist' ||
            dupeStagesRemoved[i].dataType === 'MultiPicklist'
          ) {
            this.stagePicklistQueryOpts[dupeStagesRemoved[i].apiName] = dupeStagesRemoved[i].apiName
          } else if (dupeStagesRemoved[i].dataType === 'Reference') {
            this.stagePicklistQueryOpts[dupeStagesRemoved[i].referenceDisplayLabel] =
              dupeStagesRemoved[i].referenceDisplayLabel
          }
        }
      } catch (error) {
        this.$toast('Error setting forms', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },

    async getUsers() {
      try {
        const res = await SObjects.api.getObjects('User')
        this.allUsers = res.results.filter((user) => user.has_salesforce_integration)
        this.internalParticipants = this.allUsers
      } catch (e) {
        console.log(e)
      }
    },
    internalCustomLabel({ full_name, email }) {
      return `${full_name} (${email})`
    },
    externalCustomLabel({ secondary_data, email }) {
      return `${secondary_data.Name ? secondary_data.Name : 'N/A'} (${email ? email : 'N/A'})`
    },
    async getExternalParticipants() {
      try {
        const res = await SObjects.api.getObjects('Contact')
        this.externalParticipants = res.results //.filter((user) => user.has_salesforce_integration)
      } catch (e) {
        this.$toast('Error gathering users', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getInitialAccounts() {
      this.loadingAccounts = true
      if (this.accountSobjectId) {
        try {
          const res = await SObjects.api.getSobjectPicklistValues({
            sobject_id: this.accountSobjectId,
          })
          this.allAccounts = res
        } catch (e) {
          this.$toast('Error gatherign accounts', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } finally {
          this.loadingAccounts = false
        }
      }
    },
    async getAccounts(val) {
      this.loadingAccounts = true
      try {
        const res = await SObjects.api.getSobjectPicklistValues({
          sobject_id: this.accountSobjectId,
          value: val,
        })
        this.allAccounts = res
      } catch (e) {
        console.log(e)
      } finally {
        this.loadingAccounts = false
      }
    },
    async getObjects() {
      this.loading = true
      try {
        const res = await SObjects.api.getObjectsForWorkflows('Opportunity')
        this.allOpps = res.results
        this.originalList = res.results
      } catch (e) {
        console.log(e)
      } finally {
        this.loading = false
      }
    },

    allOpportunities() {
      this.$router.replace({ path: '/Pipelines' })
    },
    weekDay(input) {
      let newer = new Date(input)
      return this.days[newer.getDay()]
    },
    formatDateTime(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      let newDate = input.replace(pattern, '$2/$3/$1')
      return newDate.split('T')[0]
    },
    formatMostRecent(date2) {
      let today = new Date()
      let d = new Date(date2)
      let diff = today.getTime() - d.getTime()
      let days = diff / (1000 * 3600 * 24)
      return Math.floor(days)
    },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

@mixin epic-sides() {
  position: relative;
  z-index: 1;

  &:before {
    position: absolute;
    content: '';
    display: block;
    top: 0;
    left: -5000px;
    height: 100%;
    width: 15000px;
    z-index: -1;
    @content;
  }
}

.input-container {
  position: relative;
  display: inline-block;
  margin: 30px 10px;
  @include epic-sides() {
    background: inherit;
  }
}

.basic-slide {
  display: inline-block;
  width: 36vw;
  margin-left: -8px;
  padding: 9px 0 10px 16px;
  font-family: $base-font-family !important;
  font-weight: 400;
  color: $base-gray;
  background: $white;
  border: 1px solid $soft-gray !important;
  border: 0;
  border-radius: 3px;
  outline: 0;
  text-indent: 70px; // Arbitrary.
  transition: all 0.3s ease-in-out;

  &::-webkit-input-placeholder {
    color: #efefef;
    text-indent: 0;
    font-weight: 300;
  }

  + label {
    display: inline-block;
    position: absolute;
    top: 0;
    left: 0;
    padding: 9px 8px;
    font-size: 15px;
    text-align: center;
    margin-left: -8px;
    width: 80px;
    // text-shadow: 0 1px 0 rgba(19, 74, 70, 0.4);
    background: $white-green;
    color: $dark-green;
    transition: all 0.3s ease-in-out;
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
    border-bottom-right-radius: 2px;
  }
}
.basic-slide:focus,
.basic-slide:active {
  color: $base-gray;
  text-indent: 0;
  background: #fff;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;

  &::-webkit-input-placeholder {
    color: #aaa;
  }
  + label {
    transform: translateX(-100%);
  }
}

.light-green-bg {
  background-color: $white-green;
  color: $dark-green !important;
  border: 1px solid $dark-green !important;
}
.note-border {
  border: 1px solid $very-light-gray;
  border-radius: 6px;
  padding: 4px;
  margin: 0px 6px;
  font-size: 12px;
}
.border-bottom {
  border-bottom: 1.25px solid $soft-gray;
}
.sticky {
  position: sticky;
  background-color: white;
  width: 100%;
  left: 0;
  top: 0;
  padding: 0px 6px 8px -2px;
}
.rel {
  position: relative;
}
.adding-stage-gate {
  border: 2px solid $coral;
  border-radius: 0.3rem;
  margin: 0.5rem 0rem;
  width: 36vw;
  min-height: 30vh;
  &__header {
    font-size: 11px;
    color: white;
    padding: 0.5rem;
    width: 100%;
    border-bottom: 1px solid $coral;
    background-color: $coral;
    display: flex;
    align-items: center;
    flex-direction: row;
    img {
      height: 16px;
      filter: invert(90%);
    }
  }
  &__body {
    padding: 0.25rem;
    font-size: 11px !important;
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.2rem;
    overflow: auto;
    height: 30vh;
    input {
      width: 10vw !important;
      height: 1.5rem !important;
    }
    .multiselect {
      width: 12vw !important;
      font-weight: 11px !important;
    }
    p {
      margin-left: 0.25rem;
    }
  }
  &__body::-webkit-scrollbar {
    width: 2px; /* Mostly for vertical scrollbars */
    height: 0px; /* Mostly for horizontal scrollbars */
  }
  &__body::-webkit-scrollbar-thumb {
    background-color: $coral;
    box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
    border-radius: 0.3rem;
  }
  &__body::-webkit-scrollbar-track {
    box-shadow: inset 2px 2px 4px 0 $soft-gray;
    border-radius: 0.3rem;
  }
  &__body::-webkit-scrollbar-track-piece {
    margin-top: 1rem;
  }
}

.hide {
  display: none;
}
.slot-icon {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0;
  margin: 0;
  img {
    height: 1rem;
    margin-right: 0.25rem;
    filter: invert(70%);
  }
}

.results {
  margin: 0;
  width: 100%;
  display: flex;
  padding-left: 1rem;
  margin-bottom: -0.25rem;
  margin-top: -0.75rem;
  align-items: center;
  justify-content: space-between;
}

select {
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  background-color: #fafafa;
  height: 40px;
  width: 100%;
  background-image: url('../assets/images/dropdown.svg');
  background-size: 1rem;
  background-position: 100%;
  background-repeat: no-repeat;
  border: 1px solid #ccc;
  padding-left: 0.75rem;
  border-radius: 0;
}
.select-btn:hover {
  transform: scale(1.02);
  box-shadow: 1px 2px 3px $very-light-gray;
}
[type='search']::-webkit-search-cancel-button {
  -webkit-appearance: none;
  appearance: none;
}
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 12px;
  width: 100%;
  padding: 0;
  margin: 0;
  cursor: text;
  &__more {
    background-color: white;
    color: $dark-green;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    // border-top: 1px solid #e8e8e8;
    width: 100%;
    height: 40px;
    padding: 0px;
    margin: 0;
    cursor: pointer;

    img {
      height: 0.8rem;
      margin-left: 0.25rem;
      filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
        brightness(93%) contrast(89%);
    }
  }
}
input:focus {
  outline: none;
}

textarea:focus {
  outline: none;
}
input[type='date']:focus {
  outline: none;
  color: $dark-green;
}
input[type='date']::-webkit-datetime-edit-text,
input[type='date']::-webkit-datetime-edit-month-field,
input[type='date']::-webkit-datetime-edit-day-field,
input[type='date']::-webkit-datetime-edit-year-field {
  color: #888;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
}
input {
  padding: 7px;
}

.table-section {
  margin: 0;
  padding: 0;
  min-height: 78vh;
  max-height: 80vh;
  overflow: scroll;
  margin-top: 0.5rem;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  background-color: white;
}

.table {
  display: table;
  overflow: scroll;
  border-collapse: separate;
  border-spacing: 4px;
  width: 100vw;
}
.modal-container {
  background-color: $white;
  overflow: auto;
  min-width: 32vw;
  max-width: 34vw;
  min-height: 44vh;
  max-height: 80vh;
  align-items: center;
  border-radius: 0.3rem;
  border: 1px solid #e8e8e8;
}
.opp-modal-container {
  overflow: hidden;
  background-color: white;
  width: 40vw;
  align-items: center;
  border-radius: 0.6rem;
  padding: 1rem;
  border: 1px solid #e8e8e8;
}
.opp-modal {
  width: 39vw;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 0.25rem;
  padding: 0.5rem;
  overflow: auto;
  max-height: 56vh;
  border-radius: 0.3rem;
  border-bottom: 3px solid $white;
  color: $base-gray;
  font-size: 16px;
  letter-spacing: 0.75px;
}
.centered {
  display: flex;
  justify-content: center;
  align-items: center;
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
  display: flex;
  flex-direction: row;
  align-items: center;
}
.flex-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.pipelines {
  padding: 4rem 1.5rem 0.5rem 1rem;
  color: $base-gray;
}
.invert {
  filter: invert(85%);
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
  img {
    margin-left: 0.5rem;
  }
}
.add-button__ {
  display: flex;
  align-items: center;
  border: none;
  padding: 8px 12px;
  font-size: 14px;
  border-radius: 6px;
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
  border: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  padding: 2px;
  border-radius: 5px;
  margin-right: 0.5rem;
}
#user-input {
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  background-color: white;
  min-height: 2.5rem;
  width: 18vw;
}
.zoom-input {
  border: 1px solid $soft-gray;
  border-radius: 0.3rem;
  padding: 0.25rem;
  height: 3rem;
  width: 32vw;
  font-family: inherit;
}
.zoom-input-ta {
  border: 1px solid $soft-gray;
  border-radius: 0.3rem;
  height: 100px;
  padding: 0.25rem;
  width: 32vw;
  font-family: inherit;
}
#user-input:focus {
  outline: 1px solid $dark-green;
}
.header {
  font-size: 18px;
  padding: 0;
  letter-spacing: 0.5px;
  margin-bottom: 0.2rem;
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
  resize: vertical;
}
a {
  text-decoration: none;
}
.green_button {
  color: white;
  background-color: $dark-green;
  max-height: 2rem;
  border-radius: 0.25rem;
  padding: 0.5rem 1.25rem;
  font-weight: bold;
  font-size: 12px;
  border: none;
  cursor: pointer;
}

.sized {
  height: 3em;
  align-self: center;
}
.logo {
  height: 1.75rem;
  margin-left: 0.5rem;
  margin-right: 0.25rem;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.note-section {
  padding: 0.25rem 1rem;
  margin-bottom: 0.25rem;
  background-color: white;
  border-bottom: 1px solid $soft-gray;
  overflow: scroll;
  &__title {
    font-size: 19px;
    font-weight: bolder;
    letter-spacing: 0.6px;
    color: $base-gray;
    padding: 0;
  }
  &__body {
    color: $base-gray;
    font-family: $base-font-family;
    word-wrap: break-word;
    white-space: pre-wrap;
    border-left: 2px solid $dark-green;
    padding-left: 8px;
    font-size: 14px;
  }
  &__date {
    color: $mid-gray;
    font-size: 12px;
    margin-top: -14px;
    margin-bottom: 8px;
    letter-spacing: 0.6px;
  }
}
.logged {
  border-left: 1px solid $dark-green;
}
.light-gray-placeholder::placeholder {
  color: #adadad;
}
.multiselect-span {
  display: flex;
  align-items: center;

  label {
    margin-right: 0.5rem;
  }
}
.multiselect-width {
  // max-width: 23vw;
  width: 23vw;
}
.label {
  margin-right: 0.5rem;
}
.select-btn {
  border: 0.5px solid $dark-green;
  padding: 0.375rem 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  color: $dark-green;
  letter-spacing: 0.2px;
  margin-right: 0.5rem;
  transition: all 0.25s;

  img {
    // filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
    // height: 1rem !important;
    margin-left: 0.25rem;
  }
}
.select-btn:disabled {
  border: none;
  box-shadow: none;
  background-color: $soft-gray;
  cursor: text;
  color: $base-gray;
  opacity: .6;
}
.select-btn:disabled:hover {
  transform: none;
}
.create-modal {
  position: relative;
  width: 36vw;
  max-height: 80vh;
  background-color: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: scroll;

  span {
    margin-bottom: 8px;
  }

  &__header {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 8px 20px;
    position: fixed;
    background-color: white;
    width: 36vw;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    h3 {
      font-size: 21px;
      letter-spacing: 1px;
      margin-left: 4px;
    }
  }
  &__body {
    padding: 20px;
    margin-top: 84px;
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
  }
  &__footer {
    display: flex;
    justify-content: flex-end;
    align-items: flex-end;
    background-color: white;
    position: sticky;
    bottom: 0;
    width: 36vw;
    height: 70px;
    padding: 8px 16px 0px 0px;
  }
}
label {
  display: inline-block;
  padding: 6px;
  font-size: 14px;
  text-align: center;
  min-width: 80px;
  background-color: $white-green;
  color: $dark-green;
  font-weight: bold;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}
.cloud {
  display: flex;
  align-items: center;
  justify-content: center;
  // color: #41b883;
  background-color: white;
  transition: all 0.25s;
  img {
    height: 1.05rem !important;
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
  }
}
@keyframes tooltips-horz {
  to {
    opacity: 0.95;
    transform: translate(0%, 50%);
  }
}
.tooltip {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 2px 0px;
  z-index: 5;
}
.tooltip .tooltiptext {
  visibility: hidden;
  background-color: $base-gray;
  color: white;
  text-align: center;
  border: 1px solid $soft-gray;
  letter-spacing: 0.5px;
  padding: 4px 0px;
  border-radius: 6px;
  font-size: 12px;

  /* Position the tooltip text */
  position: absolute;
  z-index: 1;
  width: 100px;
  top: 100%;
  left: 50%;
  margin-left: -50px;

  /* Fade in tooltip */
  opacity: 0;
  transition: opacity 0.3s;
}
.tooltip:hover .tooltiptext {
  visibility: visible;
  animation: tooltips-horz 300ms ease-out forwards;
}
</style>