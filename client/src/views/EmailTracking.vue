<template>
  <div class="tracking fadein">
    <section class="space-between">
      <div class="row">
        <div class="relative">
          <div
            style="margin-left: -4px"
            @click.stop="toggleUserDropdown"
            class="drop-header"
            :class="{ 'soft-gray-bg': showUsers }"
          >
            <img class="mobile-img" src="@/assets/images/profile.svg" height="12px" alt="" />
            User:
            <small>
              {{
                !selectedUser
                  ? 'All'
                  : selectedUser.fullName
                  ? selectedUser.fullName
                  : selectedUser.full_name
              }}
            </small>
            <img
              v-if="!showUsers"
              style="margin-left: 8px"
              src="@/assets/images/arrowDropUp.svg"
              height="14px"
              alt=""
            />
            <img
              v-else
              class="rotate-img"
              src="@/assets/images/arrowDropUp.svg"
              height="14px"
              alt=""
            />
          </div>

          <div v-outside-click="hideUsers" style="left: 0" v-show="showUsers" class="dropdown">
            <div class="dropdown-header">
              <h3>Select User</h3>
            </div>
            <div class="dropdown-body">
              <div class="col">
                <div v-if="!searchUsersText" @click="selectAllUsers" class="dropdown-item">All</div>
                <div
                  @click="selectUser(user)"
                  class="dropdown-item"
                  v-for="(user, i) in allUsers"
                  :key="i"
                >
                  {{ user.full_name }}
                </div>
              </div>
            </div>

            <div class="dropdown-footer"></div>
          </div>
        </div>
        <div style="margin: 0 8px" class="relative">
          <div
            @click="toggleFilterDropdown"
            class="icon-btn"
            :class="{ 'img-container-stay': showFilters }"
          >
            <img src="@/assets/images/filter.svg" height="11px" alt="" />
            Add filter
          </div>

          <!-- <button @click="toggleFilterDropdown" class="secondary-button-no-border">
            <img src="@/assets/images/add.svg" height="14px" alt="" /> Add Filter
          </button> -->

          <div v-show="showFilters" class="dropdown" style="left: 0">
            <div class="dropdown-header">
              <h3>Filters</h3>
              <img
                @click="toggleFilterDropdown"
                src="@/assets/images/close.svg"
                class="pointer"
                height="18px"
                alt=""
                style="margin-right: 12px"
              />
            </div>

            <div style="padding: 0 16px" class="dropdown-body">
              <div class="row" style="width: 100%; overflow-x: scroll">
                <div v-if="failedFilter !== null">
                  <button
                    style="margin: 0 4px 0 0; white-space: nowrap"
                    class="primary-button lb-bg"
                  >
                    <div @click="removeFailedFilter">
                      <img src="@/assets/images/close.svg" height="14px" alt="" />
                    </div>
                    Status -
                    {{ failedFilter === true ? 'failed' : 'delivered' }}
                  </button>
                </div>

                <div v-if="statusFilter !== null">
                  <button
                    style="margin: 0 4px 0 0; white-space: nowrap"
                    class="primary-button lb-bg"
                  >
                    <div @click="removeStatusFilter">
                      <img src="@/assets/images/close.svg" height="14px" alt="" />
                    </div>
                    Status -
                    {{ statusFilter === 'is_approved' ? 'approved' : 'rejected' }}
                  </button>
                </div>

                <div v-if="draftFilter !== null">
                  <button
                    style="margin: 0 4px 0 0; white-space: nowrap"
                    class="primary-button lb-bg"
                  >
                    <div @click="removeDraftFilter">
                      <img src="@/assets/images/close.svg" height="14px" alt="" />
                    </div>
                    Status - draft
                  </button>
                </div>

                <div v-if="activityFilter">
                  <button
                    style="margin: 0 4px 0 0; white-space: nowrap"
                    class="primary-button lb-bg"
                  >
                    <div @click="removeActivityFilter">
                      <img src="@/assets/images/close.svg" height="14px" alt="" />
                    </div>

                    {{ convertDates(activityFilter) }}
                  </button>
                </div>
              </div>
              <div class="col">
                <p>Status</p>
                <!-- <div class="status-dropdown">
                  <div class="status-dropdown-header">Select status</div>

                  <div class="status-dropdown-body">
                    <div class="status-dropdown-item">Delivered</div>
                    <div class="status-dropdown-item">Failed</div>
                    <div class="status-dropdown-item">Approved</div>
                    <div class="status-dropdown-item">Rejected</div>
                    <div class="status-dropdown-item">Draft</div>
                  </div>
                </div> -->
                <div class="radio-group">
                  <label class="radio-label">
                    <input
                      type="radio"
                      name="draft"
                      value="is_rejected"
                      :checked="draftStatus === 'is_rejected'"
                      @click="toggleSelection('draftStatus', 'is_rejected')"
                    />
                    <span class="custom-radio"></span>
                    Draft
                  </label>

                  <label class="radio-label">
                    <input
                      type="radio"
                      name="rejected"
                      value="is_rejected"
                      :checked="selectedStatus === 'is_rejected'"
                      @click="toggleSelection('selectedStatus', 'is_rejected')"
                    />
                    <span class="custom-radio"></span>
                    Rejected
                  </label>

                  <label style="margin-left: -8px" class="radio-label">
                    <input
                      type="radio"
                      name="approved"
                      value="is_approved"
                      :checked="selectedStatus === 'is_approved'"
                      @click="toggleSelection('selectedStatus', 'is_approved')"
                    />
                    <span class="custom-radio"></span>
                    Approved
                  </label>

                  <label class="radio-label">
                    <input
                      type="radio"
                      name="failed"
                      :value="true"
                      :checked="selectedOption === true"
                      @click="toggleSelection('selectedOption', true)"
                    />
                    <span class="custom-radio"></span>
                    Failed
                  </label>

                  <label class="radio-label">
                    <input
                      type="radio"
                      name="delivered"
                      :value="false"
                      :checked="selectedOption === false"
                      @click="toggleSelection('selectedOption', false)"
                    />
                    <span class="custom-radio"></span>
                    Delivered
                  </label>
                </div>
              </div>
              <div class="col top-border">
                <p>Last Activity</p>

                <div style="width: 100%">
                  <input class="area-input-smallest" type="date" v-model="dateStart" />
                  -
                  <input class="area-input-smallest" type="date" v-model="dateEnd" />
                </div>
              </div>
              <!-- <p>Journalist</p> -->
            </div>

            <div class="dropdown-footer">
              <button @click="applyFilters" class="primary-button" style="margin-right: 12px">
                Apply
              </button>
            </div>
          </div>
        </div>

        <div @click="convertData" class="icon-btn">
          <img src="@/assets/images/download.svg" height="11px" alt="" />
          Export table
        </div>
      </div>

      <div class="search">
        <div class="input">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
              fill="currentColor"
            ></path>
          </svg>
          <input v-model="searchEmailText" class="search-input" :placeholder="`Search...`" />
          <img
            v-if="searchEmailText"
            @click="clearSearchText"
            src="@/assets/images/close.svg"
            class="pointer"
            height="12px"
            alt=""
          />
        </div>
      </div>
    </section>

    <div class="table-container">
      <EmailTable
        :searchText="searchEmailText"
        :failedFilter="failedFilter"
        :statusFilter="statusFilter"
        :draftFilter="draftFilter"
        :activityFilter="activityFilter"
        :userId="selectedUser ? selectedUser.id : null"
        @emails-updated="setEmailValues"
      />
    </div>
  </div>
