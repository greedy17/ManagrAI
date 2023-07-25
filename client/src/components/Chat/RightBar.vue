<template>
  <section class="right-container">
    <div style="margin-top: -0.5rem" v-if="!selectedOpp && !currentMeeting" class="switcher">
      <div
        @click="switchMainView('pipeline')"
        :class="{ activeswitch: mainView === 'pipeline' }"
        class="switch-item"
      >
        <img src="@/assets/images/money.svg" height="14px" alt="" />
        Pipeline
      </div>
      <div
        @click="switchMainView('meetings')"
        :class="{ activeswitch: mainView === 'meetings' }"
        class="switch-item"
      >
        <font-awesome-icon icon="fa-regular fa-calendar" />
        Meetings
      </div>
    </div>
    <header>
      <section v-if="selectedOpp || currentMeeting">
        <div class="flexed-row-s"></div>
        <span v-if="selectedOpp" style="margin-top: -4px" class="flexed-row-spread header-bg">
          <div class="elipsis-text">
            <span class="icon-bg">
              <img
                @click="deselectAll"
                src="@/assets/images/back.svg"
                height="16px;width:16px"
                alt=""
              />
            </span>
            <p>
              {{ selectedOpp.name }}
            </p>
          </div>

          <div style="margin-left: -8px" class="flexed-row">
            <img
              :class="{ 'rotate opaque not-allowed': oppsLoading }"
              @click="reloadOpps"
              src="@/assets/images/refresh.svg"
              height="18px"
              alt=""
            />

            <font-awesome-icon
              v-if="userCRM === 'HUBSPOT'"
              style="height: 20px; width: 20px; color: #ff7a59"
              icon="fa-brands fa-hubspot"
              @click="openInCrm(selectedOpp.integration_id)"
            />

            <font-awesome-icon
              v-else
              style="height: 24px; width: 24px; color: #0d9dda"
              icon="fa-brands fa-salesforce"
              @click="openInCrm(selectedOpp.integration_id)"
            />
          </div>
        </span>

        <span v-else style="margin-top: -4px" class="flexed-row-spread header-bg">
          <div class="elipsis-text">
            <span class="icon-bg">
              <img
                @click="deselectAll"
                src="@/assets/images/back.svg"
                height="16px;width:16px"
                alt=""
              />
            </span>
            <p>
              {{ currentMeeting.topic }}
            </p>
          </div>

          <div style="margin-left: -8px" class="flexed-row">
            <small class="gray-text">{{ formatDate(currentMeeting.start_time) }}</small>
          </div>
        </span>
      </section>

      <section v-else>
        <div v-if="mainView === 'pipeline'" style="margin-top: 0.5rem" class="flexed-row-spread">
          <div class="input">
            <img style="cursor: text" src="@/assets/images/search.svg" height="16px" alt="" />

            <input
              @keydown.enter="loadFromEnter"
              class="search-input"
              v-model="searchText"
              :placeholder="`Search by name`"
            />
            <img
              v-show="searchText"
              @click="clearText"
              src="@/assets/images/close.svg"
              class="invert"
              height="12px"
              alt=""
            />
          </div>

          <span @click="toggleShowFilters" class="icon-button">
            <img src="@/assets/images/filterlist.svg" height="18px" alt="" />
            <small
              v-if="activeFilters.length"
              :class="{ 'pop-transition': isPopping }"
              class="filter-count"
              >{{ activeFilters.length }}</small
            >
          </span>

          <div v-show="filtersOpen" class="filter-container">
            <header>
              <p v-if="!selectedFilter">
                Select Filters
                <img
                  @click="removeFilters"
                  v-if="activeFilters.length"
                  src="@/assets/images/clearfilter.svg"
                  height="14px"
                  alt=""
                  style="margin-left: 0.5rem"
                />
              </p>

              <div
                style="margin-left: -0.75rem"
                v-else
                @click="clearFilter"
                class="flexed-row pointer"
              >
                <img src="@/assets/images/back.svg" height="16px;width:16px" alt="" />

                {{ selectedFilter.name }}
              </div>

              <p @click="toggleShowFilters">x</p>
            </header>

            <section v-if="!selectedFilter">
              <div
                @click="selectFilter(filter)"
                v-for="filter in filters"
                :key="filter.name"
                class="icon-row"
              >
                <font-awesome-icon :icon="`fa-solid  ${filter.icon}`" />
                <p>{{ filter.name }} <span></span></p>
              </div>

              <div v-if="activeFilters.length" class="active-filters">
                <div
                  :title="af[1] + ' ' + af[0].toLowerCase() + ' ' + af[2]"
                  v-for="(af, i) in activeFilters"
                  :key="i"
                >
                  <p>{{ af[1] + ' ' + af[0].toLowerCase() + ' ' + af[2] }}</p>

                  <span @click="removeFilter(af)" class="remove">x</span>
                </div>
              </div>
            </section>

            <section v-else>
              <div>
                <Multiselect
                  :placeholder="`${selectedFilter.name}`"
                  style="width: 100%; font-size: 14px"
                  v-model="selectedOperator"
                  :options="operators[selectedFilter.name]"
                  @select="selectOperator($event.value, $event.label)"
                  openDirection="below"
                  selectLabel=""
                  track-by="value"
                  label="label"
                  selectedLabel=""
                  deselectLabel=""
                  :preselectFirst="true"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                </Multiselect>

                <div v-if="selectedFilter.operator">
                  <input
                    v-if="
                      selectedFilter.name !== 'Stage' || selectedFilter.operatorLabel === 'contains'
                    "
                    class="filter-input"
                    :placeholder="`${selectedFilter.name} ${selectedFilter.operatorLabel}`"
                    :type="`${selectedFilter.dataType}`"
                    v-model="selectedFilter.value"
                    autofocus
                  />

                  <Multiselect
                    style="margin-top: 1rem"
                    v-else
                    :options="
                      this.user.crm === 'SALESFORCE' ? picklistOptions[stageField.id] : allStages
                    "
                    :placeholder="`${selectedFilter.name} ${selectedFilter.operatorLabel}`"
                    selectLabel=""
                    track-by="id"
                    label="label"
                    v-model="filtervalue"
                    selectedLabel=""
                    deselectLabel=""
                    @select="addFilterValue($event.id)"
                  >
                    <template slot="noResult">
                      <p class="multi-slot">No results.</p>
                    </template>
                  </Multiselect>
                </div>

                <div
                  style="margin: 1rem 0 1rem 0.25rem; position: relative"
                  v-if="selectedFilter.value"
                >
                  <p class="wrap-text">
                    <span style="color: #9596b4">Filter : </span>
                    "{{ selectedFilter.name }} {{ selectedFilter.operatorLabel }}
                    {{ selectedFilter.value }}"
                  </p>

                  <div
                    v-if="selectedFilter.name && selectedFilter.operator && selectedFilter.value"
                    class="save-close"
                  >
                    <div @click="addFilter" class="save">
                      <span>save</span>
                    </div>
                    <!-- <div @click="clearFilter" class="close">
                      <span>cancel</span>
                    </div> -->
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>

        <div v-else style="margin-top: 0.5rem" class="flexed-row-spread__">
          <div>
            <p class="gray-text neg-mar-small">Select a date:</p>
            <input class="inline-input" v-model="meetingDate" type="date" />
          </div>

          <button :disabled="loading" @click="getZoomMeetings" class="icon-button">
            <img
              v-if="!loading"
              class="dampen"
              src="@/assets/images/meeting.svg"
              height="14px"
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
        </div>
      </section>
    </header>
    <div class="switcher" v-if="selectedOpp && !loading">
      <div @click="switchView('crm')" :class="{ activeswitch: view === 'crm' }" class="switch-item">
        <img src="@/assets/images/crmlist.svg" height="12px" alt="" />
        Details
      </div>
      <div
        @click="switchView('notes')"
        :class="{ activeswitch: view === 'notes' }"
        class="switch-item"
      >
        <img src="@/assets/images/note.svg" height="12px" alt="" />
        Notes
      </div>
      <div style="cursor: not-allowed" class="switch-item">
        <img src="@/assets/images/callsummary.svg" height="14px" alt="" />
        Summaries
      </div>
    </div>

    <div class="selected-opp-container" v-if="currentMeeting && !loading">
      <div class="selected-opp-section bordered">
        <div style="width: 99%" class="opp-section">
          <ChatMeetingLogger
            :meeting="currentMeeting"
            :workflows="meetingWorkflows"
            :formFields="formFields"
            :stageFields="stageFields"
            :stagesWithForms="stagesWithForms"
            @reload-workflows="reloadWorkflows"
            @reload-meetings="reloadMeetings"
            @select-opp="selectOpp"
            @deselect-meeting="deselectMeeting"
            :meetingOpp="meetingOpp"
            :key="logkey"
          />
        </div>
      </div>
    </div>

    <div class="selected-opp-container" v-else-if="selectedOpp && !loading">
      <div v-show="view === 'crm'" class="selected-opp-section bordered">
        <div class="opp-section">
          <div v-for="field in oppFields" :key="field.id" style="margin-bottom: 1rem">
            <p style="font-size: 12px" class="gray-text">
              {{ field.label }}
            </p>

            <div
              @click="toggleEdit(field.id)"
              v-if="!editing || activeField !== field.id"
              class="field"
            >
              <!-- {{ field.dataType }} -->
              {{
                field.apiName === 'dealstage'
                  ? field.options[0][selectedOpp['secondary_data'].pipeline].stages.filter(
                      (stage) => stage.id === selectedOpp['secondary_data'][field.apiName],
                    )[0].label
                  : field.dataType === 'Datetime'
                  ? formatDateTime(selectedOpp['secondary_data'][field.apiName])
                  : field.dataType === 'Date'
                  ? formatDateTime(selectedOpp['secondary_data'][field.apiName])
                  : field.label === 'Owner' || field.label === 'Deal owner'
                  ? selectedOpp.owner_ref.full_name
                  : selectedOpp['secondary_data'][field.apiName] || '-'
              }}
            </div>
            <div style="padding-right: 0.5rem" v-else>
              <InlineFieldEditor
                :inlinePlaceholder="
                  field.apiName === 'dealstage'
                    ? field.options[0][selectedOpp['secondary_data'].pipeline].stages.filter(
                        (stage) => stage.id === selectedOpp['secondary_data'][field.apiName],
                      )[0].label
                    : field.label === 'Owner' || field.label === 'Deal owner'
                    ? selectedOpp.owner_ref.full_name
                    : selectedOpp['secondary_data'][field.apiName]
                "
                :dataType="field.dataType"
                :apiName="field.apiName"
                :integrationId="selectedOpp.integrationId"
                :resourceId="selectedOpp.id"
                :resource="selectedOpp"
                :resourceType="userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal'"
                :field="field"
                :showing="editing"
                @close-inline="closeInline"
                @setFields="reloadOpps"
              />
            </div>
          </div>
        </div>
      </div>
      <div
        v-for="(notes, month) in sortedNotes"
        :key="month"
        v-show="view === 'notes'"
        class="selected-opp-section"
      >
        <h4 style="margin-top: 0; background-color: white" class="selected-opp">
          {{ month }}
          <!-- <img src="@/assets/images/dropdown.svg" height="14px" alt="" /> -->
        </h4>
        <section v-if="notes.length">
          <div v-for="note in notes" :key="note.id">
            <div class="note-section">
              <small class="gray-text left-margin right-absolute">{{
                `${getMonth(note.submission_date)} ${getDate(note.submission_date)}, ${getYear(
                  note.submission_date,
                )}`
              }}</small>
              <div class="row text-ellipsis">
                <p
                  :class="{ 'gray-text strike': !!note.saved_data__StageName }"
                  style="margin-right: 0.25rem"
                >
                  {{ note.previous_data__StageName }}
                </p>

                <img
                  v-if="note.saved_data__StageName"
                  src="@/assets/images/transition.svg"
                  height="12px"
                  alt=""
                />

                <p style="margin: 0.25rem 0">{{ note.saved_data__StageName }}</p>
              </div>
              <div>
                <p style="margin: 0.25rem 0">{{ note.saved_data__meeting_comments || '---' }}</p>
              </div>
            </div>
          </div>
        </section>

        <section v-else>
          <div class="note-section">
            <p class="gray-text">Nothing here yet...</p>
          </div>
        </section>
      </div>
    </div>

    <div
      class="opp-scroll-container"
      v-else-if="!selectedOpp && this.mainView === 'pipeline' && !loading"
    >
      <!-- @mouseenter="setTooltip(opp.id)"
        @mouseleave="removeTooltip" -->
      <div
        v-for="opp in opportunities"
        class="opp-container"
        @click="changeSelectedOpp(opp)"
        :key="opp.id"
      >
        <p :title="opp.name" style="margin: 0">
          {{ opp.name }}
        </p>
        <!-- <div :class="{ 'showing-tooltip': showTooltip && hoverId === opp.id }" class="tooltip">
          {{ opp.name }}
        </div> -->
      </div>
      <div style="margin-bottom: 0.25rem" class="space-between">
        <button
          :disabled="loadingMore"
          class="chat-button no-border gray-scale"
          v-if="displayedOpps.next"
          @click="loadMoreOpps"
        >
          <img src="@/assets/images/load-more.svg" height="14px" alt="" />
          Load More
        </button>

        <p v-else>End of list</p>
      </div>
    </div>

    <div class="opp-scroll-container" v-else-if="this.mainView === 'meetings' && !loading">
      <p class="gray-text small-text">Select a meeting:</p>
      <div class="empty-container" v-if="!meetings.length && hasZoomIntegration">
        <p>No Zoom meetings found... refresh or select a different day</p>
      </div>

      <div class="empty-container" v-else-if="!hasZoomIntegration">
        <p><span @click="openSettings" class="link">Connect Zoom</span> in order to log meetings</p>
      </div>

      <div
        v-else
        @click="changeSelectedMeeting(meeting)"
        class="opp-container"
        v-for="(meeting, i) in meetings"
        :key="i"
      >
        <p class="no-margin">
          {{ meeting.topic }}
        </p>
        <small>{{ formatDate(meeting.start_time) }} </small>
      </div>
    </div>

    <div v-else-if="loading">
      <div class="loading">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>
    </div>
  </section>
