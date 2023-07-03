<template>
  <section class="meetings">
    <Modal
      v-if="chatModalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), toggleChatModal()
        }
      "
    >
      <div class="chat-modal-container">
        <div class="chat-modal-header">
          <div>
            <h3 class="elipsis-text" style="margin-bottom: 0.25rem">
              {{ currentMeetingName }}
            </h3>
            <span class="gray-text smaller"
              >Your CRM fields have been auto-filled. Pleae review and click submit.</span
            >
          </div>

          <h4 v-if="!submitting" @click="toggleChatModal" style="cursor: pointer">x</h4>
          <!-- <img
            v-else
            class="rotate opaque"
            src="@/assets/images/refresh.svg"
            height="18px"
            alt=""
          /> -->
        </div>

        <div
          style="position: relative"
          :class="{ disabled: submitting }"
          v-for="(field, i) in formFields"
          :key="i"
        >
          <!-- field.apiName === 'meeting_comments'
                ? updateData['Notes']
                : field.apiName === 'meeting_type'
                ? updateData['NoteSubject']
                : -->
          <ChatFormField
            :placeholder="updateData[field.apiName]"
            :field="field"
            :resourceId="currentResourceId"
            :integrationId="currentIntegrationId"
            :chatData="updateData"
            @set-value="setUpdateValues"
            :stageFields="stageFields"
            :stagesWithForms="stagesWithForms"
          />
        </div>

        <div class="chat-modal-footer">
          <button :disabled="submitting" @click="toggleChatModal">Close</button>
          <button :disabled="submitting" @click="onSubmitChat">Submit</button>
        </div>
      </div>
    </Modal>

    <Modal
      v-if="meetingModalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), toggleMeetingModal()
        }
      "
    >
      <div
        :class="{ 'large-height': usingAi && usingAi.value === 'false' }"
        class="meeting-modal-container"
      >
        <div class="meeting-modal-header">
          <div>
            <h3 class="elipsis-text" style="margin-bottom: 0.25rem">
              {{ currentMeeting.meeting_ref.topic }}
            </h3>
            <span class="gray-text smaller"
              >{{ formattedStartTimes[currentMeeting.id] }} -
              {{ formattedEndTimes[currentMeeting.id] }}</span
            >
          </div>

          <h4 @click="toggleMeetingModal" style="cursor: pointer">x</h4>
        </div>
        <!-- v-if="!currentMeeting.resource_id" -->
        <div class="chat-body" :class="{ disabled: submitting }">
          <div v-if="!usingAi">
            <p>Use AI to summarize the call and autofill CRM fields ?</p>

            <Multiselect
              v-model="usingAi"
              selectLabel=""
              deselectLabel=""
              label="name"
              track-by="value"
              :options="aiOptions"
              :loading="dropdownLoading"
            >
            </Multiselect>
          </div>

          <div v-else>
            <div v-if="usingAi.value === 'true'">
              <div>
                <p>Related to type</p>

                <Multiselect
                  v-model="selectedResourceType"
                  selectLabel=""
                  deselectLabel=""
                  :options="resources"
                  :loading="dropdownLoading"
                >
                </Multiselect>
              </div>

              <div v-if="selectedResourceType">
                <p>Search for a {{ selectedResourceType }}</p>

                <Multiselect
                  v-model="mappedOpp"
                  @select="selectOpp($event)"
                  @search-change="setSearchVal($event)"
                  :placeholder="`Search for ${selectedResourceType}`"
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
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results. Try loading more</p>
                    <button @click="loadMoreOpps(mappedOpp)" class="multi-slot__more">
                      Load more
                    </button>
                  </template>
                </Multiselect>
              </div>
            </div>

            <div v-else>
              <p>Log your meeting using converstional AI</p>
              <div
                @input="setValue($event)"
                class="inline-input"
                v-html="noteValue"
                contenteditable="true"
              ></div>

              <p>Use note template:</p>
              <Multiselect
                v-model="selectedTemplate"
                selectLabel=""
                deselectLabel=""
                label="subject"
                track-by="body"
                :options="noteTemplates"
                :loading="dropdownLoading"
              >
              </Multiselect>
            </div>
          </div>
        </div>

        <div class="meeting-modal-footer">
          <button :disabled="submitting" @click="toggleMeetingModal">Close</button>
          <button
            @click="submitChatMeeting"
            class="green-button"
            v-if="selectedResourceId || (usingAi && usingAi.value === 'false')"
            :disabled="submitting"
          >
            Log Meeting
          </button>
        </div>
      </div>
    </Modal>

    <header class="meetings-header">
      <p @click="test">📅 <span> Today's Meetings: </span>{{ date }}</p>

      <button :disabled="loading" @click="refreshCalEvents" class="small-button">
        <img
          v-if="!loading"
          class="dampen"
          src="@/assets/images/meeting.svg"
          height="12px"
          alt=""
        />
        <img
          v-else
          class="rotate opaque not-allowed"
          src="@/assets/images/refresh.svg"
          height="14px"
          alt=""
        />
      </button>
    </header>
    <section class="chat-meetings-section">
      <div v-if="!meetings.length">
        <p style="font-size: 13px">No meetings found. You may need to sync your calendar</p>
      </div>

      <div class="meeting-block" v-for="(meeting, i) in meetings" :key="i">
        <div>
          <p>
            {{ meeting.meeting_ref.topic }}
          </p>

          <small>{{ formattedStartTimes[meeting.id] }} - {{ formattedEndTimes[meeting.id] }}</small>

          <div v-if="submitting && currentMeeting.id === meeting.id" style="margin-top: -2px">
            <img class="rotate" src="@/assets/images/loading.svg" height="14px" alt="" />
          </div>

          <div
            v-if="meetingData[meeting.id] && meetingData[meeting.id].retry && !submitting"
            class="failed"
          >
            <img src="@/assets/images/ban.svg" height="12px" alt="" />
          </div>
          <div class="row" v-if="meetingData[meeting.id] && meetingData[meeting.id].success">
            <p><img src="@/assets/images/check.svg" height="12px" alt="" /> meeting logged</p>
          </div>
        </div>

        <button
          :disabled="submitting"
          v-if="!meetingData[meeting.id]"
          @click="logMeeting(meeting)"
          class="main-button secondary"
        >
          <img src="@/assets/images/sparkle.svg" height="14px" alt="" />
          Log Meeting
        </button>

        <div v-else>
          <button
            v-if="!(meetingData[meeting.id] && meetingData[meeting.id].success)"
            class="green-chat-button"
            @click="
              toggleChatModal(
                meetingData[meeting.id].data,
                meeting.resource_ref.name,
                meeting.resource_ref.id,
                meeting.resource_ref.integration_id,
                meeting.resource_type,
                meeting.id,
              )
            "
          >
            <img src="@/assets/images/wand.svg" class="invert" height="12px" alt="" />
            Review & Submit
          </button>

          <button disabled style="margin-right: -2px; cursor: not-allowed" class="main-button">
            <img src="@/assets/images/wand.svg" height="12px" alt="" /> Generate Content
          </button>
        </div>
      </div>
    </section>
  </section>
