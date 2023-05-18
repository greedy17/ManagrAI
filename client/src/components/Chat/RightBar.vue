<template>
  <section class="right-container">
    <header>
      <section v-if="selectedOpp">
        <div class="flexed-row-spread">
          <div class="flexed-row">
            <font-awesome-icon
              @click="selectedOpp = null"
              style="height: 20px; width: 20px; margin-left: 0"
              icon="fa-solid fa-square-caret-left"
            />
            <p>Opportunity</p>
          </div>
          <div class="flexed-row">
            <img src="@/assets/images/refresh.svg" height="18px" alt="" />
            <font-awesome-icon
              style="height: 26px; width: 26px; color: #0d9dda"
              icon="fa-brands fa-salesforce"
            />
          </div>
        </div>
        <span class="selected-opp">
          <h4>{{ selectedOpp.name }}</h4>
        </span>
      </section>

      <section v-else>
        <div class="flexed-row-spread">
          <p style="margin-bottom: 0.25rem">All Open Opportunities ({{ displayedOpps.count }})</p>

          <div class="flexed-row">
            <img src="@/assets/images/shuffle.svg" height="14px" alt="" />
            <img src="@/assets/images/refresh.svg" height="18px" alt="" />
          </div>
        </div>

        <div class="flexed-row-spread">
          <input v-model="searchText" placeholder="Seach Opportunities by name" />
          <span class="icon-button" @click="switchFiltering">
            <img src="@/assets/images/filterlist.svg" height="20px" alt="" />
          </span>
        </div>
      </section>
    </header>

    <div class="selected-opp-container" v-if="selectedOpp">
      <div class="selected-opp-section">
        <div>
          <div v-for="field in oppFields" :key="field.id" style="margin-bottom: 1rem">
            <h5 class="gray-text">{{ field.label }}</h5>
            <div>{{ selectedOpp['secondary_data'][field.apiName] }}</div>
          </div>
        </div>

        <div class="edit-button">
          <button>Edit View</button>
        </div>
      </div>
      <div class="selected-opp-section">
        <h4 class="gray-text">Notes & History</h4>
        <div v-for="note in notes" :key="note.id">
          <div>
            <p style="margin: 0.25rem 0">{{ note.value }}</p>
          </div>
          <small class="gray-text">{{
            `${getMonth(note.date)} ${getDate(note.date)}, ${getYear(note.date)}`
          }}</small>
        </div>
      </div>
    </div>

    <div class="opp-scroll-container" v-else>
      <div
        v-for="opp in opportunities"
        class="opp-container"
        @click="changeSelectedOpp(opp)"
        :key="opp.id"
      >
        <p style="margin: 0">{{ opp.name }}</p>

        <!-- <img
          class="expand-absolute"
          src="@/assets/images/expand-content.svg"
          height="14px"
          alt=""
        /> -->
      </div>
      <div v-if="displayedOpps.next" @click="loadMoreOpps">Load More</div>
    </div>
  </section>
</template>
  
<script>
import SlackOAuth from '@/services/slack'
import { CRMObjects, ObjectField } from '@/services/crm'
// import Opportunity from '@/services/opportunity'
import CollectionManager from '@/services/collectionManager'