</template>
  
<script>
import SlackOAuth from '@/services/slack'
import User from '@/services/users'
import { CRMObjects } from '@/services/crm'
import CollectionManager from '@/services/collectionManager'
import InlineFieldEditor from '@/components/Chat/InlineFieldEditor'
import ChatMeetingLogger from '@/components/Chat/ChatMeetingLogger'
import Zoom from '@/services/zoom/account'
import { MeetingWorkflows } from '@/services/salesforce/models'
import { decryptData } from '../../encryption'

export default {
  name: 'RightBar',
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    InlineFieldEditor,
    ChatMeetingLogger,
  },
  data() {
    return {
      logkey: 0,
      hoverId: null,
      showTooltip: false,
      view: 'crm',
      mainView: 'pipeline',
      stageValidationFields: {},
      updateFormData: {},
      loadingNotes: false,
      loadingMore: false,
      notes: [],
      sortedNotes: [],
      editing: false,
      activeField: null,
      loading: false,
      oppsLoading: false,
      isPopping: false,
      filtersOpen: false,
      hoveredOpp: null,
      searchText: '',
      selectedOpp: null,
      updateOppForm: [],
      oppFields: [],
      resourceName: 'Opportunity',
      stageField: null,
      filtervalue: null,
      allStages: [],
      meetings: [],
      meetingOpp: null,
      meetingDate: this.getCurrentDate(),
      objects: CollectionManager.create({
        ModelClass: CRMObjects,
        pagination: { size: 20 },
        // filters: {
        //   crmObject: 'Opportunity',
        // },
      }),
      page: 1,
      loadMorePage: 0,
      selectedOperator: null,
      months: {
        0: 'January',
        1: 'February',
        2: 'March',
        3: 'April',
        4: 'May',
        5: 'June',
        6: 'July',
        7: 'August',
        8: 'September',
        9: 'October',
        10: 'November',
        11: 'December',
      },
      operators: {
        Amount: [
          { label: 'is', value: 'EQUALS' },
          { label: 'is greater than', value: 'GREATER_THAN' },
          { label: 'is greater than or equal to', value: 'GREATER_THAN_EQUALS' },
          { label: 'is less than', value: 'LESS_THAN' },
          { label: 'is less than or equal to', value: 'LESS_THAN_EQUALS' },
          { label: 'contains', value: 'CONTAINS' },
          { label: 'does not equal', value: 'NOT_EQUALS' },
        ],
        Owner: [{ label: 'contains', value: 'CONTAINS' }],
        Stage: [
          { label: 'is', value: 'EQUALS' },
          { label: 'contains', value: 'CONTAINS' },
        ],
        Name: [
          { label: 'contains', value: 'CONTAINS' },
          { label: 'does not equal', value: 'NOT_EQUALS' },
          { label: 'is', value: 'EQUALS' },
        ],
        'Close date': [
          { label: 'is', value: 'EQUALS' },
          { label: 'is greater than', value: 'GREATER_THAN' },
          { label: 'is greater than or equal to', value: 'GREATER_THAN_EQUALS' },
          { label: 'is less than', value: 'LESS_THAN' },
          { label: 'is less than or equal to', value: 'LESS_THAN_EQUALS' },
          { label: 'does not equal', value: 'NOT_EQUALS' },
        ],
        'Last activity date': [
          { label: 'is', value: 'EQUALS' },
          { label: 'is greater than', value: 'GREATER_THAN' },
          { label: 'is greater than or equal to', value: 'GREATER_THAN_EQUALS' },
          { label: 'is less than', value: 'LESS_THAN' },
          { label: 'is less than or equal to', value: 'LESS_THAN_EQUALS' },
          { label: 'does not equal', value: 'NOT_EQUALS' },
        ],
      },
      selectedFilter: null,
      filters: [
        {
          name: 'Owner',
          dataType: 'text',
          icon: 'fa-user',
          apiName: 'Owner',
          operator: null,
          value: null,
          operatorLabel: null,
        },
        {
          name: 'Name',
          dataType: 'text',
          icon: 'fa-signature',
          apiName: `${this.userCRM === 'SALESFORCE' ? 'Name' : 'dealname'}`,
          operator: null,
          value: null,
          operatorLabel: null,
        },
        {
          name: 'Stage',
          dataType: 'text',
          icon: 'fa-stairs',
          apiName: `${this.userCRM === 'SALESFORCE' ? 'StageName' : 'dealstage'}`,
          operator: null,
          value: null,
          operatorLabel: null,
        },
        {
          name: 'Close date',
          dataType: 'date',
          icon: 'fa-calendar-plus',
          apiName: `${this.userCRM === 'SALESFORCE' ? 'CloseDate' : 'closedate'}`,
          operator: null,
          value: null,
          operatorLabel: null,
        },
        {
          name: 'Amount',
          dataType: 'number',
          icon: 'fa-sack-dollar',
          apiName: `${this.userCRM === 'SALESFORCE' ? 'Amount' : 'amount'}`,
          operator: null,
          value: null,
          operatorLabel: null,
        },
        {
          name: 'Last activity date',
          dataType: 'date',
          icon: 'fa-calendar-plus',
          apiName: 'LastActivityDate',
          operator: null,
          value: null,
          operatorLabel: null,
        },
      ],
    }
  },
  props: {
    formFields: {},
    stageFields: {},
    stagesWithForms: {},
  },
  watch: {
    activeFilters(newValue, oldValue) {
      if (newValue !== oldValue) {
        this.isPopping = true

        setTimeout(() => {
          this.isPopping = false
        }, 1000)
      }
    },
    selectedOperator(newVal) {
      if (this.selectedFilter) {
        this.selectedFilter.operator = newVal.value
        this.selectedFilter.operatorLabel = newVal.label
      } else {
        return
      }
    },
    searchText(newVal, oldVal) {
      if (newVal !== oldVal && newVal !== '') {
        return
      } else {
        this.$store.dispatch('loadChatOpps')
        this.page = 0
        this.loadMorePage = 0
      }
    },
    meetingDate: 'getZoomMeetings',
    // : 'selectOperator',
    selectedOpp: 'getNotes',
  },
  methods: {
    test() {
      console.log('log', this.opportunities)
    },
    openSettings() {
      this.$emit('open-settings')
    },
    formatDate(inputDate) {
      const dateObj = new Date(inputDate)
      const month = String(dateObj.getUTCMonth() + 1).padStart(2, '0')
      const day = String(dateObj.getUTCDate()).padStart(2, '0')
      const year = dateObj.getUTCFullYear()
      return `${month}/${day}/${year}`
    },
    getCurrentDate() {
      const now = new Date()
      const year = now.getFullYear()
      const month = String(now.getMonth() + 1).padStart(2, '0')
      const day = String(now.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    },
    addFilterValue(val) {
      this.selectedFilter.value = val
    },
    deselectAll() {
      this.selectedOpp = null
      this.$store.dispatch('setCurrentOpp', null)
      this.$store.dispatch('setCurrentMeeting', null)
    },
    deselectOpp() {
      this.selectedOpp = null
      this.$store.dispatch('setCurrentOpp', null)
    },
    deselectMeeting() {
      this.$store.dispatch('setCurrentMeeting', null)
    },
    setSortedNotes() {
      const sortedObjects = this.notes.sort((a, b) => {
        const dateA = new Date(a.submission_date)
        const dateB = new Date(b.submission_date)
        return dateB - dateA // Sort in descending order
      })

      const sections = {}

      sortedObjects.forEach((obj) => {
        const date = new Date(obj.submission_date)
        const month = `${date.toLocaleString('default', { month: 'long' })} ${date.getFullYear()}`

        if (!sections[month]) {
          sections[month] = []
        }

        sections[month].push(obj)
      })
      this.sortedNotes = sections
      // return sections;
    },
    setTooltip(id) {
      this.hoverId = id

      setTimeout(() => {
        this.showTooltip = true
      }, 2000)
    },
    removeTooltip() {
      this.showTooltip = false
      this.hoverId = null
    },
    formatDate(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return '-'
      }
      const replace = input.replace(pattern, '$2/$3/$1')
      return this.userCRM === 'HUBSPOT' ? replace.split('T')[0] : replace
    },
    formatDateTime(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return '-'
      }
      let newDate = input.replace(pattern, '$2/$3/$1')
      return newDate.split('T')[0]
    },
    switchView(view) {
      if (view !== this.view) {
        this.view = view
      }
    },
    async getZoomMeetings() {
      this.loading = true
      try {
        let res = await Zoom.api.getZoomMeetings({
          user_id: this.user.id,
          date: this.meetingDate,
        })
        this.meetings = res.data
      } catch (e) {
        console.log('ERROR GETTING MEETINGS:', e)
      } finally {
        setTimeout(() => {
          this.loading = false
        }, 1000)
      }
    },
    async reloadWorkflows() {
      try {
        await MeetingWorkflows.api.getMeetingList().then((response) => {
          this.meetingWorkflows = response.results
          this.logkey += 1
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.$store.dispatch('refreshCurrentUser')
      }
    },
    async reloadMeetings() {
      try {
        await Zoom.api
          .getZoomMeetings({
            user_id: this.user.id,
            date: this.meetingDate,
          })
          .then((response) => {
            this.logkey += 1
            this.meetings = response.data
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.reloadWorkflows()
        // this.logkey += 1
      }
    },
    async getMeetingWorkflows() {
      this.loading = true
      try {
        const res = await MeetingWorkflows.api.getMeetingList()
        this.meetingWorkflows = res.results
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.loading = false
        }, 2000)
      }
    },
    // async refreshCalEvents() {
    //   this.loading = true
    //   try {
    //     let res = await User.api.refreshCalendarEvents()
    //   } catch (e) {
    //     console.log('Error in refreshCalEvents: ', e)
    //   } finally {
    //     setTimeout(() => {
    //       this.refreshUser()
    //     }, 4000)
    //     setTimeout(() => {
    //       this.loading = false
    //       this.$store.dispatch('loadMeetings')
    //     }, 5000)
    //   }
    // },
    selectOpp(opp) {
      this.changeSelectedOpp(opp)
      this.deselectMeeting()
    },
    switchMainView(view) {
      if (view === 'meetings' && !this.meetings.length && this.hasZoomIntegration) {
        this.getZoomMeetings()
        this.deselectOpp()
      } else if (view === 'meetings') {
        this.deselectOpp()
      } else if (view !== 'meetings') {
        this.deselectMeeting()
      }
      if (view !== this.mainView) {
        this.mainView = view
      }
    },
    setMeetingOpp(opp) {
      this.meetingOpp = opp
    },
    async getNotes() {
      this.sortedNotes = []
      this.notes = []
      if (this.selectedOpp) {
        this.loadingNotes = true
        try {
          const res = await CRMObjects.api.getNotes({
            resourceId: this.selectedOpp.id,
          })
          if (res.length) {
            this.notes = []
            for (let i = 0; i < res.length; i++) {
              this.notes.push(res[i])
              this.notes = this.notes.filter((note) => note.saved_data__meeting_comments !== null)
              // this.notesLength = this.notes.length
            }
          }
        } catch (e) {
          console.log(e)
        } finally {
          if (this.notes.length) {
            this.setSortedNotes()
          }
          setTimeout(() => {
            this.loadingNotes = false
          }, 300)
        }
      } else {
        return
      }
    },
    clearFilter() {
      this.selectedFilter = null
      this.selectedOperator = null
    },
    async removeFilters() {
      try {
        this.$store.dispatch('changeFilters', [])
        await this.$store.dispatch('loadChatOpps', 1)
      } catch (e) {
        console.log('Error removing filter', e)
      } finally {
      }
    },
    closeInline() {
      this.activeField = null
      this.editing = false
      this.$store.dispatch('loadChatOpps')
    },
    setUpdateFormData(key, val) {
      if (val) {
        this.updateFormData[key] = val
      }
    },
    toggleEdit(id) {
      this.editing = !this.editing
      this.activeField = id
    },
    async reloadOpps() {
      this.oppsLoading = true
      let newOpp
      try {
        let res = await this.$store.dispatch('loadChatOpps')
        if (this.selectedOpp) {
          newOpp = res.results.filter((opp) => opp.id === this.selectedOpp.id)
          this.selectedOpp = newOpp[0]
        }
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.oppsLoading = false
          this.$emit('refresh-list')
        }, 1000)
      }
    },
    async addFilter() {
      let filter = []

      filter = [
        this.selectedFilter.operator,
        this.selectedFilter.apiName,
        this.selectedFilter.value,
      ]
      try {
        this.$store.dispatch('changeFilters', [...this.$store.state.filters, [...filter]])
        await this.$store.dispatch('loadChatOpps', 1)
      } catch (e) {
        console.log('Error in addFilter', e)
      } finally {
        this.toggleShowFilters()
      }
    },
    async removeFilter(targetList) {
      let lists = []
      lists = this.$store.state.filters.filter(
        (list) => JSON.stringify(list) !== JSON.stringify(targetList),
      )
      try {
        this.$store.dispatch('changeFilters', lists)
        await this.$store.dispatch('loadChatOpps', 1)
      } catch (e) {
        console.log('Error removing filter', e)
      } finally {
      }
    },
    selectOperator(val, label) {
      this.selectedFilter.operator = val
      this.selectedFilter.operatorLabel = label
    },
    selectFilter(filter) {
      this.selectedFilter = filter
    },
    toggleShowFilters() {
      this.filtersOpen = !this.filtersOpen
      this.selectedOperator = null
      this.selectedFilter = null
    },
    openInCrm(id) {
      let url

      if (this.user.crm === 'HUBSPOT') {
        url = `https://app.hubspot.com/contacts/${this.user.hubspotAccountRef.hubspotAppId}/record/0-3/${id}`
      } else {
        url =
          this.user.crm === 'SALESFORCE'
            ? `${this.user.salesforceAccountRef.instanceUrl}/lightning/r/Opportunity/${id}/view`
            : ''
      }

      window.open(url, '_blank')
    },
    clearText() {
      this.searchText = ''
    },
    changeSelectedMeeting(meeting) {
      this.$store.dispatch('setCurrentMeeting', meeting)
    },
    changeSelectedOpp(opp, name) {
      this.hoverId = null
      this.loadMorePage = 0
      this.$store.dispatch('setCurrentMeeting', null)
      if (opp) {
        this.selectedOpp = opp
        this.$store.dispatch('setCurrentOpp', opp)
      } else if (name) {
        let opp
        opp = this.opportunities.filter((opp) => opp.name === name)[0]
        if (opp) {
          this.selectedOpp = opp
          this.$store.dispatch('setCurrentOpp', opp)
        } else {
          this.selectedOpp = null
          this.searchText = name
          this.loadMoreOpps()

          setTimeout(() => {
            let opp
            opp = this.opportunities.filter((opp) => opp.name === this.searchText)[0]
            this.selectedOpp = opp
            this.$store.dispatch('setCurrentOpp', opp)
          }, 300)
        }
      }
    },
    removeDuplicatesByKey(arr, key) {
      const uniqueObjects = arr.filter(
        (item, index, self) => index === self.findIndex((obj) => obj[key] === item[key]),
      )
      return uniqueObjects
    },
    async setOppForms() {
      let stageGateForms
      let stagesWithForms
      const formsRes = await SlackOAuth.api.getOrgCustomForm()

      this.updateOppForm = formsRes.filter(
        (obj) =>
          obj.formType === 'UPDATE' && (obj.resource === 'Opportunity' || obj.resource === 'Deal'),
      )

      let allFields = this.updateOppForm[0].fieldsRef

      let stageField = this.updateOppForm[0].fieldsRef.filter(
        (field) => field.apiName === 'Stage' || field.apiName === 'dealstage',
      )
      this.stageField = stageField[0]

      if (this.userCRM === 'HUBSPOT') {
        let stages = this.stageField.options[0]
        const mappedStages = Object.keys(stages).map((key) => {
          const originalValue = stages[key]
          return originalValue.stages
        })
        const allStages = mappedStages.reduce((acc, curr) => acc.concat(curr), [])
        this.allStages = allStages
        this.allStages = this.removeDuplicatesByKey(this.allStages, 'id')
        // console.log(this.allStages)
      }

      this.oppFields = this.updateOppForm[0].fieldsRef.filter(
        (field) =>
          field.apiName !== 'meeting_type' &&
          field.apiName !== 'meeting_comments' &&
          // field.apiName !== 'Name' &&
          // field.apiName !== 'dealname' &&
          // field.apiName !== 'name' &&
          (this.resourceName === 'Contact' || this.resourceName === 'Lead'
            ? field.apiName !== 'email'
            : true) &&
          (this.resourceName === 'Contact' || this.resourceName === 'Lead'
            ? field.apiName !== 'Email'
            : true),
      )

      stageGateForms = formsRes.filter(
        (obj) =>
          obj.formType === 'STAGE_GATING' &&
          obj.resource === (this.userCRM === 'HUBSPOT' ? 'Deal' : 'Opportunity'),
      )

      if (stageGateForms.length) {
        // this.stageGateCopy = stageGateForms[0].fieldsRef

        let stages = stageGateForms.map((field) => field.stage)
        let newStages = []
        if (this.userCRM === 'HUBSPOT') {
          for (let i = 0; i < stages.length; i++) {
            newStages.push(stages[i].split(' ').join('').toLowerCase())
          }
        } else {
          newStages = stages
        }
        stagesWithForms = newStages
        for (const field of stageGateForms) {
          if (this.userCRM === 'SALESFORCE') {
            this.stageValidationFields[field.stage] = field.fieldsRef
          } else {
            this.stageValidationFields[field.stage.split(' ').join('').toLowerCase()] =
              field.fieldsRef
          }
        }
      }

      this.$emit('set-fields', allFields)
      this.$emit('set-stages', this.stageValidationFields, stagesWithForms)
    },
    getDate(input) {
      let newer = new Date(input)
      return newer.getDate()
    },
    getMonth(input) {
      let newer = new Date(input)
      return this.months[newer.getMonth()]
    },
    getYear(input) {
      let newer = new Date(input)
      return newer.getFullYear()
    },
    getTime(input) {
      let newer = new Date(input)
      let hours = newer.getHours()
      let minutes = newer.getMinutes()
      if (minutes < 10) {
        let newMinutes = '0' + minutes
        minutes = newMinutes
      }
      let afternoon = false
      if (hours === 0) {
        hours = 12
      } else if (hours === 12) {
        afternoon = true
      } else if (hours > 12) {
        hours = hours - 12
        afternoon = true
      }
      if (afternoon) {
        return `${hours}:${minutes} PM`
      } else {
        return `${hours}:${minutes} AM`
      }
    },
    async loadFromEnter() {
      if (this.searchText) {
        this.loadMorePage += 1
        this.loadingMore = true
        try {
          let res = await this.$store.dispatch('loadMoreChatOpps', {
            page: this.loadMorePage,
            text: this.searchText,
          })
        } catch (e) {
          console.log(e)
          this.page = 0
          this.loadMorePage = 0
        } finally {
          setTimeout(() => {
            this.loadingMore = false
          }, 300)
        }
      }
    },
    async loadMoreOpps() {
      if (this.searchText) {
        this.loadMorePage += 1
        this.loadingMore = true
        try {
          let res = await this.$store.dispatch('loadMoreChatOpps', {
            page: this.loadMorePage,
            text: this.searchText,
          })
        } catch (e) {
          console.log(e)
          this.page = 0
          this.loadMorePage = 0
        } finally {
          setTimeout(() => {
            this.loadingMore = false
          }, 300)
        }
      } else {
        this.page += 1
        this.loadingMore = true
        try {
          await this.$store.dispatch('loadChatOpps', this.page)
        } catch (e) {
          console.log(e)
        } finally {
          setTimeout(() => {
            this.loadingMore = false
          }, 300)
        }
      }
    },
  },
  computed: {
    hasZoomIntegration() {
      return !!this.$store.state.user.hasZoomIntegration
    },
    currentMeeting() {
      return this.$store.state.currentMeeting
    },
    opportunities() {
      if (this.displayedOpps.results) {
        return this.displayedOpps.results.filter((opp) =>
          opp.name.toLowerCase().includes(this.searchText.toLowerCase()),
        )
      } else return []
    },
    date() {
      let today = new Date()
      let month = String(today.getMonth() + 1).padStart(2, '0')
      let day = String(today.getDate()).padStart(2, '0')
      let year = today.getFullYear()
      let formattedDate = `${month}/${day}/${year}`

      return formattedDate
    },
    // meetings() {
    //   return this.$store.state.meetings
    // },
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
    activeFilters() {
      return this.$store.state.filters
    },
    displayedOpps: {
      get() {
        return this.$store.state.chatOpps
      },

      set(value) {
        this.displayedOpps = value
      },
    },
    userCRM() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.crm
    },
    user() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user
    },
    picklistOptions() {
      return this.$store.state.allPicklistOptions
    },
  },
  created() {
    if (this.userCRM === 'HUBSPOT') {
      this.resourceName = 'Deal'
    }
    this.$store.dispatch('loadChatOpps')
    this.$store.dispatch('loadAllPicklists')
    this.setOppForms()
    this.getMeetingWorkflows()
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
}

