<template>
  <div class="pipelines">
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
            src="@/assets/images/close.svg"
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
                style="width: 36.5vw; border-radius: 0.2rem"
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
                style="width: 36.5vw; border-radius: 0.2rem"
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
            <div v-else-if="field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <Multiselect
                :placeholder="
                  `${currentVals[field.apiName]}` !== 'null'
                    ? `${currentVals[field.apiName]}`
                    : `Select ${field.referenceDisplayLabel}`
                "
                :options="picklistQueryOpts[field.apiName]"
                @select="
                  setUpdateValues(
                    field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
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
                  <p>No results.</p>
                </template>
              </Multiselect>

              <div
                :class="stageGateField ? 'adding-stage-gate' : 'hide'"
                v-if="field.apiName === 'StageName'"
              >
                <div class="adding-stage-gate__header">
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
              <Multiselect
                :placeholder="currentOwner"
                v-model="selectedOwner"
                :options="allUsers"
                @select="
                  setUpdateValues(field.apiName, $event.salesforce_account_ref.salesforce_id)
                "
                openDirection="below"
                style="width: 18vw"
                selectLabel="Enter"
                track-by="salesforce_account_ref.salesforce_id"
                label="full_name"
                :loading="dropdownLoading"
              >
                <template slot="noResult">
                  <p>No results.</p>
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
              <p>{{ field.referenceDisplayLabel }}:</p>

              <Multiselect
                :placeholder="currentAccount"
                v-model="selectedAccount"
                :options="allAccounts"
                @select="setUpdateValues(field.apiName, $event.integration_id)"
                openDirection="below"
                style="width: 18vw"
                selectLabel="Enter"
                track-by="integration_id"
                label="name"
                :loading="dropdownLoading"
              >
                <template slot="noResult">
                  <p>No results.</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    {{ currentAccount }}
                  </p>
                </template>
              </Multiselect>
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

    <div ref="pipelines" v-if="!loading">
      <div class="results">
        <h6 style="color: #9b9b9b">
          Today's Meetings:
          <span>{{ meetings.length }}</span>
        </h6>
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
      <Loader loaderText="Pulling in your meetings" />
    </div>
  </div>
</template>
<script>
import { SObjects, SObjectPicklist, MeetingWorkflows } from '@/services/salesforce'
import AlertTemplate from '@/services/alerts/'
import CollectionManager from '@/services/collectionManager'
import SlackOAuth from '@/services/slack'
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
      stageGateId: null,
      booleans: ['true', 'false'],
    }
  },
  computed: {
    user() {
      return this.$store.state.user
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
        console.log(e)
      }
    },
    async getReferenceFieldList(key, val) {
      try {
        const res = await SObjects.api.getSobjectPicklistValues({
          sobject_id: val,
        })
        this.referenceOpts[key] = res
      } catch (e) {
        console.log(e)
      }
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
    async mapOpp(workflow, resource, resourceType) {
      this.meetingLoading = true
      try {
        const res = await MeetingWorkflows.api
          .mapMeeting(workflow, resource, resourceType)
          .then(() => {
            this.getMeetingList()
          })
      } catch (e) {
        console.log(e)
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
        console.log(e)
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
      } finally {
        setTimeout(() => {
          this.meetingLoading = false
          this.$Alert.alert({
            type: 'success',
            timeout: 2000,
            message: 'Contact Added Successfully',
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
          })
          .then(() => {
            this.getMeetingList()
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.meetingLoading = false
        this.$Alert.alert({
          type: 'success',
          timeout: 2000,
          message: 'Meeting Logged successfully',
          sub: 'No update necessary',
        })
      }
    },
    async updateMeeting(meetingWorkflow, id) {
      this.dropdownLoading = true
      this.currentVals = []
      this.editOpModalOpen = true
      this.updatingMeeting = true
      this.meetingWorkflowId = meetingWorkflow
      this.dropdownVal = {}
      this.formData = {}
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Opportunity',
          formType: 'UPDATE',
          resourceId: id,
        })
        this.currentVals = res.current_values
      } catch (e) {
        console.log(e)
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
        console.log(e)
      } finally {
        this.updatingMeeting = false
        this.meetingLoading = false
        this.$Alert.alert({
          type: 'success',
          timeout: 2000,
          message: 'Meeting Logged successfully',
          sub: 'Opportunity updated',
        })
      }
    },
    async createFormInstance(id, alertInstanceId = null) {
      this.stageGateField = null
      this.dropdownLoading = true
      this.editOpModalOpen = true
      this.currentVals = []
      this.updatingMeeting = false
      this.currentOwner = null
      this.currentAccount = null
      this.alertInstanceId = alertInstanceId
      this.oppId = id
      try {
        const res = await SObjects.api
          .createFormInstance({
            resourceType: 'Opportunity',
            formType: 'UPDATE',
            resourceId: id,
          })
          .then((res) => {
            this.currentVals = res.current_values
            this.instanceId = res.form_id
            this.currentOwner = this.allUsers.filter(
              (user) => user.salesforce_account_ref.salesforce_id === this.currentVals['OwnerId'],
            )[0].full_name
            this.allOpps.filter((opp) => opp.id === this.oppId)[0].account_ref
              ? (this.currentAccount = this.allOpps.filter(
                  (opp) => opp.id === this.oppId,
                )[0].account_ref.name)
              : (this.currentAccount = 'Account')
          })
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
    setUpdateValues(key, val) {
      if (val) {
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
        const res = await SObjects.api
          .updateResource({
            form_id: this.stageGateField ? [this.instanceId, this.stageGateId] : [this.instanceId],
            form_data: this.formData,
            from_workflow: false,
            workflow_title: 'None',
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
        this.createContactForm = this.createContactForm[0].fieldsRef

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
        console.log(error)
      }
    },

    async getUsers() {
      try {
        const res = await SObjects.api.getObjects('User')
        this.allUsers = res.results.filter((user) => user.has_salesforce_integration)
      } catch (e) {
        console.log(e)
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
          console.log(e)
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
        const res = await SObjects.api.getObjects('Opportunity')
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
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.adding-stage-gate {
  border: 2px solid #e8e8e8;
  border-radius: 0.3rem;
  margin: 0.5rem 0rem;
  width: 36vw;
  min-height: 30vh;
  &__header {
    font-size: 11px;
    color: $coral;
    padding: 0.5rem;
    width: 100%;
    border-bottom: 1px solid #e8e8e8;
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
    background-image: linear-gradient(100deg, $darker-green 0%, $lighter-green 99%);
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
  background-image: url('../assets/images/dropdown.svg');
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
  // box-shadow: 1px 1px 2px $very-light-gray;
  border-radius: 0.25rem;
  background-color: white;
  border: 1px solid #e8e8e8;
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
[type='search']::-webkit-search-cancel-button {
  -webkit-appearance: none;
  appearance: none;
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

.table-section {
  margin: 0;
  padding: 0;
  min-height: 78vh;
  max-height: 80vh;
  overflow: scroll;
  margin-top: 0.5rem;
  border-radius: 5px;
  box-shadow: 2px 2px 20px 2px $soft-gray;
  background-color: $off-white;
}

.table {
  display: table;
  overflow: scroll;
  width: 100vw;
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
  width: 40vw;
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
  div {
    margin-right: 0.25rem;
  }
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
  padding-top: 5rem;
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
}
.add-button__ {
  display: flex;
  align-items: center;
  border: none;
  min-height: 4.5vh;
  padding: 0.75rem 1rem;
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
  resize: none;
}
a {
  text-decoration: none;
}
</style>