</template>

<script>
import User from '@/services/users'
import Modal from '@/components/InviteModal'
import ChatFormField from '@/components/Chat/ChatFormField.vue'
import { CRMObjects } from '@/services/crm'

export default {
  name: 'ChatMeetings',
  components: {
    Modal,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    ChatFormField,
  },
  props: {
    formFields: {},
    stageFields: {},
    stagesWithForms: {},
  },
  watch: {
    usingAi(val) {
      if (val && val.value === 'false') {
        console.log('here')
        this.$store.dispatch('loadTemplates')
      }
    },
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
      listLoading: false,
      loading: false,
      chatModalOpen: false,
      meetingModalOpen: false,
      submitting: false,
      currentMeeting: null,
      mappedOpp: null,
      dropdownLoading: false,
      loadMorePage: 0,
      searchValue: null,
      usingAi: null,
      selectedResourceId: null,
      selectedResourceType: null,
      selectedList: [],
      noteValue: null,
      selectedTemplate: null,
      prompt: null,
      updateData: {},
      currentMeetingName: null,
      currentResourceId: null,
      currentIntegrationId: null,
      currentResourceType: null,
      currentMeetingId: null,
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
      console.log(this.meetings)
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
      this.chatModalOpen = false

      try {
        const res = await CRMObjects.api.updateResource({
          form_data: this.updateData,
          resource_type: this.currentResourceType,
          form_type: 'UPDATE',
          resource_id: this.currentResourceId,
          integration_ids: [this.currentIntegrationId],
          chat_form_id: ['000ae5577320'],
          from_workflow: false,
          workflow_title: 'None',
          stage_name: null,
        })
        if (res.success) {
          this.$store.dispatch('setMeetingData', {
            id: this.currentMeetingId,
            data: res.data,
            success: true,
            retry: false,
          })
        } else {
          this.$store.dispatch('setMeetingData', {
            id: this.currentMeetingId,
            data: res.data,
            success: false,
            retry: true,
          })
        }
      } catch (e) {
        console.log(e)
      } finally {
        // this.$refs.rightSideBar.reloadOpps()
        setTimeout(() => {
          this.submitting = false
        }, 1000)
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
    toggleChatModal(data, name, resourceId, intId, type, currentMeetingId) {
      this.chatModalOpen = !this.chatModalOpen
      if (data) {
        console.log(data)
        this.updateData = data
      }
      if (name) {
        this.currentMeetingName = name
        this.$emit('set-opp', name)
      }
      if (resourceId) {
        this.currentResourceId = resourceId
      }
      if (intId) {
        this.currentIntegrationId = intId
      }
      if (type) {
        this.currentResourceType = type
      }
      if (currentMeetingId) {
        this.currentMeetingId = currentMeetingId
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
      this.meetingModalOpen = false
      try {
        let res = await User.api.submitChatMeeting({
          user_id: this.user.id,
          prompt: this.prompt,
          workflow_id: this.currentMeeting.id,
          resource_type: this.user.crm === 'HUBSPOT' ? 'Deal' : 'Opportunity',
        })
        this.$store.dispatch('setMeetingData', {
          id: this.currentMeeting.id,
          data: res.data,
          success: false,
          retry: false,
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.submitting = false
        setTimeout(() => {
          this.$store.dispatch('loadMeetings')
        })
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
        console.log(res)
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
        console.log(res)
      } catch (e) {
        console.log('Error in refreshCalEvents: ', e)
      } finally {
        setTimeout(() => {
          this.refreshUser()
        }, 1000)
        setTimeout(() => {
          this.loading = false
          this.$store.dispatch('loadMeetings')
        }, 1500)
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
      this.selectedResourceId = val.id
      if (this.selectedResourceType === 'Deal' || this.selectedResourceType === 'Opportunity') {
        this.$emit('set-opp', val.name)
      }
    },
    addTemplate() {
      this.noteValue = this.selectedTemplate.body
    },
  },
  created() {
    this.getMeetingList()
  },
  computed: {
    user() {
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
  width: 400px;
}
::v-deep .multiselect__placeholder {
  color: $base-gray;
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
  // margin-top: 0.25rem;
  img {
    filter: invert(50%) sepia(32%) saturate(1115%) hue-rotate(309deg) brightness(99%) contrast(97%);
  }
}

.inline-input {
  outline: none;
  padding: 0.5rem 0.75rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  color: $base-gray;
  min-height: 100px;
  width: 100%;
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

.secondary {
  color: $dark-green;
  border: 0.5px solid $dark-green;
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
  padding: 0 1rem 0 1.25rem;
  overflow-y: scroll;
  overflow-x: hidden;
  scroll-behavior: smooth;
}

.chat-meetings-section::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.chat-meetings-section::-webkit-scrollbar-thumb {
  background-color: transparent;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px !important;
}
.chat-meetings-section:hover::-webkit-scrollbar-thumb {
  background-color: $base-gray;
}

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
  padding: 4px;
  border-radius: 4px;
  margin: 4px 0 0 -4px;

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

.meeting-modal-footer {
  position: absolute;
  width: 100%;
  bottom: 0;
  right: 1rem;
  margin-top: auto;
  display: flex;
  justify-content: flex-end;
  // border-top: 1px solid $soft-gray;
  margin-top: 1rem;

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
</style>