@keyframes shimmer {
  100% {
    -webkit-mask-position: left;
  }
}

.link {
  text-decoration: underline;
  text-decoration-color: $dark-black-blue;
  color: $dark-black-blue;
  display: inline-block;
  cursor: pointer;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 6px;
  padding: 0.75rem 0.75rem;
}

.dot {
  width: 4px;
  height: 4px;
  margin: 0 5px;
  background: rgb(97, 96, 96);
  border-radius: 50%;
  animation: bounce 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: -0.4s;
}

.dot:nth-child(3) {
  animation-delay: -0.2s;
}

.empty-container {
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 12px;
  border-radius: 5px;
  margin-top: 4px;
  padding: 2px 8px;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0;
  }
  40% {
    transform: scale(1);
    opacity: 1;
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

.switcher {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-evenly;
  background-color: $off-white;
  border: 1px solid $off-white;
  border-radius: 6px;
  padding: 2px 0;
  width: 100%;
  margin-bottom: 0.5rem;
}
.switch-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 0.25rem;
  border-radius: 6px;
  width: 100%;
  margin: 0 2px;
  cursor: pointer;
  color: $light-gray-blue;
  white-space: nowrap;
  img {
    filter: invert(63%) sepia(10%) saturate(617%) hue-rotate(200deg) brightness(93%) contrast(94%);
    margin-left: -0.25rem;
  }
}