export default {
  name: 'RightBar',
  components: {
    
  },
  data() {
    return {
      searchText: '',
      selectedOpp: null,
      updateOppForm: [],
      oppFields: [],
      resourceName: 'Opportunity',
      objects: CollectionManager.create({
        ModelClass: CRMObjects,
        pagination: { size: 20 },
        // filters: {
        //   crmObject: 'Opportunity',
        // },
      }),
      page: 1,
      notes: [{ id: 0, value: 'Moved close date back to end of June', date: Date.now() }],
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
    }
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    changeSelectedOpp(opp) {
      this.selectedOpp = opp
    },
    async switchFiltering() {
      // this.$store.dispatch('changeFilters', [['EQUALS', 'Name', 'Marriot']])
      // await this.$store.dispatch('loadChatOpps', this.page)
      this.filtering = !this.filtering
    },
    selectFilter(name, type, label) {
      this.filtering = !this.filtering
      this.filterApiName = name
      this.filterType = type
      this.currentFilter = label
      this.filterSelected = true
    },
    async setOppForms() {
      const formsRes = await SlackOAuth.api.getOrgCustomForm()
      this.updateOppForm = formsRes.filter(
        (obj) =>
          obj.formType === 'UPDATE' && (obj.resource === 'Opportunity' || obj.resource === 'Deal'),
      )
      this.oppFields = this.updateOppForm[0].fieldsRef.filter(
        (field) =>
          field.apiName !== 'meeting_type' &&
          field.apiName !== 'meeting_comments' &&
          field.apiName !== 'Name' &&
          field.apiName !== 'dealname' &&
          field.apiName !== 'name' &&
          (this.resourceName === 'Contact' || this.resourceName === 'Lead'
            ? field.apiName !== 'email'
            : true) &&
          (this.resourceName === 'Contact' || this.resourceName === 'Lead'
            ? field.apiName !== 'Email'
            : true),
      )
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
    async loadMoreOpps() {
      this.page += 1
      await this.$store.dispatch('loadChatOpps', this.page)
    },
  },
  computed: {
    opportunities() {
      if (this.displayedOpps.results) {
        return this.displayedOpps.results.filter((opp) =>
          opp.name.toLowerCase().includes(this.searchText.toLowerCase()),
        )
      } else return []
    },
    displayedOpps() {
      return this.$store.state.chatOpps
    },
    userCRM() {
      return this.$store.state.user.crm
    },
  },
  async created() {
    if (this.userCRM === 'HUBSPOT') {
      this.resourceName = 'Deal'
    }
    this.$store.dispatch('changeFilters', [])
    await this.$store.dispatch('loadChatOpps')
    console.log('created displayedOpps', this.displayedOpps)
    this.setOppForms()
  },
}
</script>
  
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';

.right-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  padding: 1rem 1rem 0.25rem 1rem;
  font-family: $base-font-family;
  font-size: 14px;
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

  p {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
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
  overflow: hidden;
  padding: 0.5rem 0;
}

.opp-scroll-container:hover {
  overflow: auto;
  scroll-behavior: smooth;
}

.opp-scroll-container::-webkit-scrollbar {
  width: 6px;
  height: 0px;
  margin-left: 0.25rem;
}
.opp-scroll-container::-webkit-scrollbar-thumb {
  background-color: $base-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

header {
  margin: 0;
  padding: 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  height: 100px;

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

.flexed-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;

  h4,
  p {
    font-family: $base-font-family;
    font-size: 12px;
    letter-spacing: 0.4px;
  }
}

.selected-opp {
  display: block;
  width: 350px;
  border-radius: 6px;
  padding: 0.75rem;
  background-color: $soft-gray;
  margin-bottom: 1rem;

  h4 {
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }
}

.selected-opp-section {
  height: 50%;
  overflow-y: scroll;
  overflow-x: hidden;
  padding: 0.5rem 0rem;
  position: relative;
  h5,
  h4 {
    margin: 0.5rem 0rem;
  }
}

.selected-opp-section:first-of-type {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.selected-opp-container {
  height: 100%;
}

input {
  width: 87.5%;
  outline: none;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $base-font-family;
  padding: 0.75rem;
  font-size: 14px;
}

.gray-text {
  color: $light-gray-blue;
}

.edit-button {
  position: absolute;
  top: 1rem;
  right: 4px;

  button {
    @include chat-button();
    width: 100px;
    font-size: 14px;
    font-family: $base-font-family;
    color: $chat-font-color;
    background-color: white;
  }
}

svg,
img {
  margin: 0 0.5rem;
  cursor: pointer;
}

.icon-button {
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.5rem 0.25rem;
  background-color: white;
  border-radius: 6px;
  margin-left: 0.5rem;
}
</style>