</template>

<script>
import EmailTable from '../components/EmailTable.vue'
import User from '@/services/users'

export default {
  name: 'EmailTracking',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    EmailTable,
  },
  data() {
    return {
      newInsight: '',
      loadingInsight: false,
      insight: '',
      searchEmailText: '',
      searchUsersText: '',
      showFilters: false,
      showUsers: false,
      selectedOption: null,
      selectedStatus: null,
      draftStatus: null,
      dateStart: '',
      dateEnd: '',
      failedFilter: null,
      statusFilter: null,
      draftFilter: null,
      activityFilter: null,
      selectedUser: null,
      users: [],
      emailValues: null,
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    allUsers() {
      return this.users.filter((user) =>
        user.full_name.toLowerCase().includes(this.searchUsersText),
      )
    },
  },
  mounted() {},
  created() {
    this.selectedUser = this.user
    this.getUsers()
  },
  methods: {
    async getInsight() {
      this.loadingInsight = true
      try {
        const res = await Comms.api.getInsight({
          notes: this.currentContact.notes,
          activity: this.activities,
          bio: this.currentContact.bio,
          instructions: this.insight,
        })
        this.newInsight = res.content.replace(/\*(.*?)\*/g, '<strong>$1</strong>')
      } catch (e) {
        console.error(e)
      } finally {
        this.insight = ''
        this.loadingInsight = false
      }
    },
    toggleSelection(model, value) {
      if (this[model] === value) {
        this[model] = null
      } else {
        this[model] = value
      }
    },
    setEmailValues(value) {
      this.emailValues = value
    },
    formatActivityLog(logEntry, fullEntry = false) {
      const [action, dateTime] = logEntry.split('|')
      const date = new Date(dateTime)
      const now = new Date()
      const diffInMilliseconds = now - date
      const diffInMinutes = Math.floor(diffInMilliseconds / (1000 * 60))
      const diffInHours = Math.floor(diffInMilliseconds / (1000 * 60 * 60))
      const diffInDays = Math.floor(diffInMilliseconds / (1000 * 60 * 60 * 24))

      let formattedTime
      if (diffInMinutes < 120) {
        formattedTime = `${diffInMinutes - 60} minute${diffInMinutes - 60 !== 1 ? 's' : ''} ago`
      } else if (diffInHours < 24) {
        formattedTime = `${diffInHours} hour${diffInHours !== 1 ? 's' : ''} ago`
      } else if (diffInDays < 30) {
        formattedTime = `${diffInDays} day${diffInDays !== 1 ? 's' : ''} ago`
      } else {
        const formattedDate = `${date.getMonth() + 1}/${date.getDate()}/${String(
          date.getFullYear(),
        ).slice(-2)}`
        formattedTime = `on ${formattedDate}`
      }

      if (fullEntry) {
        return `${action.charAt(0).toUpperCase() + action.slice(1)} - ${formattedTime}`
      } else {
        return formattedTime
      }
    },

    convertData() {
      let csvData = this.emailValues.map((email) => ({
        email: email.subject + ':' + email.body.replace(/<\/?[^>]+(>|$)/g, ''),
        to: email.recipient,
        publication:
          email.journalist_ref && email.journalist_ref.outlet
            ? email.journalist_ref.outlet
            : 'Unknown',
        status: email.failed ? 'failed' : 'Delivered',
        opens: email.opens,
        clicks: email.clicks,
        replies: email.replies,
        lastActivity: this.formatActivityLog(email.activity_log.at(-1)),
      }))

      this.arrayToCSV(csvData)
    },

    arrayToCSV(data) {
      const csvRows = []

      const headers = Object.keys(data[0])
      csvRows.push(headers.join(','))

      // Loop over the rows
      for (const row of data) {
        const values = headers.map((header) => {
          const escaped = ('' + row[header]).replace(/"/g, '\\"')
          return `"${escaped}"`
        })
        csvRows.push(values.join(','))
      }

      const csvString = csvRows.join('\n')

      this.downloadCSV(csvString)
    },

    downloadCSV(csvString, filename = 'managr-tracker.csv') {
      const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = filename
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    async getUsers() {
      try {
        const res = await User.api.getAllUsers()
        this.users = res.results.filter((user) => user.organization == this.user.organization)
      } catch (e) {
        console.log('Error in getTrialUsers', e)
      }
    },
    clearSearchText() {
      this.searchEmailText = ''
    },
    clearUsersText() {
      this.searchUsersText = ''
    },
    toggleFilterDropdown() {
      this.showFilters = !this.showFilters
    },
    hideFilters() {
      this.showFilters = false
    },
    toggleUserDropdown() {
      this.showUsers = !this.showUsers
    },
    hideUsers() {
      this.showUsers = false
    },
    applyFilters() {
      if (this.dateStart && this.dateEnd) {
        this.activityFilter = `${this.dateStart},${this.dateEnd}`
      }

      if (this.selectedOption !== null) {
        this.failedFilter = this.selectedOption
      }

      if (this.selectedStatus !== null) {
        this.statusFilter = this.selectedStatus
      }

      if (this.draftStatus !== null) {
        this.draftFilter = this.draftStatus
      }
      this.toggleFilterDropdown()
    },
    selectUser(user) {
      this.selectedUser = user
      this.toggleUserDropdown()
    },
    selectAllUsers() {
      this.selectedUser = null
      this.toggleUserDropdown()
    },
    removeFailedFilter() {
      this.failedFilter = null
    },
    removeStatusFilter() {
      this.statusFilter = null
    },
    removeDraftFilter() {
      this.draftFilter = null
    },
    removeActivityFilter() {
      this.activityFilter = null
    },
    convertDates(dates) {
      const [firstDate, secondDate] = dates.split(',')
      const [year, month, day] = firstDate.split('-')
      const newFirstDate = `${month}/${day}/${year.slice(-2)}`
      const [yr, m, d] = secondDate.split('-')
      const newSecondDate = `${m}/${d}/${yr.slice(-2)}`

      return `${newFirstDate} - ${newSecondDate}`
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.tracking {
  width: 100vw;
  height: 88vh;
  margin: 0 auto;
  // padding: 72px 32px 16px 32px;
  padding: 100px 96px 32px 96px;
  font-family: $thin-font-family;
  color: $dark-black-blue;

  @media only screen and (max-width: 600px) {
    padding: 108px 10px 64px 10px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    padding: 108px 10px 64px 10px;
  }
}

.image-container {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  background-color: white;
  margin-left: 16px;
  transition: all 0.25s;

  img {
    filter: invert(40%);
  }

  &:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transform: scale(1.1);
  }
}

.table-container {
  border: 1px solid rgba(0, 0, 0, 0.1);
  // box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  margin-top: 24px;
  height: 100%;
  background-color: white;
  overflow: scroll;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.primary-button {
  @include dark-blue-button();
  border: none;
  border-radius: 16px;

  img {
    filter: invert(100%);
    margin-right: 4px;
  }
}

.secondary-button {
  @include dark-blue-button();
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: $dark-black-blue;
  border-radius: 16px;
}

.secondary-button-no-border {
  @include dark-blue-button();
  border-radius: 16px;
  padding: 6px 12px;
  border: none;
  color: $dark-black-blue;
  background-color: white;
  margin: 0;
  transition: none;
  font-size: 14px;

  img {
    margin-right: 4px;
  }

  &:hover {
    background-color: $soft-gray;
    transform: none !important;
    box-shadow: none;
  }
}

.space-between {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  // border: 1px solid rgba(0, 0, 0, 0.1);
  // background-color: white;
  // padding: 16px ;
  border-radius: 6px;
  margin-left: -2px;
  // box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

::placeholder {
  color: rgba(0, 0, 0, 0.4);
}

.input {
  position: sticky;
  z-index: 8;
  top: 1.5rem;
  width: 28vw;
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $thin-font-family;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 10px 20px 10px 10px;

  @media only screen and (max-width: 600px) {
    width: 40vw;
  }
}

.search-input {
  border: none;
  outline: none;
  margin-left: 0.5rem;
  width: 100%;
}

.pointer {
  cursor: pointer;
}

.relative {
  position: relative;
}
.dropdown {
  position: absolute;
  top: 40px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  // padding: 8px;
  left: 16px;
  z-index: 9;
  min-width: 25vw;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);

  .dropdown-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    // padding: 0 8px;

    h3 {
      font-family: $base-font-family;
      font-weight: 200;
      width: 100%;
      padding: 0 16px;
    }

    img {
      margin-right: 8px;
    }
  }

  .dropdown-body {
    // padding: 0 8px;
    max-height: 250px;
    overflow: scroll;
  }

  .dropdown-item {
    padding: 8px 16px;
    cursor: pointer;
    width: 100%;

    &:hover {
      background-color: $soft-gray;
    }
  }

  .dropdown-item:last-of-type {
    border-bottom: none;
  }

  .dropdown-item:hover {
    opacity: 0.7;
  }

  .dropdown-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding: 24px 8px 12px 8px;
  }
}

.col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;

  p {
    font-family: $base-font-family;
  }
}

.radio-group {
  width: 300px;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 16px 20px;
}

.radio-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  position: relative;
  padding-left: 24px;
  font-size: 14px;
  user-select: none;
  width: 80px;
}

.radio-label input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
}

