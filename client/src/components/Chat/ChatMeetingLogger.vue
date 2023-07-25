<template>
  <section class="meetings">
    <div
      v-if="
        !hasMeetingWorkflow || (selectedMeetingWorkflow && !selectedMeetingWorkflow.forms.length)
      "
      :class="{ disabled: submitting }"
    >
      <div class="margin-top-s">
        <p @click="test">Related to type:</p>

        <Multiselect
          v-model="selectedResourceType"
          selectLabel=""
          deselectLabel=""
          :options="resources"
          :loading="dropdownLoading"
          style="width: 96%"
          :disabled="submitting"
        >
        </Multiselect>
      </div>

      <div class="margin-top">
        <p>Search for a {{ selectedResourceType }}:</p>

        <Multiselect
          style="width: 96%"
          v-model="mappedOpp"
          @select="selectOpp($event)"
          @search-change="setSearchVal($event)"
          :placeholder="`Search for ${selectedResourceType || ''}`"
          selectLabel=""
          deselectLabel=""
          label="name"
          :customLabel="({ name, email }) => (name ? name : email)"
          track-by="id"
          :options="
            selectedResourceType === 'Opportunity' || selectedResourceType === 'Deal'
              ? allOpps
              : selectedList
          "
          :loading="dropdownLoading || listLoading"
          :disabled="!selectedResourceType || submitting"
        >
          <template slot="noResult">
            <p class="multi-slot">No results. Try loading more</p>
            <button @click="loadMoreOpps(mappedOpp)" class="multi-slot__more">Load more</button>
          </template>
        </Multiselect>
      </div>

      <div class="margin-top">
        <p>Use AI to summarize & auto-fill CRM?</p>

        <Multiselect
          v-model="usingAi"
          selectLabel=""
          deselectLabel=""
          label="name"
          track-by="value"
          style="width: 96%"
          :options="aiOptions"
          :loading="dropdownLoading"
          :disabled="!mappedOpp || submitting"
        >
        </Multiselect>
      </div>

      <div v-if="errorText" class="margin-top">
        <p class="error">{{ errorText }}</p>
      </div>

      <p v-if="processing" class="row__ gray-text smaller">
        <img class="rotate" src="@/assets/images/loading.svg" height="14px" alt="" /> Processing
        transcript, this could take a few minutes...
      </p>
    </div>

    <div v-else-if="selectedMeetingWorkflow && selectedMeetingWorkflow.forms.length">
      <div v-if="selectedMeetingWorkflow.forms[0].update_source === 'transcript'">
        <!-- selectedMeetingWorkflow.is_completed && -->
        <div
          v-if="
            !(selectedMeetingWorkflow.forms[0] && selectedMeetingWorkflow.forms[0].is_submitted) &&
            !updatingMeeting
          "
        >
          <div class="opp-row">
            <p class="logged">Summary</p>
            <button @click="toggleUpdateMeeting" class="view-opp-button">
              Review & Update {{ this.user.crm === 'HUBSPOT' ? 'HubSpot' : 'Salesforce' }}
            </button>
          </div>

          {{ selectedMeetingWorkflow.transcript_summary }}
          <div>
            <p class="logged-blue">Analysis</p>
            <pre class="message-text" v-html="selectedMeetingWorkflow.transcript_analysis"></pre>
          </div>
        </div>

        <div
          v-else-if="
            !(selectedMeetingWorkflow.forms[0] && selectedMeetingWorkflow.forms[0].is_submitted) &&
            updatingMeeting
          "
        >
          <div :class="{ disabled: submitting }" v-for="(field, i) in formFields" :key="i">
            <ChatMeetingFormField
              :placeholder="toString(updateData[field.apiName])"
              :field="field"
              :chatData="updateData"
              @set-value="setUpdateValues"
              :stageFields="stageFields"
              :stagesWithForms="stagesWithForms"
              :hubspotStages="
                user.crm === 'HUBSPOT'
                  ? selectedMeetingWorkflow.resource_ref.secondary_data.pipeline
                  : []
              "
            />
          </div>
          <div class="meeting-modal-footer">
            <button @click="toggleUpdateMeeting">Cancel</button>
            <button @click="onSubmitChat" class="green-button" :disabled="submitting">
              Log Meeting
            </button>
          </div>
        </div>

        <div v-else>
          <div class="opp-row">
            <p class="logged">
              <img src="@/assets/images/check.svg" height="12px" alt="" /> meeting logged
            </p>

            <button @click="viewOpp" class="view-opp-button">
              View {{ selectedMeetingWorkflow.resource_ref.name }}
            </button>
          </div>

          <p>{{ selectedMeetingWorkflow.transcript_summary }}</p>
          <div>
            <p class="logged-blue">Analysis</p>
            <pre class="message-text" v-html="selectedMeetingWorkflow.transcript_analysis"></pre>
          </div>
        </div>
      </div>

      <div v-else>
        <div v-if="!selectedMeetingWorkflow.is_completed">
          <div :class="{ disabled: submitting }" v-for="(field, i) in formFields" :key="i">
            <ChatMeetingFormField
              :placeholder="toString(updateData[field.apiName])"
              :field="field"
              :chatData="updateData"
              @set-value="setUpdateValues"
              :stageFields="stageFields"
              :stagesWithForms="stagesWithForms"
              :hubspotStages="
                user.crm === 'HUBSPOT'
                  ? selectedMeetingWorkflow.resource_ref.secondary_data.pipeline
                  : []
              "
            />
          </div>
          <div class="meeting-modal-footer">
            <button @click="onSubmitChat" class="green-button" :disabled="submitting">
              Log Meeting
            </button>
          </div>
        </div>

        <div v-else>
          <div class="opp-row">
            <p class="logged">
              <img src="@/assets/images/check.svg" height="12px" alt="" /> meeting logged
            </p>
            <button @click="viewOpp" class="view-opp-button">
              View {{ selectedMeetingWorkflow.resource_ref.name }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!hasMeetingWorkflow">
      <div class="meeting-modal-footer">
        <button
          @click="deselectMeeting"
          v-if="selectedResourceId && usingAi"
          :disabled="submitting"
        >
          Cancel
        </button>

        <button
          @click="submitChatMeeting"
          class="green-button"
          v-if="selectedResourceId && usingAi && usingAi.value === 'false'"
          :disabled="submitting"
        >
          Submit
        </button>

        <button
          @click="submitChatTranscript"
          class="green-button"
          v-if="selectedResourceId && usingAi && usingAi.value === 'true'"
          :disabled="submitting"
        >
          Submit
        </button>
      </div>
    </div>

    <!-- <div class="meeting-modal-footer">
      <button
        @click="submitChatMeeting"
        class="green-button"
        v-if="selectedResourceId && usingAi && usingAi.value === 'false'"
        :disabled="submitting"
      >
        Log Meeting
      </button>

      <button
        @click="submitChatTranscript"
        class="green-button"
        v-if="selectedResourceId && usingAi && usingAi.value === 'true'"
        :disabled="submitting"
      >
        Log Meeting
      </button>
    </div> -->
  </section>
</template>

<script>
import User from '@/services/users'
import Modal from '@/components/InviteModal'
import ChatMeetingFormField from '@/components/Chat/ChatMeetingFormField.vue'
import SlackOAuth from '@/services/slack'
import { MeetingWorkflows } from '@/services/salesforce'

export default {
  name: 'ChatMeetingLogger',
  components: {
    Modal,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    ChatMeetingFormField,
  },
  props: {
    meeting: {},
    workflows: {},
    formFields: {},
    stageFields: {},
    stagesWithForms: {},
    meetingOpp: {},
  },
  watch: {
    // usingAi(val) {
    //   if (val && val.value === 'false') {
    //     this.submitChatMeeting()
    //   } else if (val && val.value === 'true') {
    //     this.submitChatTranscript()
    //   }
    // },
    selectedResourceType: 'changeList',
    searchValue(newVal, oldVal) {
      if (newVal !== oldVal && newVal !== '') {
        return
      } else {
        this.$store.dispatch('loadChatOpps')
        this.page = 0
        this.loadMorePage = 0
      }
    },
    selectedTemplate: 'addTemplate',
  },
  data() {
    return {
      updatingMeeting: false,
      textLoading: null,
      listLoading: false,
      loading: false,
      chatModalOpen: false,
      processing: false,
      stageGateId: [],
      errorText: null,
      meetingModalOpen: false,
      reviewTranscript: false,
      submitting: false,
      currentMeeting: null,
      mappedOpp: null,
      dropdownLoading: false,
      loadMorePage: 0,
      searchValue: null,
      usingAi: null,
      selectedResourceId: null,
      selectedResourceType: null,
      selectedMeetingWorkflow: null,
      selectedList: [],
      noteValue: null,
      selectedTemplate: null,
      prompt: null,
      updateData: {},
      currentMeetingName: null,
      currentAnalysis: null,
      currentResourceId: null,
      currentIntegrationId: null,
      currentResourceType: null,
      currentMeetingId: null,
      analysisModalOpen: false,
      aiOptions: [
        {
          name: 'Yes',
          value: 'true',
        },
        {
          name: 'No',
          value: 'false',
        },
      ],
    }
  },
  methods: {
    test() {
      console.log(this.currentOpp)
    },
    deselectMeeting() {
      this.$emit('deselect-meeting')
    },
    toggleUpdateMeeting() {
      this.updatingMeeting = !this.updatingMeeting
    },
    viewOpp() {
      this.$emit('select-opp', this.selectedMeetingWorkflow.resource_ref)
    },
    deselectAI() {
      this.usingAi = null
    },
    toggleAnalysisModal(name, analysis) {
      this.analysisModalOpen = !this.analysisModalOpen

      if (name) {
        this.currentMeetingName = name
        this.$emit('set-opp', name)
      }

      if (analysis) {
        this.currentAnalysis = analysis
      }
    },

    async submitChatTranscript() {
      this.submitting = true
      this.processing = true
      this.meetingModalOpen = false
      try {
        await User.api
          .submitChatTranscript({
            user_id: this.user.id,
            resource_type: this.selectedResourceType,
            resource_id: this.mappedOpp.id,
            integration_id: this.mappedOpp.integration_id,
            meeting_id: this.meeting.id,
          })
          .then((response) => {
            if (response.status === 200) {
              setTimeout(() => {
                this.$emit('reload-workflows')
              }, 1500)
            } else {
              this.errorText = response.data
              this.selectedResourceType = null
              this.mappedOpp = null
              this.usingAi = null
            }
          })
      } catch (e) {
        console.log(e)
        this.errorText =
          'No transcript found for this meeting. Try again later or continue without using AI.'
        this.selectedResourceType = null
        this.mappedOpp = null
        this.usingAi = null
      } finally {
        this.submitting = false
        this.processing = false
      }
    },
    toString(data) {
      let type = typeof data
      if (type === 'number') {
        let newData = data.toString()
        return newData
      } else {
        return data
      }
    },
    removeSpacesFromKeys(obj) {
      const newObj = {}

      for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
          const newKey = key.replace(/\s/g, '') // Remove spaces from the key
          newObj[newKey] = obj[key] // Create a new key-value pair
          if (key !== newKey) {
            delete obj[key] // Delete the old key
          }
        }
      }

      return newObj
    },

    async onSubmitChat() {
      this.submitting = true
      try {
        await MeetingWorkflows.api
          .updateWorkflow({
            workflow_id: this.selectedMeetingWorkflow.id,
            stage_form_id: this.stageGateId,
            form_data: this.updateData,
          })
          .then((response) => {
            setTimeout(() => {
              this.$emit('reload-workflows')
            }, 10000)
          })
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.submitting = false
        }, 11000)
      }
    },
    setUpdateValues(key, val, multi) {
      if (multi) {
        this.updateData[key] = this.updateData[key]
          ? this.updateData[key] + ';' + val
          : val.split(/&#39;/g)[0]
      } else {
        this.updateData[key] = val
      }
    },
    setValue(e) {
      this.prompt = e.target.textContent
    },
    changeList() {
      if (this.selectedResourceType === 'Account' || this.selectedResourceType === 'Company') {
        this.$store.dispatch('loadAllAccounts')
        this.listLoading = true
        setTimeout(() => {
          this.selectedList = this.allAccounts
          this.listLoading = false
        }, 2000)
      } else if (this.selectedResourceType === 'Contact') {
        this.$store.dispatch('loadAllContacts')

        this.listLoading = true
        setTimeout(() => {
          this.selectedList = this.allContacts
          this.listLoading = false
        }, 2000)
      } else if (this.selectedResourceType === 'Lead') {
        this.$store.dispatch('loadAllLeads')

        setTimeout(() => {
          this.selectedList = this.allLeads
          this.listLoading = false
        }, 2000)
      }
    },
    async submitChatMeeting() {
      this.submitting = true
      try {
        let res = await User.api
          .submitChatMeeting({
            user_id: this.user.id,
            meeting_id: this.meeting.id,
            resource_id: this.mappedOpp.id,
            resource_type: this.selectedResourceType,
          })
          .then((response) => {
            this.$emit('reload-workflows')
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.submitting = false
      }
    },
    async loadMoreOpps() {
      this.loadMorePage += 1
      this.dropdownLoading = true
      try {
        let res = await this.$store.dispatch('loadMoreChatOpps', {
          page: this.loadMorePage,
          text: this.searchValue,
        })
      } catch (e) {
        console.log(e)
        this.loadMorePage = 0
      } finally {
        setTimeout(() => {
          this.dropdownLoading = false
          this.loadMorePage = 0
        }, 500)
      }
    },
    setSearchVal(val) {
      this.searchValue = val
    },
    logMeeting(meeting) {
      this.currentMeeting = meeting
      this.toggleMeetingModal()
    },
    toggleMeetingModal() {
      this.meetingModalOpen = !this.meetingModalOpen

      this.mappedOpp = null
      this.usingAi = null
      this.selectedResourceId = null
      this.selectedResourceType = null
      this.noteValue = null
    },
    refreshUser() {
      User.api
        .getUser(this.user.id)
        .then((user) => {
          this.$store.dispatch('updateUser', user)
          return user
        })
        .catch(() => {
          // do nothing for now
          return null
        })
    },
    async refreshCalEvents() {
      this.loading = true
      try {
        let res = await User.api.refreshCalendarEvents()
      } catch (e) {
        console.log('Error in refreshCalEvents: ', e)
      } finally {
        setTimeout(() => {
          this.refreshUser()
        }, 4000)
        setTimeout(() => {
          this.loading = false
          this.$store.dispatch('loadMeetings')
        }, 5000)
      }
    },
    async getMeetingList() {
      try {
        await this.$store.dispatch('loadMeetings')
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.loading = false
        }, 2000)
      }
    },
    selectOpp(val) {
      console.log(val)
      this.selectedResourceId = val.id
      if (this.selectedResourceType === 'Deal' || this.selectedResourceType === 'Opportunity') {
        this.$emit('set-opp', val.name)
      }
    },
    addTemplate() {
      this.noteValue = this.selectedTemplate.body
    },
  },
  mounted() {
    if (this.hasMeetingWorkflow) {
      this.selectedMeetingWorkflow = this.workflows.filter(
        (workflow) => workflow.meeting_ref.meeting_id === this.meeting.id.toString(),
      )[0]
      if (
        this.selectedMeetingWorkflow.forms[0] &&
        this.selectedMeetingWorkflow.forms[0].saved_data &&
        Object.values(this.selectedMeetingWorkflow.forms[0].saved_data).length > 0
      ) {
        console.log(this.selectedMeetingWorkflow)
        this.updateData = this.selectedMeetingWorkflow.forms[0].saved_data
      } else {
        console.log(this.selectedMeetingWorkflow)
        const keys = Object.keys(this.selectedMeetingWorkflow.resource_ref.secondary_data)
        const filteredKeys = keys.filter((key) => this.formFieldNames.includes(key))
        let filteredObject = {}
        filteredKeys.forEach((key) => {
          filteredObject[key] = this.selectedMeetingWorkflow.resource_ref.secondary_data[key]
        })
        this.updateData = filteredObject
      }
    }

    if (this.meetingOpp) {
      console.log('HERE', this.meetingOpp)
      this.selectedResourceId = this.meetingOpp.id
      this.mappedOpp = this.meetingOpp
      if (this.user.crm === 'HUBSPOT') {
        this.selectedResourceType = 'Deal'
      } else {
        this.selectedResourceType = 'Opportunity'
      }
      if (this.selectedResourceType === 'Deal' || this.selectedResourceType === 'Opportunity') {
        this.$emit('set-opp', this.meetingOpp.name)
      }
    }

    this.usingAi = {
      name: 'Yes',
      value: 'true',
    }
  },
  computed: {
    hasMeetingWorkflow() {
      let newWfList = this.workflows.map((wf) => wf.meeting_ref.meeting_id)
      let stringId = this.meeting.id.toString()
      return newWfList.includes(stringId)
    },
    user() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user
    },
    meetings() {
      return this.$store.state.meetings
    },
    resources() {
      return this.user.crm === 'HUBSPOT'
        ? ['Deal', 'Company', 'Contact']
        : ['Opportunity', 'Account', 'Contact', 'Lead']
    },
    defaultResource() {
      return this.user.crm === 'HUBSPOT' ? 'Deal' : 'Opportunity'
    },
    formFieldNames() {
      return this.formFields.map((field) => field.apiName)
    },
    date() {
      let today = new Date()
      let month = String(today.getMonth() + 1).padStart(2, '0')
      let day = String(today.getDate()).padStart(2, '0')
      let year = today.getFullYear()
      let formattedDate = `${month}/${day}/${year}`

      return formattedDate
    },

    formattedStartTimes() {
      return this.meetings.reduce((formatted, meeting) => {
        const date = new Date(meeting.meeting_ref['start_time'])
        const hours = date.getHours()
        const minutes = date.getMinutes()
        const period = hours >= 12 ? 'pm' : 'am'
        const formattedTime = `${((hours + 11) % 12) + 1}:${minutes
          .toString()
          .padStart(2, '0')}${period}`
        formatted[meeting.id] = formattedTime
        return formatted || null
      }, {})
    },

    formattedEndTimes() {
      return this.meetings.reduce((formatted, meeting) => {
        const date = new Date(meeting.meeting_ref['end_time'])
        const hours = date.getHours()
        const minutes = date.getMinutes()
        const period = hours >= 12 ? 'pm' : 'am'
        const formattedTime = `${((hours + 11) % 12) + 1}:${minutes
          .toString()
          .padStart(2, '0')}${period}`
        formatted[meeting.id] = formattedTime
        return formatted || null
      }, {})
    },
    allOpps() {
      return this.$store.state.chatOpps.results
    },
    allAccounts() {
      return this.$store.state.allAccounts
    },
    allContacts() {
      return this.$store.state.allContacts
    },
    allLeads() {
      return this.user.crm === 'SALESFORCE' ? this.$store.state.allLeads : []
    },
    noteTemplates() {
      return this.$store.state.templates || []
    },
    meetingData() {
      return this.$store.state.meetingData
    },
    currentOpp() {
      return this.$store.state.currentOpp
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';

::v-deep .multiselect * {
  font-size: 13px;
  font-family: $base-font-family;
  border-radius: 5px !important;
}
::v-deep .multiselect__option--highlight {
  background-color: $off-white;
  color: $base-gray;
}
::v-deep .multiselect__option--selected {
  background-color: $soft-gray;
}

::v-deep .multiselect__content-wrapper {
  border-radius: 5px;
  margin: 0.5rem 0rem;
  border-top: 1px solid $soft-gray;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  max-height: 250px !important;
  position: fixed;
  z-index: 1000;
  width: 275px;
}
::v-deep .multiselect__placeholder {
  color: $base-gray;
}

.logged {
  display: flex;
  align-items: center;
  flex-direction: row;
  background-color: $white-green;
  width: fit-content;
  font-size: 12px;
  color: $dark-green;
  padding: 6px 8px;
  border-radius: 5px;
  margin-top: 1rem;

  img {
    margin-right: 0.25rem;
    margin-bottom: -2px;
    filter: brightness(0%) invert(64%) sepia(8%) saturate(2746%) hue-rotate(101deg) brightness(97%)
      contrast(82%);
  }
}

.logged-blue {
  display: flex;
  align-items: center;
  flex-direction: row;
  background-color: $white-blue;
  width: fit-content;
  font-size: 12px;
  color: $dark-black-blue;
  padding: 6px 8px;
  border-radius: 5px;
  margin-top: 1rem;

  img {
    margin-right: 0.25rem;
    margin-bottom: -2px;
    filter: brightness(0%) invert(64%) sepia(8%) saturate(2746%) hue-rotate(101deg) brightness(97%)
      contrast(82%);
  }
}

.small-font {
  font-size: 14px;
}

.top-margin {
  margin-top: 0.5rem;
}

.summary {
  // border-left: 1px solid rgba(0, 0, 0, 0.2);
  width: 100%;
  // padding-left: 0.5rem;
  // margin-left: -0.5rem;
  margin-top: 0.5rem;
  font-size: 12px;
}

.large-height {
  height: 556px !important;
}

button {
  &:disabled {
    opacity: 0.5;
  }
}

.opaque {
  opacity: 0.5;
}

.failed {
  display: flex;
  align-items: flex-start;
  color: $coral;
  font-size: 11px;
  margin-top: 0.25rem;
  font-size: 11px !important;

  width: 100%;

  img {
    filter: invert(50%) sepia(32%) saturate(1115%) hue-rotate(309deg) brightness(99%) contrast(97%);
    margin-right: 0.5rem;
    margin-top: 3px;
  }
}

.inline-input {
  outline: none;
  padding: 0.5rem 0.75rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  color: $base-gray;
  min-height: 100px;
  width: 96%;
  font-family: $base-font-family;
  font-size: 12px;
  line-height: 1.5;
  letter-spacing: 0.4px;
}

.complete {
  background-color: $white-green;
  padding: 0.5rem;
  border-radius: 5px;
  color: $dark-green;
}

.multi-slot {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  color: $light-gray-blue;
  font-weight: bold;
  width: 100%;
  padding: 0.5rem 0rem;
  margin: 0;
  &__more {
    background-color: $base-gray;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border-top: 1px solid #e8e8e8;
    width: 100%;
    padding: 0.75rem 0rem;
    margin-top: 1rem;
    cursor: pointer;
  }
}

.small-button {
  @include chat-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: transparent;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  border-radius: 5px;
  font-size: 12px;
  padding: 0.35rem;
  margin-left: 1rem;
  font-weight: normal;

  img {
    margin: 0;
  }

  &:disabled {
    background-color: $off-white;
  }
}

.main-button {
  @include chat-button();
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.5rem;

  img {
    margin-right: 0.5rem;
    filter: invert(89%) sepia(43%) saturate(4130%) hue-rotate(323deg) brightness(90%) contrast(87%);
  }
}

.tertiary-chat-button {
  @include chat-button();
  padding: 0.5rem 0.75rem;
  margin-left: 1rem;

  img {
    margin-right: 0.5rem;
    filter: invert(89%) sepia(43%) saturate(4130%) hue-rotate(323deg) brightness(90%) contrast(87%);
  }
}

.secondary {
  color: $dark-green;
  border: 0.5px solid $dark-green;
}

.no-vertical-margin {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
}

.green-chat-button {
  @include chat-button();
  background-color: $dark-green;
  padding: 0.5rem;
  margin-top: 0.5rem;
  color: white;
  border: none;
  font-size: 13px;
  img {
    margin-right: 0.5rem;
    filter: invert(98%);
  }
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.chat-meetings-section {
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0 1rem 0.5rem 1.25rem;
  overflow-y: scroll;
  overflow-x: hidden;
  scroll-behavior: smooth;
}

// .chat-meetings-section::-webkit-scrollbar {
//   width: 6px;
//   height: 0px;
// }
// .chat-meetings-section::-webkit-scrollbar-thumb {
//   background-color: transparent;
//   box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
//   border-radius: 6px !important;
// }
// .chat-meetings-section:hover::-webkit-scrollbar-thumb {
//   background-color: $base-gray;
// }

.meeting-block {
  // background-color: yellow;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1rem 0 0 0;

  div {
    p {
      font-size: 14px;
      margin: 0;
    }
    small,
    s {
      color: $light-gray-blue;
      font-size: 12px;
    }
  }
}

.meetings {
  height: 100%;
  width: 100%;
  overflow-y: scroll;
  overflow-x: hidden;
}

.meetings-header {
  position: sticky;
  background-color: white;
  top: 0;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  // border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  p {
    font-size: 12px;
    padding: 0;
    margin: 0;
    span {
      color: $light-gray-blue;
      margin-right: 0.25rem;
    }
  }
}

.rotate {
  animation: rotation 3s infinite linear;
  cursor: not-allowed;
  // opacity: 0.3;
}

.row {
  display: flex;
  align-items: center;
  flex-direction: row;
  background-color: $white-green;
  width: fit-content;
  padding: 4px;
  border-radius: 4px;
  margin: 8px 0 0 -4px;

  p {
    font-size: 12px !important;
    color: $dark-green;
  }

  img {
    margin-bottom: -2px;
    filter: brightness(0%) invert(64%) sepia(8%) saturate(2746%) hue-rotate(101deg) brightness(97%)
      contrast(82%);
  }
}

.view-opp-button {
  @include chat-button();
  border-radius: 5px;
  padding: 6px 8px;
  display: block;
  overflow: hidden;
  width: 220px;
  margin-right: 0.75rem;
  white-space: nowrap;
  text-overflow: ellipsis;
  background-color: $dark-green;
  border: 1px solid $dark-green;
  color: white;
}

.opp-row {
  position: sticky;
  top: 0;
  background-color: white;
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 100%;
  justify-content: space-between;
}

.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;

  img {
    margin-right: 0.25rem;
  }
}