.activeswitch {
  background-color: white;
  border: 1px solid $soft-gray;
  color: $base-gray;
  img {
    filter: none;
  }
}

.absolute-img {
  position: absolute;
  top: 1rem;
  right: 2px;
  // background-color: white;
}

.shimmer {
  animation: shimmer 2s;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/200% 100%;
}

.pop-transition {
  transition: transform 0.3s ease; /* Adjust the transition duration and easing as per your preference */
  transform: scale(1.25); /* Adjust the transform properties to create the desired effect */
  animation: shimmer 2s infinite;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/200% 100%;
}

::v-deep .multiselect__single {
  font-size: 14px;
}
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
}
::v-deep .multiselect__placeholder {
  color: $base-gray;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0;
  padding-top: 0.5rem;
  padding-bottom: 0.75rem;
  padding-left: 0.5rem;

  h4,
  p {
    margin: 0;
    font-size: 14px;
  }
}

.elipsis-text {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 300px;

  p {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin: 0;
    font-size: 14px !important;
  }
}

.right-container {
  position: sticky;
  background-color: white;
  // right: 0;
  // top: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  padding: 1rem 1.25rem 0 1.25rem;
  font-family: $base-font-family;
  font-size: 14px;
}
.text-cursor {
  cursor: text !important;
}
.opp-section {
  border: 1px solid #eeeeee;
  background-color: white;
  padding-left: 1rem;
  width: 99.75%;
  margin-left: 0.5px;
  border-radius: 5px;
  height: 100%;
  overflow-y: scroll;
}
.opp-container {
  background-color: white;
  position: relative;
  width: 100%;
  padding: 0.75rem 1rem;
  margin: 0.5rem 0;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s;

  p {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
  }

  &:hover {
    box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.05);

    background-color: $off-white;
  }
}

