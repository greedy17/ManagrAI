<template>
  <section class="meetings">
    <Modal
      v-if="meetingModalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), toggleMeetingModal()
        }
      "
    >
      <div class="meeting-modal-container">
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

          <h4 v-if="!submitting" @click="toggleMeetingModal" style="cursor: pointer">x</h4>
          <img v-else class="rotate" src="@/assets/images/refresh.svg" height="18px" alt="" />
        </div>

        <div v-if="!currentMeeting.resource_id" :class="{ disabled: submitting }" class="chat-body">
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
                :loading="dropdownLoading"
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
        </div>

        <div class="meeting-modal-footer">
          <button :disabled="submitting" @click="toggleMeetingModal">Close</button>
          <button class="green-button" v-if="selectedResourceId" :disabled="submitting">
            Log Meeting
          </button>
        </div>
      </div>
    </Modal>

    <header class="meetings-header">
      <p><span>Today's Meetings: </span>{{ date }}</p>

      <button :disabled="loading" @click="refreshCalEvents" class="small-button">
        <img
          v-if="!loading"
          class="dampen"
          src="@/assets/images/calendar.svg"
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
        sync
      </button>
    </header>
    <section class="chat-meetings-section">
      <div class="meeting-block" v-for="(meeting, i) in meetings" :key="i">
        <div>
          <p>
            {{ meeting.meeting_ref.topic }}
          </p>
          <small v-if="!meeting.is_completed"
            >{{ formattedStartTimes[meeting.id] }} - {{ formattedEndTimes[meeting.id] }}</small
          >
          <s v-else>{{ formattedStartTimes[meeting.id] }} - {{ formattedEndTimes[meeting.id] }} </s>

          <div v-if="submitting" style="margin-top: -2px">
            <img class="rotate" src="@/assets/images/loading.svg" height="14px" alt="" />
          </div>
        </div>

        <button v-if="!meeting.is_completed" @click="logMeeting(meeting)" class="main-button">
          <img src="@/assets/images/sparkle.svg" height="14px" alt="" /> Log meeting
        </button>

        <div class="complete" v-else>
          <p style="font-size: 12px">complete</p>
        </div>
      </div>
    </section>
  </section>
</template>

<script>
import User from '@/services/users'
import Modal from '@/components/InviteModal'

export default {
  name: 'ChatMeetings',
  components: { Modal, Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect') },
  props: {},
  watch: {
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
  },
  data() {
    return {
      loading: false,
      meetingModalOpen: false,
      submitting: false,
      currentMeeting: null,
      mappedOpp: null,
      dropdownLoading: false,
      loadMorePage: 0,
      searchValue: null,
      usingAi: false,
      selectedResourceId: null,
      selectedResourceType: null,
      selectedList: [],
      aiOptions: [
        {
          name: 'Yes',
          value: true,
        },
        {
          name: 'No',
          value: false,
        },
      ],
    }
  },
  methods: {
    changeList() {
      if (this.selectedResourceType === 'Account' || this.selectedResourceType === 'Company') {
        this.selectedList = this.allAccounts
      } else if (this.selectedResourceType === 'Contact') {
        this.selectedList = this.allContacts
      } else if (this.selectedResourceType === 'Lead') {
        this.selectedList = this.allLeads
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
      this.usingAi = false
      this.selectedResourceId = null
      this.selectedResourceType = null
    },
    async refreshCalEvents() {
      this.loading = true
      try {
        let res = await User.api.refreshCalendarEvents()
        console.log(res)
      } catch (e) {
        console.log('Error in refreshCalEvents: ', e)
      } finally {
        this.getMeetingList()
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
      return this.$store.state.allLeads
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
}
::v-deep .multiselect__placeholder {
  color: $base-gray;
}

.complete {
  background-color: $white-green;
  padding: 0.25rem 0.5rem;
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
    margin-right: 0.5rem;
  }

  &:disabled {
    background-color: $off-white;
  }
}

.main-button {
  @include chat-button();
  // background-color: $dark-green;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.5rem;
  // color: white;
  // border: none;
  img {
    margin-right: 0.5rem;
    filter: invert(89%) sepia(43%) saturate(4130%) hue-rotate(323deg) brightness(90%) contrast(87%);
    // filter: invert(96%);
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
  padding: 0 1.25rem;
  // background-color: red;
}

.meeting-block {
  // background-color: yellow;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1rem 0 1.25rem 0;

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

.meeting-modal-container {
  display: flex;
  flex-direction: column;
  width: 525px;
  height: 600px;
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
  background-color: white;
  width: 100%;
  bottom: 0;
  right: 1rem;
  z-index: 1000;
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
</style>