.margin-top {
  margin-top: 2rem;
}

.margin-top-s {
  margin-top: 1.5rem;
}

.meeting-modal-container {
  display: flex;
  flex-direction: column;
  width: 525px;
  height: 400px;
  padding: 0 1.5rem;
  background-color: white;
  border-radius: 8px;
  overflow-y: scroll;
  position: relative;
}

.meeting-modal-header {
  position: sticky;
  background-color: white;
  top: 0;
  z-index: 1000;
  display: flex;
  justify-content: space-between;
  padding-bottom: 0.5rem;
}

.chat-body {
  margin-top: 1rem;

  p {
    font-size: 13px;
  }
}

.green-button {
  background-color: $dark-green !important;
  color: white !important;
  border: none !important;
}

.error {
  color: $coral;
  font-size: 12px;
}

.meeting-modal-footer {
  p {
    margin-right: auto;
    margin-left: 0.75rem;
    font-size: 12px;
  }
  position: absolute;
  background-color: white;
  border: 1px solid $soft-gray;
  border-radius: 4px;
  border-right: none;
  border-top: none;
  left: 0;
  padding: 1.5rem 1rem 0 0;
  width: 99%;
  bottom: 0;
  margin-top: auto;
  display: flex;
  justify-content: flex-end;
  // border-top: 1px solid $soft-gray;

  button {
    @include chat-button();
    padding: 0.5rem 1rem;
    margin-left: 1rem;
    margin-bottom: 1rem;
    font-size: 12px;
  }
}

.chat-modal-container {
  display: flex;
  flex-direction: column;
  width: 525px;
  height: 90vh;
  padding: 0 1.25rem;
  background-color: white;
  border-radius: 8px;
  overflow-y: scroll;
  position: relative;
}

.chat-modal-header {
  position: sticky;
  background-color: white;
  top: 0;
  z-index: 1000;
  display: flex;
  justify-content: space-between;
  padding-bottom: 0.5rem;
}

.gray-text {
  color: $light-gray-blue;
}
.smaller {
  font-size: 12px;
}

.elipsis-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 450px;
}

.chat-modal-footer {
  position: sticky;
  padding: 1rem 0;
  background-color: white;
  bottom: 0;
  z-index: 1000;
  margin-top: auto;
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;

  button {
    @include chat-button();
    padding: 0.5rem 1rem;
    margin-left: 1rem;
    font-size: 12px;
  }

  button:last-of-type {
    background-color: $dark-green;
    color: white;
    border: none;
  }
}
.message-text {
  font-family: $base-font-family;
  word-wrap: break-word;
  white-space: pre-wrap;
  padding: 0 0.75rem 0 0;
  margin: 0;
}
</style>