.custom-radio {
  position: absolute;
  top: 50%;
  left: 0;
  transform: translateY(-50%);
  height: 12px;
  width: 12px;
  background-color: white;
  border-radius: 50%;
  border: 3px solid rgba(0, 0, 0, 0.1);
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.radio-label input:checked ~ .custom-radio {
  background-color: $lite-blue;
  border-color: $lite-blue;
}

.custom-radio::after {
  content: '';
  position: absolute;
  display: none;
}

.radio-label input:checked ~ .custom-radio::after {
  display: block;
}

.radio-label .custom-radio::after {
  top: 50%;
  left: 50%;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: white;
  border: 3px solid $lite-blue;
  transform: translate(-50%, -50%);
}

.area-input-smallest {
  background-color: $off-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 4px 8px 5px 8px;
  line-height: 1.75;
  width: 48%;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 13px;
  font-family: $thin-font-family !important;
  font-weight: 400;
  border: 1px solid rgba(0, 0, 0, 0.1);
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
  cursor: pointer;
  border-radius: 4px;
}

.area-input-smallest:last-of-type {
  @media only screen and (max-width: 600px) {
  }
}

.lb-bg {
  background-color: $white-blue;
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: $dark-black-blue;
  padding-left: 28px;
  position: relative;

  &:hover {
    box-shadow: none;
    scale: 1;
  }

  div {
    position: absolute;
    left: 4px;
    padding: 4px;
    background-color: $soft-gray;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;

    img {
      filter: none;
      margin: 0;
    }
  }

  div:hover {
    opacity: 0.4;
  }
}

.lb-bg:hover {
  box-shadow: none;
}

.top-border {
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  margin-top: 1.2rem;
}

.wrapper {
  display: flex;
  align-items: center;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.wrapper .tooltip {
  z-index: 10000;
  background: $dark-black-blue;
  border-radius: 4px;
  bottom: 100%;
  color: #fff;
  display: block;
  left: -34px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 100px;
  -webkit-transform: translateY(10px);
  -moz-transform: translateY(10px);
  -ms-transform: translateY(10px);
  -o-transform: translateY(10px);
  transform: translateY(10px);
  -webkit-transition: all 0.25s ease-out;
  -moz-transition: all 0.25s ease-out;
  -ms-transition: all 0.25s ease-out;
  -o-transition: all 0.25s ease-out;
  transition: all 0.25s ease-out;
  -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}

.wrapper .tooltip:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-top: solid $dark-black-blue 10px;
  bottom: -10px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper:hover .tooltip {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .wrapper .tooltip {
  display: none;
}

.lte8 .wrapper:hover .tooltip {
  display: block;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

.fadein {
  transition: opacity 1s ease-out;
  opacity: 0;
  animation: fadeIn 0.5s forwards;
}

.img-container {
  cursor: pointer;
  padding: 5px 7px 4px 7px;
  border-radius: 50%;
  &:hover {
    background-color: $soft-gray;
  }

  img {
    margin: 0;
    padding: 0;
  }
}

.img-container-stay {
  padding: 5px 7px 4px 7px;
  border-radius: 50%;
  background-color: $soft-gray;

  img {
    margin: 0;
    padding: 0;
  }
}

.s-tooltip {
  visibility: hidden;
  width: 100px;
  background-color: $graper;
  color: white;
  text-align: center;
  border-radius: 4px;
  padding: 6px 2px;
  position: absolute;
  z-index: 100;
  bottom: 130%;
  left: 50%;
  margin-left: -50px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  // border: 1px solid rgba(0, 0, 0, 0.328);
  font-size: 13px;
  line-height: 1.4;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.s-tooltip-below {
  visibility: hidden;
  width: 80px;
  background-color: $graper;
  color: white;
  text-align: center;
  border-radius: 4px;
  padding: 6px 2px;
  position: absolute;
  z-index: 100;
  top: 130%;
  left: 50%;
  margin-left: -40px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  font-size: 13px;
  line-height: 1.4;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.s-wrapper {
  position: relative;
  display: inline-block;
}

.s-wrapper:hover .s-tooltip,
.s-wrapper:hover .s-tooltip-below {
  visibility: visible;
  opacity: 1;
}

.drop-header {
  padding: 8px;
  background-color: $off-white;
  font-size: 14px;
  // border: 0.5px solid rgba(0, 0, 0, 0.355);
  border-radius: 16px;
  display: flex;
  flex-direction: row;
  align-items: center;
  cursor: pointer;

  img {
    margin: 0 4px 0 8px;
  }

  small {
    font-size: 14px;
    margin-left: 4px !important;
    font-family: $base-font-family;
  }

  p,
  small {
    margin: 0;
    padding: 0;
  }

  &:hover {
    background-color: $soft-gray;
  }
}

.rotate-img {
  transform: rotate(180deg);
}

.soft-gray-bg {
  background-color: $soft-gray;
}

input {
  font-family: $thin-font-family;
}

::placeholder {
  font-family: $thin-font-family;
}

.mobile-img {
  @media only screen and (max-width: 600px) {
    display: none;
  }
}

::v-deep ::selection {
  background-color: $lite-blue !important;
  color: white;
}

.status-dropdown {
  position: relative;
  width: 100%;
  &-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 6px;
    padding: 8px;
  }

  &-body {
    position: absolute;
    width: 100%;
    background-color: white;
    z-index: 1000;
    top: 40px;
    border: 1px solid rgba(0, 0, 0, 0.1);
    padding: 8px;
    box-shadow: 3px 11px 16px;
  }

  &-item {
  }
}

.icon-btn {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 16px;
  padding: 6px 8px;
  margin: 0 10px;
  width: 140px;
  cursor: pointer;
  font-family: $base-font-family;
  img {
    margin-right: 6px;
  }
  &:hover {
    background-color: $soft-gray;
  }
}
</style>
