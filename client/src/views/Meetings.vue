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
          <pre v-html="note.saved_data__meeting_comments" class="note-section__body"></pre>
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
          <p class="note-section__body">No notes for selected Record</p>
        </section>
      </div>
    </Modal>
    <section
      v-if="meetingOpen"
      dimmed
      @close-modal="
        () => {
          //$emit('cancel'), resetMeeting()
        }
      "
    >
      <div class="form-field">
        <span>
          <label for="title">Meeting Title</label>
          <input v-model="meetingTitle" class="zoom-input" type="text" id="title" />
        </span>

        <span>
          <label for="description">Meeting Description</label>
          <textarea v-model="description" class="zoom-input-ta" type="text" id="description" />
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
          <label for="duration">Duration</label>
          <Multiselect
            id="duration"
            placeholder="Duration"
            style="width: 44vw"
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

        <span>
          <label for="internals">Internal Participants</label>
          <Multiselect
            id="internals"
            placeholder="Internal Users"
            style="width: 44vw"
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
          <label for="externals">Externals</label>
          <Multiselect
            id="externals"
            placeholder="External Users"
            style="width: 44vw; margin-bottom: 1rem"
            v-model="externalParticipantsSelected"
            :options="externalParticipants"
            openDirection="above"
            selectLabel="Enter"
            track-by="id"
            :custom-label="externalCustomLabel"
            :multiple="true"
          >
            <template slot="noResult">
              <p class="multi-slot">No results.</p>
            </template>
            <template slot="afterList">
              <p v-if="hasNext" @click="addMoreContacts" class="multi-slot__more">
                Load more <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
              </p>
              <p v-else class="multi-slot__more" style="color: #4d4e4c; cursor: text">
                End of list
              </p>
            </template>
          </Multiselect>
        </span>

        <span>
          <label for="additionals">Additional Users</label>
          <input
            id="additionals"
            :class="
              extraParticipantsSelected.length ? 'zoom-input' : 'light-gray-placeholder zoom-input'
            "
            v-model="extraParticipantsSelected"
            type="text"
            placeholder="Separate emails by commas"
          />
        </span>
      </div>
    </section>

    <div v-if="editOpModalOpen">
      <UpdateForm
        @reset-edit="resetEdit"
        @add-product="addProduct"
        @set-update-values="setUpdateValues"
        @set-template="setTemplate"
        @update-resource="updateResource"
        @update-meeting="onMakeMeetingUpdate"
        @create-product="createProduct"
        @set-create-values="setCreateValues"
        @set-validation-values="setUpdateValidationValues"
        @get-pricebooks="getPricebookEntries"
        @get-accounts="getAccounts"
        @load-more="loadMore"
        @edit-product="editProduct"
        @update-product="updateProduct"
        @cancel-edit-product="cancelEditProduct"
        @set-product-values="setProductValues"
        @go-to-profile="goToProfile"
        :resource="resourceType"
        :productReferenceOpts="productReferenceOpts"
        :fields="resourceFields"
        :currentVals="currentVals"
        :noteTitle="noteTitle"
        :allAccounts="allAccounts"
        :selectedAccount="selectedAccount"
        :hasProducts="hasProducts"
        :allPicklistOptions="apiPicklistOptions"
        :pricebooks="pricebooks"
        :noteValue="noteValue"
        :noteTemplates="noteTemplates"
        :dropdownLoading="dropdownLoading"
        :stageGateField="stageGateField"
        :stagePicklistQueryOpts="stagePicklistQueryOpts"
        :stageValidationFields="stageValidationFields"
        :currentAccount="currentAccount"
        :referenceOpts="currentRefList"
        :loadingAccounts="loadingAccounts"
        :addingProduct="addingProduct"
        :pricebookId="pricebookId"
        :createProductForm="createProductForm"
        :loadingProducts="loadingProducts"
        :savingCreateForm="savingCreateForm"
        :showLoadMore="showLoadMore"
        :currentProducts="currentProducts"
        :editingProduct="editingProduct"
        :productName="productName"
        :savingProduct="savingProduct"
        :currentSelectedProduct="currentSelectedProduct"
        :dropdownProductVal="dropdownProductVal"
        :dropdownVal="dropdownVal"
      />
    </div>

    <div class="alerts-header">
      <div class="results-title">
        <p v-if="!meetingOpen">
          Meetings : <span>{{ meetings.length }}</span>
        </p>

        <button class="back-button" @click="resetMeeting()" v-else>
          <img src="@/assets/images/left.svg" height="12px" alt="" /> Back
        </button>
      </div>

      <h3 v-if="meetingOpen">Create Zoom Meeting</h3>

      <div v-if="!meetingOpen" class="flex-row">
        <div class="tooltip">
          <button @click="refreshCalEvents" class="img-button">
            <img src="@/assets/images/refresh.svg" alt="" style="height: 22px" />
          </button>
          <span class="tooltiptext">Sync Calendar</span>
        </div>

        <button
          @click="resetMeeting()"
          style="margin-left: 8px"
          class="green_button"
          :disabled="!hasZoomIntegration"
        >
          Schedule Zoom
        </button>
      </div>

      <div v-else>
        <button v-if="!submitting" class="green_button" @click="submitZoomMeeting">
          Create Meeting
        </button>
        <div v-else>
          <PipelineLoader />
        </div>
      </div>
    </div>

    <div class="container" ref="pipelines" v-if="!loading && !meetingOpen">
      <div v-if="meetings.length">
        <MeetingWorkflow
          v-for="(meeting, i) in meetings"
          :key="i"
          @map-opp="mapOpp"
          @update-Opportunity="updateMeeting"
          @no-update="noMeetingUpdate"
          @remove-participant="removeParticipant"
          @add-participant="addParticipant"
          @get-notes="getNotes"
          @filter-accounts="getAccounts"
          @change-resource="changeResource"
          :dropdowns="picklistQueryOptsContacts"
          :contactFields="createContactForm"
          :meeting="meeting.meeting_ref"
          :participants="meeting.meeting_ref.participants"
          :workflowId="meeting.id"
          :resourceId="meeting.resource_id"
          :resourceRef="meeting.resource_ref"
          :resourceType="meeting.resource_type ? meeting.resource_type : resourceType"
          :meetingUpdated="meeting.is_completed"
          :owners="allUsers"
          :accounts="allAccounts"
          :meetingLoading="meetingLoading"
          :allOpps="allOpps"
          :allPicklistOptions="allPicklistOptions"
          :referenceOpts="contactCreateReferenceOpts"
          :dropdownLoading="dropdownLoading"
          :accountSobjectId="accountSobjectId"
          :index="i"
        />
      </div>
      <div v-else class="empty-list">
        <section class="bg-img"></section>
        <h3>No meetings found.</h3>
        <p>You may need to sync your calendar</p>
        <button @click="refreshCalEvents" class="green_button">Sync calendar</button>
      </div>
    </div>

    <div v-if="loading">
      <Loader :loaderText="loaderText" />
    </div>
  </div>