.rotate {
  transform: rotate(45deg);
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;

  span {
    img {
      padding-top: 4px;
    }
  }
}

.expand-absolute {
  position: absolute;
  right: 0.5rem;
  bottom: 0.75rem;
  background-color: white;
}
.opp-scroll-container {
  height: 100%;
  width: 101%;
  overflow-y: scroll;
  scroll-behavior: smooth;
  padding: 0;
  margin-top: -4px;
}

.opp-scroll-container::-webkit-scrollbar {
  width: 6px;
  height: 0px;
  margin-left: 0.25rem;
}
.opp-scroll-container::-webkit-scrollbar-thumb {
  background-color: transparent;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}
.opp-scroll-container:hover::-webkit-scrollbar-thumb {
  overflow: auto;
  scroll-behavior: smooth;
  background-color: $base-gray;
}
header {
  margin: 0;
  padding: 0;
  // border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  height: 80px;

  h4,
  p {
    margin: 0;
  }
}

.flexed-row {
  display: flex;
  flex-direction: row;
  align-items: center;

  p {
    color: $light-gray-blue;
  }
}

.pointer {
  cursor: pointer;
}

.flex-row-between {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.flexed-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  position: relative;

  h4,
  p {
    font-family: $base-font-family;
    font-size: 12px;
    letter-spacing: 0.4px;
  }
}

