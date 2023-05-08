<template>
  <section class="right-container">
    <div v-if="selectedOpp">
      <div class="display-flex">
        <div class="display-flex">
          <button class="right-button" @click="selectedOpp = null"><img class="right-button-icon" src="@/assets/images/back.svg" /></button>
          <p>Opportunity</p>
        </div>
        <div class="display-flex">
          <button class="right-button"><img class="right-button-icon" src="@/assets/images/cycle.svg" /></button>
          <button>Salesforce</button>
        </div>
      </div>
      <div>
        <h4>{{ selectedOpp.name }}</h4>
      </div>
      <div class="display-flex">
        <div>
          <div v-for="field in oppFields" :key="field.id" style="margin-bottom: 1rem;">
            <div @click="test(selectedOpp['secondary_data'][field.apiName])">{{ field.label }}</div>
            <div>{{ selectedOpp['secondary_data'][field.apiName] }}</div>
          </div>
        </div>
        <div>
          <button>Edit View</button>
        </div>
      </div>
      <div>
        <h4>Notes & History</h4>
        <div v-for="note in notes" :key="note.id">
          <div>
            <p>{{ note.value }}</p>
          </div>
          <div>{{ `${getMonth(note.date)} ${getDate(note.date)}, ${getYear(note.date)}` }}</div>
        </div>
      </div>
    </div>
    <div v-else>
      <div class="display-flex">
        <div>
          <h4>All Open Opportunities ({{ opportunities.length }})</h4>
        </div>
        <div class="display-flex">
          <button class="right-button"><img class="right-button-icon" src="@/assets/images/shuffle.svg" /></button>
          <button class="right-button"><img class="right-button-icon" src="@/assets/images/cycle.svg" /></button>
        </div>
      </div>
      <div class="display-flex">
        <input class="search__input" placeholder="Seach Opportunities by name" />
        <button class="right-button"><img class="right-button-icon" src="@/assets/images/filter-list.svg" /></button>
      </div>
      <div class="opp-scroll-container">
        <div v-for="opp in opportunities" :key="opp.id">
          <div class="opp-container" @click="changeSelectedOpp(opp)">
            <p style="margin: 0;">{{ opp.name }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
  
<script>
  import SlackOAuth from '@/services/slack'

  export default {
    name: 'RightBar',
    components: {

    },
    data() {
      return {
        // opportunities
        selectedOpp: null,
        updateOppForm: [],
        oppFields: [],
        notes: [
          { id: 0, value: 'Moved close date back to end of June', date: Date.now() }
        ],
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
          (obj) => obj.formType === 'UPDATE' && (obj.resource === 'Opportunity' || obj.resource === 'Deal'),
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
        return this.$store.state.allOpps
      }
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
    height:100%;
    padding: 2.5rem .5rem;
  }
  .display-flex {
    display: flex;
  }
  .opp-container {
    background-color: $soft-gray;
    padding: 0.5rem 1rem;
    margin: 0.5rem 0.5rem;
    border-radius: 4px;
  }
  .opp-scroll-container {
    height: 55vh;
    overflow: scroll;
    border-top: 1px solid $very-light-gray;
    padding: 0.5rem 0;
    margin: 0.5rem 0;
  }
  .search__input {
    min-height: 40px;
    display: block;
    padding: 8px 8px 8px 8px;
    border-radius: 5px;
    border: 1px solid #e8e8e8;
    background: #fff;
    font-size: 14px;
    box-shadow: none;
    width: 70%;
  }
  .right-button-icon {
    height: 20px;
  }
</style>