</template>
<script>
import { SObjects, MeetingWorkflows } from '@/services/salesforce'
import { ObjectField } from '@/services/crm'
import SlackOAuth from '@/services/slack'
import Zoom from '@/services/zoom/account'
import MeetingWorkflow from '@/components/MeetingWorkflow'
import UpdateForm from '@/components/updateForm/'
import User from '@/services/users'
import { decryptData } from '../encryption'

export default {
  name: 'Meetings',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    SkeletonBox: () => import(/* webpackPrefetch: true */ '@/components/SkeletonBox'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    MeetingWorkflow,
    UpdateForm,
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
    Loader: () => import(/* webpackPrefetch: true */ '@/components/Loader'),
  },
  data() {
    return {
      contactCreateReferenceOpts: {},
      currentSelectedProduct: null,
      savingProduct: null,
      productName: null,
      editingProduct: false,
      productId: null,
      productIntegrationId: null,
      currentProducts: [],
      updateProductData: {},
      resourceType: 'Opportunity',
      resourceFields: null,
      pricebookId: null,
      createData: {},
      productRefCopy: {},
      productReferenceOpts: {},
      page: 1,
      savingCreateForm: false,
      hasNext: false,
      noteTitle: null,
      noteTemplates: null,
      noteValue: null,
      submitting: false,
      meetingOpen: false,
      integrationId: null,
      stageGateField: null,
      stageValidationFields: {},
      stagesWithForms: [],
      dropdownVal: {},
      countSets: 0,
      dropdownLoading: false,
      loadingProducts: false,
      pricebookPage: 1,
      savedPricebookEntryId: '',
      showLoadMore: false,
      updatingMeeting: false,
      meetingWorkflowId: null,
      meetingLoading: null,
      oppId: null,
      updateList: [],
      currentVals: [],
      originalList: null,
      allOpps: null,
      loading: false,
      stagePicklistQueryOpts: {},
      currentWorkflow: null,
      selectedWorkflow: false,
      modalOpen: false,
      editOpModalOpen: false,
      loadingAccounts: false,
      accountSobjectId: null,
      currentAccount: null,
      selectedAccount: null,
      updateOppForm: [],
      oppFormCopy: null,
      createContactForm: null,
      updateContactForm: null,
      updateAccountForm: null,
      updateLeadForm: null,
      formData: {},
      picklistQueryOptsContacts: {},
      allAccounts: null,
      allUsers: null,
      createProductForm: null,
      referenceOpts: {},
      accountReferenceOpts: {},
      contactReferenceOpts: {},
      leadReferenceOpts: {},
      currentRefList: null,
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
      notes: [],
      notesLength: 0,
      addingProduct: false,
      stageGateCopy: null,
      stageReferenceOpts: {},
      days: {
        0: 'Sunday',
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
      },
      loaderText: 'Pulling in your meetings',
    }
  },
  computed: {
    user() {
      const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return decryptedUser
    },
    userCRM() {
      const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return decryptedUser.crm
    },
    hasZoomIntegration() {
      const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!decryptedUser.zoomAccount && decryptedUser.hasZoomIntegration
    },
    hasProducts() {
      const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return decryptedUser.organizationRef.hasProducts
    },
    meetings() {
      return this.$store.state.meetings
    },
    allPicklistOptions() {
      return this.$store.state.allPicklistOptions
    },
    apiPicklistOptions() {
      if (this.userCRM === 'HUBSPOT') {
        return this.getHubspotOptions()
      } else {
        return this.$store.state.apiPicklistOptions
      }
    },
    pricebooks() {
      return this.$store.state.pricebooks
    },
  },
  created() {
    // this.resourceType = this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal'
    this.getAllForms()
  },
  beforeMount() {
    this.getUsers()
    this.getExternalParticipants()
  },
  mounted() {
    this.getTemplates()
  },
  watch: {
    accountSobjectId: 'getInitialAccounts',
    updateOppForm: ['setForms', 'filtersAndOppFields'],
    stageGateField: 'stageGateInstance',
    resourceType: ['selectFormFields'],
  },
  methods: {
    // resourceSelect(resType) {
    //   let i = 'Opportunity'
    //   resType !== this.resourceType ? i = this.resourceType : i = resType
    //   return i
    // },
    async getHubspotOptions() {
      let stages = []
      if (this.userCRM === 'HUBSPOT') {
        try {
          let res = await ObjectField.api.listFields({
            crmObject: this.DEAL,
            search: 'Deal Stage',
          })
          let dealStages = []
          for (let i = 0; i < res.length; i++) {
            if (res[i].apiName === 'dealstage') {
              dealStages = res[i]
              break
            }
          }
          let dealStage = []
          if (dealStages.optionsRef.length) {
            for (let i = 0; i < dealStages.optionsRef.length; i++) {
              dealStage = [...dealStage, ...dealStages.optionsRef[i]]
            }
          }
          return dealStage && dealStage.length ? dealStage : []
        } catch (e) {
          console.log(e)
        }
      }
      return stages
    },
    cancelEditProduct() {
      this.dropdownProductVal = {}
      this.editingProduct = !this.editingProduct
    },
    editProduct(integrationId, id, name, secondaryData) {
      this.editingProduct = true
      this.productIntegrationId = integrationId
      this.productId = id
      this.productName = name
      this.currentSelectedProduct = secondaryData
    },
    changeResource(i) {
      this.resourceType = i
    },
    selectFormFields() {
      switch (this.resourceType) {
        case 'Opportunity':
          this.resourceFields = this.oppFormCopy
          this.currentRefList = this.referenceOpts
          break
        case 'Account':
          this.resourceFields = this.updateAccountForm
          this.currentRefList = this.accountReferenceOpts
          break
        case 'Contact':
          this.resourceFields = this.updateContactForm
          this.currentRefList = this.contactReferenceOpts
          break
        case 'Lead':
          this.resourceFields = this.updateLeadForm
          this.currentRefList = this.leadReferenceOpts
          break
        default:
          return
      }
    },
    async getTemplates() {
      try {
        const res = await User.api.getTemplates()
        this.noteTemplates = res.results
      } catch (e) {
        console.log(e)
      }
    },
    setTemplate(val, field, title) {
      this.noteTitle = title
      this.noteValue = val
      this.setUpdateValues(field, val)
      this.setUpdateValues('meeting_type', title ? title : null)
    },
    addProduct() {
      this.addingProduct = !this.addingProduct
    },
    resetMeeting() {
      this.clearData()
      this.meetingOpen = !this.meetingOpen
    },
    async submitZoomMeeting() {
      this.submitting = true
      if (
        !this.meetingTitle ||
        !this.startDate ||
        !this.startTime ||
        !this.meetingDuration ||
        !this.externalParticipantsSelected
      ) {
        this.$toast('Please input all information', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.submitting = false
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
        this.$toast('Please add participants to the meeting', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.submitting = false
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
      } finally {
        this.submitting = false
        this.resetMeeting()
      }
    },
    setCreateValues(key, val) {
      if (val) {
        this.createData[key] = val
      }
    },
    async createProduct(id = this.integrationId) {
      if (this.addingProduct) {
        try {
          const res = await SObjects.api.createResource({
            integration_ids: [id],
            form_type: 'CREATE',
            resource_type: 'OpportunityLineItem',
            // stage_name: this.stageGateField ? this.stageGateField : null,
            resource_id: this.oppId,
            form_data: this.createData,
          })

          this.$toast('Product created successfully', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } catch (e) {
          this.$toast(`${e.response.data.error}`, {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } finally {
          this.addingProduct = !this.addingProduct
        }
      } else {
        return
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
    async getReferenceFieldList(key, val, type, eventVal) {
      try {
        const res = await SObjects.api.getSobjectPicklistValues({
          sobject_id: val,
          value: eventVal ? eventVal : '',
        })
        if (type === 'update') {
          this.referenceOpts[key] = res
        } else if (type === 'createProduct') {
          this.productReferenceOpts[key] = res
        } else if (type === 'updateAccount') {
          this.accountReferenceOpts[key] = res
        } else if (type === 'updateContact') {
          this.contactReferenceOpts[key] = res
        } else if (type === 'createContact') {
          this.contactCreateReferenceOpts[key] = res
        } else if (type === 'updateLead') {
          this.leadReferenceOpts[key] = res
        }
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
        this.loaderText = 'Pulling your calendar events...'
        setTimeout(() => {
          this.loaderText = `Mapping to ${
            this.userCRM === 'SALESFORCE' ? 'Salesforce' : 'Hubspot'
          }...`
          this.getMeetingList()
          setTimeout(() => {
            this.loading = false
            this.loaderText = 'Pulling in your meetings'
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
          }, 3000)
        }, 2000)
      }
    },
    async getMeetingList() {
      try {
        this.$store.dispatch('loadMeetings')
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
        let newResourceType = resourceType
        if (newResourceType === 'Opportunity') {
          newResourceType = this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal'
        }
        const res = await MeetingWorkflows.api
          .mapMeeting(workflow, resource, newResourceType)
          .then(() => {
            this.$store.dispatch('loadMeetings')
          })
      } catch (e) {
        this.$toast('Error mapping record', {
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
          this.$store.dispatch('loadMeetings')
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
            this.$store.dispatch('loadMeetings')
          })
      } catch (e) {
        console.log(e)
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
    goToProfile() {
      this.$router.push({ name: 'InviteUsers' })
    },
    resetEdit() {
      this.editOpModalOpen = !this.editOpModalOpen
    },
    async noMeetingUpdate(meetingWorkflow) {
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
          .then((res) => {
            this.$store.dispatch('loadMeetings')
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
    async updateProduct() {
      this.savingProduct = true
      try {
        const res = await SObjects.api
          .updateResource({
            form_data: this.updateProductData,
            from_workflow: this.selectedWorkflow,
            workflow_title: this.selectedWorkflow ? this.currentWorkflowName : 'None',
            form_type: 'UPDATE',
            integration_ids: [this.productIntegrationId],
            resource_type: 'OpportunityLineItem',
            resource_id: this.productId,
            stage_name: null,
          })
          .then(async (res) => {
            const res2 = await SObjects.api.getCurrentValues({
              resourceType: 'Opportunity',
              resourceId: this.oppId,
            })
            this.currentProducts = res2.current_products
          })
        this.$toast('Product updated successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        this.$toast('Error updating Product', {
          timeout: 1500,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.editingProduct = false
        this.savingProduct = false
      }
    },
    async updateMeeting(resourceType, meetingWorkflow, id, integrationId, pricebookId) {
      this.resourceType = resourceType
      pricebookId ? (this.pricebookId = pricebookId) : (this.pricebookId = null)
      this.dropdownLoading = true
      this.currentVals = []
      this.editOpModalOpen = true
      this.updatingMeeting = true
      this.meetingWorkflowId = meetingWorkflow
      this.dropdownVal = {}
      this.formData = {}
      this.createData = {}
      this.oppId = id
      this.integrationId = integrationId
      this.noteValue = null
      this.noteTitle = null
      this.addingProduct = false
      this.updateProductData = {}
      this.productId = null
      this.productIntegrationId = null
      this.dropdownProductVal = {}
      this.editingProduct = false
      try {
        const res = await SObjects.api.getCurrentValues({
          resourceType: resourceType,
          resourceId: id,
        })
        this.currentVals = res.current_values
        this.currentProducts = res.current_products
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
        pricebookId ? this.getPricebookEntries(pricebookId) : null
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
            this.$store.dispatch('loadMeetings')
          })
        this.$toast('Meeting logged Successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        this.$toast(`${e.response.data.error}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.updatingMeeting = false
        this.meetingLoading = false
      }
    },
    async loadMore() {
      if (!this.savedPricebookEntryId) {
        return
      }
      try {
        this.loadingProducts = true
        this.savedProductedReferenceOps = [...this.productReferenceOpts['PricebookEntryId']]
        const res = await SObjects.api.getObjects('PricebookEntry', this.pricebookPage, true, [
          ['EQUALS', 'Pricebook2Id', this.savedPricebookEntryId],
        ])
        this.productReferenceOpts['PricebookEntryId'] = [
          ...res.results,
          ...this.savedProductedReferenceOps,
        ]
        if (res.next) {
          this.pricebookPage++
          this.showLoadMore = true
        } else {
          this.showLoadMore = false
        }
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.loadingProducts = false
        }, 1000)
      }
    },
    async getPricebookEntries(id) {
      try {
        this.loadingProducts = true
        const res = await SObjects.api.getObjects('PricebookEntry', 1, true, [
          ['EQUALS', 'Pricebook2Id', id],
        ])
        this.productReferenceOpts['PricebookEntryId'] = res.results
        this.productList = res.results
        if (res.next) {
          this.pricebookPage++
          this.showLoadMore = true
        } else {
          this.pricebookPage = 1
          this.showLoadMore = false
        }
        this.savedPricebookEntryId = id
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.loadingProducts = false
        }, 1000)
      }
    },
    setUpdateValues(key, val, multi = null) {
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
    setProductValues(key, val) {
      if (val) {
        this.updateProductData[key] = val
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
        this.$toast(`${e.response.data.error}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    setForms() {
      this.countSets += 1
      if (this.countSets < 2) {
        for (let i = 0; i < this.oppFormCopy.length; i++) {
          if (this.oppFormCopy[i].dataType === 'Reference') {
            this.referenceOpts[this.oppFormCopy[i].apiName] = this.oppFormCopy[i].id
            this.currentRefList = this.referenceOpts
          }
        }
        for (let i = 0; i < this.updateContactForm.length; i++) {
          if (this.updateContactForm[i].dataType === 'Reference') {
            this.contactReferenceOpts[this.updateContactForm[i].apiName] =
              this.updateContactForm[i].id
          }
        }
        for (let i = 0; i < this.createContactForm.length; i++) {
          if (this.createContactForm[i].dataType === 'Reference') {
            this.contactCreateReferenceOpts[this.createContactForm[i].apiName] =
              this.createContactForm[i].id
          }
        }

        if (this.stageGateCopy) {
          for (let i = 0; i < this.stageGateCopy.length; i++) {
            if (this.stageGateCopy[i].dataType === 'Reference') {
              this.stageReferenceOpts[this.stageGateCopy[i].apiName] = this.stageGateCopy[i].id
            }
          }
        }
        for (let i = 0; i < this.updateAccountForm.length; i++) {
          if (this.updateAccountForm[i].dataType === 'Reference') {
            this.accountReferenceOpts[this.updateAccountForm[i].apiName] =
              this.updateAccountForm[i].id
          }
        }
        for (let i = 0; i < this.updateLeadForm.length; i++) {
          if (this.updateLeadForm[i].dataType === 'Reference') {
            this.leadReferenceOpts[this.updateLeadForm[i].apiName] = this.updateLeadForm[i].id
          }
        }

        if (this.hasProducts) {
          for (let i = 0; i < this.createProductForm.length; i++) {
            if (this.createProductForm[i].dataType === 'Reference') {
              this.productRefCopy[this.createProductForm[i].apiName] = this.createProductForm[i]
              this.productReferenceOpts[this.createProductForm[i].apiName] =
                this.createProductForm[i].id
            }
          }
        }

        for (let i in this.referenceOpts) {
          this.referenceOpts[i] = this.getReferenceFieldList(i, this.referenceOpts[i], 'update')
        }
        if (this.stageReferenceOpts) {
          for (let i in this.stageReferenceOpts) {
            this.stageReferenceOpts[i] = this.getReferenceFieldList(
              i,
              this.stageReferenceOpts[i],
              'stage',
            )
          }
        }
        for (let i in this.accountReferenceOpts) {
          this.accountReferenceOpts[i] = this.getReferenceFieldList(
            i,
            this.accountReferenceOpts[i],
            'updateAccount',
          )
        }
        for (let i in this.contactReferenceOpts) {
          this.contactReferenceOpts[i] = this.getReferenceFieldList(
            i,
            this.contactReferenceOpts[i],
            'updateContact',
          )
        }

        for (let i in this.contactCreateReferenceOpts) {
          this.contactCreateReferenceOpts[i] = this.getReferenceFieldList(
            i,
            this.contactCreateReferenceOpts[i],
            'createContact',
          )
        }

        for (let i in this.leadReferenceOpts) {
          this.leadReferenceOpts[i] = this.getReferenceFieldList(
            i,
            this.leadReferenceOpts[i],
            'updateLead',
          )
        }

        if (this.hasProducts) {
          for (let i in this.productReferenceOpts) {
            this.productReferenceOpts[i] = this.getReferenceFieldList(
              i,
              this.productReferenceOpts[i],
              'createProduct',
            )
          }
        }
      }
    },
    filtersAndOppFields() {
      if (this.updateOppForm[0]) {
        this.updateOppForm[0].fieldsRef.filter((field) => field.apiName === 'AccountId').length
          ? (this.accountSobjectId = this.updateOppForm[0].fieldsRef.filter(
              (field) => field.apiName === 'AccountId',
            )[0].id)
          : (this.accountSobjectId = null)
      }
    },
    async getAllForms() {
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()

        this.updateOppForm =
          this.userCRM === 'SALESFORCE'
            ? res.filter((obj) => obj.formType === 'UPDATE' && obj.resource === 'Opportunity')
            : res.filter((obj) => obj.formType === 'UPDATE' && obj.resource === 'Deal')

        let stageGateForms =
          this.userCRM === 'SALESFORCE'
            ? res.filter((obj) => obj.formType === 'STAGE_GATING' && obj.resource === 'Opportunity')
            : res.filter((obj) => obj.formType === 'STAGE_GATING' && obj.resource === 'Deal')
        this.createContactForm = res.filter(
          (obj) => obj.formType === 'CREATE' && obj.resource === 'Contact',
        )[0]
        this.createContactForm = this.createContactForm ? this.createContactForm.fieldsRef : []
        this.updateContactForm = res.filter(
          (obj) => obj.formType === 'UPDATE' && obj.resource === 'Contact',
        )[0]
        this.updateContactForm = this.updateContactForm ? this.updateContactForm.fieldsRef : []
        this.updateAccountForm =
          this.userCRM === 'SALESFORCE'
            ? res.filter((obj) => obj.formType === 'UPDATE' && obj.resource === 'Account')[0]
                .fieldsRef
            : res.filter((obj) => obj.formType === 'UPDATE' && obj.resource === 'Company')[0]
                .fieldsRef
        this.updateLeadForm = res.filter(
          (obj) => obj.formType === 'UPDATE' && obj.resource === 'Lead',
        )[0]
        this.updateLeadForm = this.updateLeadForm ? this.updateLeadForm.fieldsRef : []
        this.createProductForm = res.filter(
          (obj) => obj.formType === 'CREATE' && obj.resource === 'OpportunityLineItem',
        )[0]
        this.createProductForm = this.createProductForm ? this.createProductForm.fieldsRef : []

        let stages = stageGateForms.map((field) => field.stage)
        this.stagesWithForms = stages
        this.oppFormCopy = this.updateOppForm[0] ? this.updateOppForm[0].fieldsRef : []
        this.resourceFields = this.updateOppForm[0] ? this.updateOppForm[0].fieldsRef : []
        this.stageGateCopy = stageGateForms[0] ? stageGateForms[0].fieldsRef : []

        for (const field of stageGateForms) {
          this.stageValidationFields[field.stage] = field.fieldsRef
        }

        // let stageArrayOfArrays = stageGateForms.map((field) => field.fieldsRef)
        // let allStageFields = [].concat.apply([], stageArrayOfArrays)
        // let dupeStagesRemoved = [
        //   ...new Map(allStageFields.map((v) => [v.referenceDisplayLabel, v])).values(),
        // ]

        // for (let i = 0; i < dupeStagesRemoved.length; i++) {
        //   if (
        //     dupeStagesRemoved[i].dataType === 'Picklist' ||
        //     dupeStagesRemoved[i].dataType === 'MultiPicklist'
        //   ) {
        //     this.stagePicklistQueryOpts[dupeStagesRemoved[i].apiName] = dupeStagesRemoved[i].apiName
        //   } else if (dupeStagesRemoved[i].dataType === 'Reference') {
        //     this.stagePicklistQueryOpts[dupeStagesRemoved[i].referenceDisplayLabel] =
        //       dupeStagesRemoved[i].referenceDisplayLabel
        //   }
        // }
      } catch (error) {
        // this.$toast('Error setting forms', {
        //   timeout: 2000,
        //   position: 'top-left',
        //   type: 'error',
        //   toastClassName: 'custom',
        //   bodyClassName: ['custom'],
        // })
        console.log(error)
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
    async addMoreContacts() {
      this.page += 1
      try {
        const res = await SObjects.api.getObjects('Contact', this.page)
        this.externalParticipants = [...res.results, ...this.externalParticipants]
        res.next ? (this.hasNext = true) : (this.hasNext = false)
      } catch (e) {
        console.log(e)
      }
    },
    async getExternalParticipants() {
      try {
        const res = await SObjects.api.getObjects('Contact')
        this.externalParticipants = res.results
        res.next ? (this.hasNext = true) : (this.hasNext = false)
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
        const res = await SObjects.api.getObjectsForWorkflows(this.resourceType)
        this.allOpps = res.results
        this.originalList = res.results
      } catch (e) {
        console.log(e)
      } finally {
        this.loading = false
      }
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

.form-field {
  display: flex;
  align-items: flex-start;
  justify-content: space-evenly;
  flex-direction: column;
  gap: 12px;
  border-radius: 6px;
  background-color: white;
  // border: 1px solid #e8e8e8;
  box-shadow: 1px 1px 2px 1px rgba($very-light-gray, 50%);
  padding: 2rem;
  width: 50vw;
  color: $base-gray;
  letter-spacing: 0.75px;
  label {
    color: $light-gray-blue;
    font-size: 14px;
    margin-bottom: 4px;
  }

  &__footer {
    font-size: 12px;
  }
  span {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }
}
.container {
  min-height: 85vh;
  padding: 16px 0px;
  width: 40vw;
  outline: 1px solid $soft-gray;
  border-radius: 8px;
  background-color: white;
}
.back-button {
  color: $base-gray;
  background-color: transparent;
  display: flex;
  align-items: center;
  border: none;
  cursor: pointer;
  font-size: 16px;
  letter-spacing: 0.75px;

  img {
    margin-right: 8px;
  }
}
#container {
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  background-color: $base-gray;
  opacity: 0.4;
  z-index: 10;
  border-radius: 8px;
}
#calendar {
  z-index: 11;
  color: white;
  position: absolute;
  bottom: 50%;
  left: 40%;
  font-size: 24px;
}
.alerts-header {
  position: fixed;
  z-index: 10;
  top: 0;
  left: 60px;
  background-color: white;
  width: 96vw;
  border-bottom: 1px solid $soft-gray;
  padding: 8px 32px 0px 8px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  // gap: 24px;

  h3 {
    font-size: 16px;
    font-weight: 400;
    letter-spacing: 0.75px;
    line-height: 1.2;
    cursor: pointer;
    color: $light-gray-blue;
  }
}
.empty-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: $light-gray-blue;
  letter-spacing: 0.76px !important;

  .bg-img {
    background-image: url(../assets/images/logo.png);
    background-repeat: no-repeat;
    background-size: contain;
    background-position: center;
    height: 72px;
    width: 120px;
    opacity: 0.5;
  }
  h3 {
    color: $base-gray;
    margin-bottom: 0;
    margin-top: 12px;
  }
  p {
    font-size: 13px;
  }
}

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
:disabled {
  color: $base-gray !important;
  background-color: $soft-gray !important;
  max-height: 2rem;
  border-radius: 0.25rem;
  padding: 0.5rem 1.25rem;
  font-size: 12px;
  border: none;
  cursor: pointer;
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
.results-title {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  margin-left: 4px;

  p {
    font-size: 16px;
    margin-left: 2px;
    color: $base-gray;
    span {
      // background-color: $white-green;
      color: $light-gray-blue;
      border-radius: 6px;
      padding: 2px;
      margin-left: 4px;
      font-size: 14px;
    }
  }
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
.modal-container {
  background-color: $white;
  overflow: auto;
  min-width: 36vw;
  max-width: 36vw;
  min-height: 44vh;
  max-height: 80vh;
  align-items: center;
  border-radius: 0.5rem;
  border: 1px solid #e8e8e8;
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
  padding-top: 8px;
  padding-bottom: 0;
}
.flex-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.pipelines {
  color: $base-gray;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-left: 80px;
  margin-top: 12vh;
}
.invert {
  filter: invert(85%);
}
.zoom-input {
  border: 1px solid $soft-gray;
  border-radius: 6px;
  padding: 12px 8px;

  width: 44vw;
  font-family: inherit;
}
.zoom-input-ta {
  border: 1px solid $soft-gray;
  border-radius: 6px;
  height: 80px;
  padding: 8px;
  width: 44vw;
  font-family: inherit;
  resize: none;
}
textarea {
  resize: vertical;
}
a {
  text-decoration: none;
}
.green_button {
  @include primary-button();
  max-height: 2rem;
  padding: 0.5rem 1.25rem;
  font-size: 12px;
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
.light-gray-placeholder::placeholder {
  color: #adadad;
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
  // border: 1px solid $soft-gray;
  letter-spacing: 0.5px;
  padding: 8px 4px;
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
.img-button {
  background-color: transparent;
  padding: 4px 6px;
  border: none;
}
</style>