.flexed-row-spread__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  position: relative;
  padding: 0 4px 0 0;

  h4,
  p {
    font-family: $base-font-family;
    font-size: 12px;
    letter-spacing: 0.4px;
  }
}

.space-between {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;

  p {
    font-size: 14px;
    margin: 0 0 0.25rem 0.5rem;
    color: $light-gray-blue;
  }
}

.selected {
  border: 1px solid red;
}

.selected-opp {
  width: 100%;
  border-radius: 6px;
  background-color: $soft-gray;
  color: $base-gray;

  h4 {
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    font-size: 16px;
    font-weight: normal;
  }
}

.selected-opp:first-of-type {
  padding: 0.75rem 0.5rem;
}

.gray-bg {
  background: $off-white;
  padding-left: 0.5rem;
  padding-top: 1rem;
  background-color: $off-white !important;
  color: $base-gray;
  // border-top: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 0;
}

.right-absolute {
  position: absolute;
  right: 12px;
  top: 16px;
}

.text-ellipsis {
  width: 260px;

  p {
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }
}

.note-section {
  background-color: white;
  width: 409px;
  padding: 0 0.5rem 1rem 1rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 5px;
  margin: 0.5rem 0;
  position: relative;
}

.bordered {
  width: 100%;
  background-color: $off-white;
  // border: 1px solid rgba(0, 0, 0, 0.1) !important;
  padding: 2px 1px 2p 2px !important;
  border-radius: 5px;
  margin-top: 0.5rem;
}

