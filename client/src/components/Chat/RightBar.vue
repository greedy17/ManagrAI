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
            <font-awesome-icon style="height: 18px; width: 18px" icon="fa-solid fa-rotate" />
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
          <h4>All Open Opportunities ({{ opportunities.length }})</h4>

          <div>
            <font-awesome-icon icon="fa-solid fa-shuffle" />
            <font-awesome-icon icon="fa-solid fa-rotate" />
          </div>
        </div>

        <div class="flexed-row-spread">
          <input v-model="searchText" placeholder="Seach Opportunities by name" />
          <font-awesome-icon icon="fa-solid fa-filter" />
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
            <p>{{ note.value }}</p>
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
      </div>
    </div>
  </section>
</template>
  
<script>
import SlackOAuth from '@/services/slack'

export default {
  name: 'RightBar',
  components: {},
  data() {
    return {
      searchText: '',
      selectedOpp: null,
      updateOppForm: [],
      oppFields: [],
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
    async setOppForms() {
      const formsRes = await SlackOAuth.api.getOrgCustomForm()
      console.log('formsRes', formsRes)
      this.updateOppForm = formsRes.filter(
        (obj) =>
          obj.formType === 'UPDATE' && (obj.resource === 'Opportunity' || obj.resource === 'Deal'),
      )
      console.log('this.updateOppForm', this.updateOppForm)
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
      console.log('oppFields', this.oppFields)
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
  },
  computed: {
    opportunities() {
      return this.$store.state.allOpps.filter((opp) =>
        opp.name.toLowerCase().includes(this.searchText.toLowerCase()),
      )
    },
  },
  created() {
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
  font-family: $chat-font-family;
}
.opp-container {
  background-color: white;
  width: 100%;
  padding: 0.75rem 1rem;
  margin: 0.5rem 0 1rem 0;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  cursor: pointer;
}
.opp-scroll-container {
  height: 100%;
  overflow: scroll;
  padding: 0.5rem 0;
}

header {
  margin: 0%;
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

  h4 {
    font-family: $chat-title-family;
    color: rgba(0, 0, 0, 0.6);
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
  font-family: $chat-font-family;
  padding: 0.75rem;
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
    font-family: $chat-font-family;
    color: $chat-font-color;
    background-color: white;
  }
}

svg {
  margin: 0 0.5rem;
  cursor: pointer;
}
</style>