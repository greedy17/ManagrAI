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
              style="height: 24px; width: 24px; color: #0d9dda"
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
          <p style="margin-bottom: 0.25rem">All Open Opportunities ({{ opportunities.length }})</p>

          <div class="flexed-row">
            <img src="@/assets/images/shuffle.svg" height="14px" alt="" />

            <img src="@/assets/images/refresh.svg" height="18px" alt="" />
          </div>
        </div>

        <div class="flexed-row-spread">
          <div class="input">
            <img src="@/assets/images/search.svg" height="16px" alt="" />
            <input v-model="searchText" placeholder="Search Opportunity by name" />
            <img
              v-show="searchText"
              @click="clearText"
              src="@/assets/images/close.svg"
              class="invert"
              height="12px"
              alt=""
            />
          </div>

          <span class="icon-button">
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
        @mouseenter="hoveredOpp = opp.id"
        @mouseleave="hoveredOpp = null"
      >
        <p style="margin: 0">{{ opp.name }}</p>

        <img
          v-show="hoveredOpp === opp.id"
          class="expand-absolute shadow"
          src="@/assets/images/expand.svg"
          height="14px"
          alt=""
        />
      </div>
    </div>
  </section>
</template>
  
<script>
import SlackOAuth from '@/services/slack'
import Tooltip from './Tooltip.vue'

export default {
  name: 'RightBar',
  components: {
    Tooltip,
  },
  data() {
    return {
      hoveredOpp: null,
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
    clearText() {
      this.searchText = ''
    },
    changeSelectedOpp(opp) {
      this.selectedOpp = opp
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

input {
  width: 80%;
  padding: 0.5rem 0rem;
  border: none;
  outline: none;
}

::placeholder {
  color: #afafaf;
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

.invert {
  filter: invert(40%);
}

.tooltip {
  position: relative;
  display: inline-block;
}

.tooltip .tooltiptext {
  visibility: hidden;
  width: 120px;
  background-color: $dark-green;
  color: white;
  text-align: center;
  padding: 0.5rem 0.25rem;
  border-radius: 4px;

  /* Position the tooltip text - see examples below! */
  position: absolute;
  z-index: 1;
  top: 100%;
  left: 50%;
  margin-left: -90px; /* Use half of the width to center the tooltip */
  margin-top: 4px;

  opacity: 0;
  transition: opacity 0.3s ease-in-out;
}

.tooltip:hover .tooltiptext {
  visibility: visible;
  opacity: 1;
}

.tooltip:hover {
  img {
    filter: invert(54%) sepia(76%) saturate(330%) hue-rotate(101deg) brightness(98%) contrast(89%);
  }
}

.tooltip .tooltiptext::after {
  content: ' ';
  position: absolute;
  bottom: 100%; /* At the top of the tooltip */
  left: 75%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: transparent transparent $dark-green transparent;
}
</style>