.selected-opp-section {
  height: 100%;
  width: 100%;
  overflow-y: scroll;
  overflow-x: hidden;
  scroll-behavior: smooth;
  position: relative;
  h5,
  h4 {
    margin: 0rem;
  }
}

.selected-opp-section:first-of-type {
  height: 98.5%;
  width: 101%;
}

.selected-opp-section:last-of-type {
  height: 98%;
  width: 102%;
}

.selected-opp-section::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.selected-opp-section::-webkit-scrollbar-thumb {
  background-color: transparent;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px !important;
}
.selected-opp-section:hover::-webkit-scrollbar-thumb {
  background-color: $base-gray;
}

.sticky-top {
  position: sticky;
  top: 0;
  z-index: 10;
}

// .selected-opp-section:first-of-type {
//   border-bottom: 1px solid rgba(0, 0, 0, 0.1);
// }

.selected-opp-container {
  height: 100%;
  overflow-y: scroll;
  overflow-x: hidden;
  padding: 0 !important;
}

.input {
  width: 100%;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $base-font-family;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 0.25rem 0.25rem;
}

.search-input {
  width: 80%;
  padding: 0.5rem 0rem;
  border: none;
  outline: none;
}

.filter-input {
  width: 100%;
  outline: none;
  border-radius: 6px;
  border: 1px solid $soft-gray;
  font-family: $base-font-family;
  padding: 0.75rem 0.75rem;
  font-size: 13px;
  margin-top: 1rem;
}

::placeholder {
  color: #afafaf;
}

.right-mar-s {
  margin-right: 4px;
}

.gray-text {
  color: $light-gray-blue;
}
.small-text {
  font-size: 12px;
  margin-bottom: 0;
}
.zero-margin {
  padding: 0;
  margin: 0;
}
.neg-mar {
  margin-top: -0.25rem;
  font-size: 12px;
}
.left-margin {
  margin-left: 0.5rem;
}

.strike {
  text-decoration: line-through;
}

.edit-button {
  position: absolute;
  top: -4px;
  right: 8px;

  // button {
  //   @include chat-button();

  //   font-size: 13px;
  //   font-weight: normal;
  //   font-family: $base-font-family;
  //   color: $chat-font-color;
  //   background-color: white;
  //   padding: 0.75rem;
  // }
}

