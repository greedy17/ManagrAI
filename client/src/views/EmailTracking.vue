<template>
  <div class="tracking">
    <h2>Track your outreach</h2>

    <section class="space-between">
      <div class="row">
        <div class="relative">
          <button @click="toggleUserDropdown" class="secondary-button">
            {{ selectedUser.fullName ? selectedUser.fullName : selectedUser.full_name }}
            <img src="@/assets/images/dropdown.svg" height="14px" alt="" />
          </button>

          <div style="left: 0" v-if="showUsers" class="dropdown">
            <div class="dropdown-header">
              <h3>Select User</h3>
              <img
                @click="toggleUserDropdown"
                src="@/assets/images/close.svg"
                class="pointer"
                height="18px"
                alt=""
              />
            </div>

            <div class="dropdown-body">
              <div class="col">
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

        <div class="relative">
          <button @click="toggleFilterDropdown" class="primary-button">
            <img src="@/assets/images/add.svg" height="12px" alt="" /> Add Filter
          </button>
          <div v-if="showFilters" class="dropdown">
            <div class="dropdown-header">
              <h3>Filters</h3>
              <img
                @click="toggleFilterDropdown"
                src="@/assets/images/close.svg"
                class="pointer"
                height="18px"
                alt=""
              />
            </div>

            <div class="dropdown-body">
              <div class="col">
                <p>Status</p>
                <div class="radio-group">
                  <label class="radio-label">
                    <input type="radio" name="option" :value="false" v-model="selectedOption" />
                    <span class="custom-radio"></span>
                    Delivered
                  </label>
                  <label class="radio-label">
                    <input type="radio" name="option" :value="true" v-model="selectedOption" />
                    <span class="custom-radio"></span>
                    Failed
                  </label>
                </div>
              </div>
              <div class="col">
                <p>Last Activity</p>

                <div>
                  <input class="area-input-smallest" type="date" v-model="dateStart" />
                  -
                  <input class="area-input-smallest" type="date" v-model="dateEnd" />
                </div>
              </div>
              <!-- <p>Journalist</p> -->
            </div>

            <div class="dropdown-footer">
              <button @click="applyFilters" class="primary-button">Apply</button>
            </div>
          </div>
        </div>

        <div v-if="failedFilter !== null">
          <button class="primary-button lb-bg">
            <div @click="removeFailedFilter">
              <img src="@/assets/images/close.svg" height="14px" alt="" />
            </div>
            Status -
            {{ failedFilter === true ? 'failed' : 'delivered' }}
          </button>
        </div>

        <div v-if="activityFilter">
          <button class="primary-button lb-bg">
            <div @click="removeActivityFilter">
              <img src="@/assets/images/close.svg" height="14px" alt="" />
            </div>

            {{ convertDates(activityFilter) }}
          </button>
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
        :activityFilter="activityFilter"
        :userId="selectedUser.id"
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
      searchEmailText: '',
      showFilters: false,
      showUsers: false,
      selectedOption: null,
      dateStart: '',
      dateEnd: '',
      failedFilter: null,
      activityFilter: null,
      selectedUser: null,
      allUSers: [],
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
  },
  mounted() {},
  created() {
    this.selectedUser = this.user
    this.getUsers()
  },
  methods: {
    async getUsers() {
      try {
        const res = await User.api.getAllUsers()
        this.allUsers = res.results
        console.log(res.results)
      } catch (e) {
        console.log('Error in getTrialUsers', e)
      }
    },
    clearSearchText() {
      this.searchEmailText = ''
    },
    toggleFilterDropdown() {
      this.showFilters = !this.showFilters
    },
    toggleUserDropdown() {
      this.showUsers = !this.showUsers
    },
    applyFilters() {
      if (this.dateStart && this.dateEnd) {
        this.activityFilter = `${this.dateStart},${this.dateEnd}`
      }

      if (this.selectedOption !== null) {
        this.failedFilter = this.selectedOption
      }
      this.toggleFilterDropdown()
    },
    selectUser(user) {
      this.selectedUser = user
      this.toggleUserDropdown()
    },
    removeFailedFilter() {
      this.failedFilter = null
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
  height: 80vh;
  margin: 0 auto;
  padding: 72px 32px 16px 32px;
  font-family: $thin-font-family;
}

.table-container {
  border: 1px solid rgba(0, 0, 0, 0.1);
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

.space-between {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

::placeholder {
  color: rgba(0, 0, 0, 0.4);
}

.input {
  position: sticky;
  z-index: 8;
  top: 1.5rem;
  width: 300px;
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $thin-font-family;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 10px 20px 10px 10px;
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
  padding: 8px;
  left: 16px;
  z-index: 6;
  min-width: 25vw;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);

  .dropdown-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    img {
      margin-right: 8px;
    }
  }

  .dropdown-body {
    padding: 0 8px;
    max-height: 250px;
    overflow: scroll;
  }

  .dropdown-item {
    margin: 8px 0;
    cursor: pointer;
    width: 100%;
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
  display: flex;
  flex-direction: row;
  gap: 16px;
}

.radio-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  position: relative;
  padding-left: 24px;
  font-size: 14px;
  user-select: none;
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
  height: 20px;
  width: 20px;
  background-color: #f0f0f0;
  border-radius: 50%;
  border: 2px solid #dcdcdc;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.radio-label input:checked ~ .custom-radio {
  background-color: $dark-blue;
  border-color: $dark-black-blue;
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
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: white;
  transform: translate(-50%, -50%);
}

.area-input-smallest {
  background-color: $off-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 2px 0.5rem 2px 2px;
  line-height: 1.75;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 13px;
  font-family: $thin-font-family !important;
  font-weight: 400;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
  cursor: pointer;
  border-radius: 4px;
}

.area-input-smallest:last-of-type {
  padding-left: 0.5rem;

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
</style>