.chat-button {
  @include chat-button();
  padding: 0.75rem;
  font-size: 14px;
  font-family: $base-font-family;
  color: $chat-font-color;
  background-color: white;
  img {
    margin-left: 0;
  }
}

.no-border {
  border: none !important;
  background-color: transparent !important;

  &:hover {
    box-shadow: none !important;
  }
}

.gray-scale {
  color: $light-gray-blue !important;
  img {
    filter: invert(82%) sepia(2%) saturate(5238%) hue-rotate(201deg) brightness(78%) contrast(75%);
  }
}

.no-padding {
  padding: 0 !important;
}

svg,
img {
  margin: 0 0.5rem;
  cursor: pointer;
}

.icon-button {
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.45rem 0.25rem;
  background-color: white;
  border-radius: 6px;
  margin-left: 0.5rem;
  position: relative;
  cursor: pointer;
}

.invert {
  filter: invert(40%);
}

//  ALL THE FILTER STYLES BELOW , WILL BE MOING THESE TO THE COMPONENT WHEN IT'S READY
.filter-count {
  color: $dark-green;
  position: absolute;
  top: -4px;
  right: -4px;
  background-color: $white-green;
  padding: 0 4px;
  border-radius: 100%;
  box-shadow: 0 1px 3px 0 $dark-green;
  font-size: 8px;
}

.active-filters {
  padding: 1rem 0.5rem;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 0.5rem;
  div {
    width: fit-content;
    max-width: 50%;
    position: relative;

    p {
      background-color: $soft-gray;
      padding: 0.25rem;
      border-radius: 3px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    span {
      opacity: 0;
    }

    &:hover {
      span {
        opacity: 1;
        cursor: pointer;
      }
    }
  }
}

.remove {
  background-color: rgba(10, 0, 0, 0.6);
  color: white;
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 16px;
  font-size: 16px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bottom-border {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.filter-container {
  position: absolute;
  height: auto;
  min-height: 300px;
  max-height: 500px;
  width: 350px;
  background-color: white;
  z-index: 1000;
  top: 3.25rem;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 0 11px #b8bdc2;
  right: 0;

  header {
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0rem 1rem 1rem;

    p {
      font-size: 14px;
      margin: 0;
      padding: 0;
    }

    p:last-of-type {
      margin-top: -8px;
      margin-right: 12px;
      padding: 0.25rem;
      color: $light-gray-blue;
      font-size: 18px;
      cursor: pointer;
    }
  }

  section {
    padding: 1rem 0.45rem;
  }
}

.icon-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  margin-bottom: 8px;
  margin-left: 0.5rem;
  height: 30px;
  cursor: pointer;

  p {
    margin-right: 1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 14px;
  }

  svg {
    color: $light-gray-blue;
    margin-right: 1rem;
    background-color: white;
    border: 1px solid rgba(0, 0, 0, 0.1);
    height: 10px;
    width: 10px;
    padding: 0.25rem;
    border-radius: 6px;
    margin-left: 1px;
  }

  &:hover {
    color: $light-gray-blue;
  }
}

.active-filer {
  svg {
    color: $white-green;
    margin-right: 1rem;
    background-color: $dark-green;
    height: 12px;
    width: 12px;
    padding: 0.3rem;
    border-radius: 6px;
    margin-left: 1px;
  }
}

.slide-fade-enter-active {
  transition: all 0.2s ease-in;
}

.slide-fade-leave-active {
  transition: all 0.1s ease-out;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(100px);
}
//  ALL THE FILTER STYLES ABOVE , WILL BE MOING THESE TO THE COMPONENT WHEN IT'S READY

.icon-bg {
  display: flex;
  align-items: center;
  margin-left: -0.5rem;
}

.opaque {
  opacity: 0.3;
}

.not-allowed {
  cursor: not-allowed;
}

.rotate {
  animation: rotation 3s infinite linear;
}

.coming-soon {
  &:hover {
    cursor: not-allowed;
    opacity: 0.3;
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
.field {
  cursor: pointer;
}

.clear {
  margin-left: 1rem;
  background-color: $soft-gray;
  font-size: 11px;
  border-radius: 4px;
  padding: 4px;
}

.wrap-text {
  width: 90%;

  overflow: hidden;
}

.save-close {
  position: absolute;
  right: 0;
  top: -0.5rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  background-color: red;
  padding: 0.25rem;
  background-color: white;
}

.close {
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  outline: 1px solid rgba(0, 0, 0, 0.1);
  color: $coral;
  width: 40px;
  height: 20px;
  border-radius: 3px;
  cursor: pointer;
  margin-left: 0.5rem;
  margin-right: 2px;
  font-size: 11px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 3px 6px 0 $very-light-gray;
    scale: 1.025;
  }
}

.save {
  display: flex;
  align-items: center;
  justify-content: center;
  background: $dark-green;
  outline: 1px solid $dark-green;
  color: white;
  width: 36px;
  height: 20px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 3px 6px 0 $very-light-gray;
    scale: 1.025;
  }
}

.header-bg {
  background-color: white;
  padding: 0.75rem 0.5rem;
  border-radius: 5px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.tooltip {
  display: block;
  width: fit-content;
  height: auto;
  position: absolute;
  top: 0;
  left: 0;
  font-size: 14px;
  background: $base-gray;
  color: white;
  padding: 0.5rem;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  opacity: 0;
  pointer-events: none;
  line-height: 1.5;
  z-index: 20;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);

  header {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;

    p {
      margin: 0;
      padding: 0;
      margin-top: 0.25rem;
    }

    p:last-of-type {
      cursor: pointer;
      margin-top: -4px;
    }
  }
}

.neg-mar-small {
  margin-top: -4px;
}

.tooltip::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: $base-gray;
  bottom: -3px;
  left: 50%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.showing-tooltip {
  top: -40px;
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  text-shadow: 0px -1px 0px rgba(0, 0, 0, 0.1);
}

.inline-input {
  outline: none;
  padding: 0.5rem 0.75rem;
  border: 1px solid rgba(0, 0, 0, 0.15) !important;
  border-radius: 6px;
  color: $base-gray;
  width: 100%;
  margin-top: 4px;
  font-family: $base-font-family;
  font-size: 12px;
  line-height: 1.5;
  letter-spacing: 0.4px;
  resize: none;
}

.pointer {
  cursor: pointer;
}
</style>