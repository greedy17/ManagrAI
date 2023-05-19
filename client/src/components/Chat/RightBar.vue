<template>
  <section class="right-container">
    <header>
      <section v-if="selectedOpp">
        <div class="flexed-row-spread">
          <div class="flexed-row">
            <font-awesome-icon
              @click="selectedOpp = null"
              style="height: 20px; width: 20px; margin-left: 0; color: #27292c"
              icon="fa-solid fa-square-caret-left"
            />
            <!-- <img src="@/assets/images/back.svg" height="14px;width:14px" alt=""> -->
            <p>Opportunity</p>
          </div>
          <div class="flexed-row">
            <img src="@/assets/images/refresh.svg" height="18px" alt="" />

            <font-awesome-icon
              style="height: 24px; width: 24px; color: #0d9dda"
              icon="fa-brands fa-salesforce"
              @click="openInCrm(selectedOpp.integration_id)"
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
          <div class="input">
            <img src="@/assets/images/search.svg" height="16px" alt="" />
            <input
              class="search-input"
              v-model="searchText"
              placeholder="Search Opportunity by name"
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
            <img src="@/assets/images/filterlist.svg" height="20px" alt="" />
            <small
              v-if="activeFilters.length"
              :class="{ 'pop-transition': isPopping }"
              class="filter-count"
              >{{ activeFilters.length }}</small
            >
          </span>

          <div v-show="filtersOpen" class="filter-container">
            <header>
              <p v-if="!selectedFilter">Select Filters</p>

              <div v-else @click="selectedFilter = null" class="flexed-row pointer">
                <font-awesome-icon
                  style="height: 20px; width: 20px; margin-left: 0; color: #27292c"
                  icon="fa-solid fa-square-caret-left"
                />

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
                  :options="operators"
                  @select="selectOperator($event.value, $event.label)"
                  openDirection="below"
                  selectLabel=""
                  track-by="value"
                  label="label"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                </Multiselect>

                <div v-if="selectedFilter.operator">
                  <input
                    class="filter-input"
                    :placeholder="`${selectedFilter.name} ${selectedFilter.operatorLabel}`"
                    :type="`${selectedFilter.dataType}`"
                    v-model="selectedFilter.value"
                    autofocus="true"
                  />
                </div>

                <div style="margin: 1rem 0 1rem 0.25rem" v-if="selectedFilter.value">
                  <p>
                    <span style="color: #9596b4">Filter : </span>
                    "{{ selectedFilter.name }} is {{ selectedFilter.operatorLabel }}
                    {{ selectedFilter.value }}"
                  </p>
                </div>

                <button
                  @click="addFilter()"
                  v-if="selectedFilter.name && selectedFilter.operator && selectedFilter.value"
                  class="chat-button shimmer"
                  style="padding: 0.5rem 1rem"
                >
                  Add filter
                </button>
              </div>
            </section>
          </div>
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
      </div>
      <div class="space-between">
        <p v-if="searchText">End of list</p>
        <span v-else></span>
        <button class="chat-button" v-if="displayedOpps.next" @click="loadMoreOpps">
          Load More
        </button>
      </div>
    </div>
    <!-- <div class="opp-scroll-container" v-else>
      <div
        v-for="opp in searchOpportunities"
        class="opp-container"
        @click="changeSelectedOpp(opp)"
        :key="opp.id"
      >
        <p style="margin: 0">{{ opp.name }}</p>
      </div>
      <div v-if="displayedOpps.next" @click="loadMoreOpps">Load More</div>
    </div> -->
  </section>
</template>
  
<script>
import SlackOAuth from '@/services/slack'
import { CRMObjects, ObjectField } from '@/services/crm'
// import Opportunity from '@/services/opportunity'
import CollectionManager from '@/services/collectionManager'
import Tooltip from './Tooltip.vue'

export default {
  name: 'RightBar',
  components: {
    Tooltip,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      isPopping: false,
      filtersOpen: false,
      hoveredOpp: null,
      searchText: '',
      selectedOpp: null,
      updateOppForm: [],
      oppFields: [],
      resourceName: 'Opportunity',
      searchOpportunities: [],
      objects: CollectionManager.create({
        ModelClass: CRMObjects,
        pagination: { size: 20 },
        // filters: {
        //   crmObject: 'Opportunity',
        // },
      }),
      page: 1,
      notes: [{ id: 0, value: 'Moved close date back to end of June', date: Date.now() }],
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
      operators: [
        { label: 'is', value: 'EQUALS' },
        { label: 'is greater than', value: 'GREATER_THAN' },
        { label: 'is greater than or equal to', value: 'GREATER_THAN_EQUALS' },
        { label: 'is less than', value: 'LESS_THAN' },
        { label: 'is less than or equal to', value: 'LESS_THAN_EQUALS' },
        { label: 'contains', value: 'CONTAINS' },
        { label: 'does not equal', value: 'NOT_EQUALS' },
      ],
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
          apiName: 'Name',
          operator: null,
          value: null,
          operatorLabel: null,
        },
        {
          name: 'Stage',
          dataType: 'text',
          icon: 'fa-stairs',
          apiName: 'StageName',
          operator: null,
          value: null,
          operatorLabel: null,
        },
        {
          name: 'Close date',
          dataType: 'date',
          icon: 'fa-calendar-plus',
          apiName: 'CloseDate',
          operator: null,
          value: null,
          operatorLabel: null,
        },
        {
          name: 'Amount',
          dataType: 'number',
          icon: 'fa-sack-dollar',
          apiName: 'Amount',
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
  watch: {
    activeFilters(newValue, oldValue) {
      if (newValue !== oldValue) {
        this.isPopping = true

        setTimeout(() => {
          this.isPopping = false
        }, 1000)
      }
    },
  },
  methods: {
    test(log) {
      console.log('log', log)
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
        setTimeout(() => {
          this.toggleShowFilters()
        }, 100)
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
    // async searchOpps() {
    //   if (this.searchText) {
    //     this.searchOpportunities = await this.$store.dispatch('loadAllOpps', [['CONTAINS', 'Name', this.searchText]])
    //   }
    // },
    selectOperator(val, label) {
      this.selectedFilter.operator = val
      this.selectedFilter.operatorLabel = label
    },
    selectFilter(filter) {
      console.log('filter', filter)
      this.selectedFilter = filter
    },
    toggleShowFilters() {
      this.filtersOpen = !this.filtersOpen
      this.selectedOperator = null
      this.selectedFilter = null
    },
    openInCrm(id) {
      let url
      url =
        this.user.crm === 'SALESFORCE'
          ? `${this.user.salesforceAccountRef.instanceUrl}/lighning/r/Opportunity/${id}/view`
          : ''
      window.open(url, '_blank')
    },
    clearText() {
      this.searchText = ''
    },
    changeSelectedOpp(opp) {
      this.selectedOpp = opp
    },
    async switchFiltering() {
      // this.$store.dispatch('changeFilters', [['EQUALS', 'Name', 'Marriot']])
      // await this.$store.dispatch('loadChatOpps', this.page)
      this.filtering = !this.filtering
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
    activeFilters() {
      return this.$store.state.filters
    },
    displayedOpps() {
      return this.$store.state.chatOpps
    },
    userCRM() {
      return this.$store.state.user.crm
    },
    user() {
      return this.$store.state.user
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

@keyframes shimmer {
  100% {
    -webkit-mask-position: left;
  }
}

.shimmer {
  animation: shimmer 2s infinite;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/200% 100%;
}

.pop-transition {
  transition: transform 0.3s ease; /* Adjust the transition duration and easing as per your preference */
  transform: scale(1.25); /* Adjust the transform properties to create the desired effect */
  animation: shimmer 1s infinite;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/200% 100%;
}

::v-deep .multiselect__single {
  font-size: 14px;
}

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

.pointer {
  cursor: pointer;
}

.flexed-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  position: relative;

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

.chat-button {
  @include chat-button();
  width: 100px;
  font-size: 14px;
  font-family: $base-font-family;
  color: $chat-font-color;
  background-color: white;
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

.filter-container {
  position: absolute;
  height: auto;
  min-height: 300px;
  max-height: 500px;
  width: 350px;
  background-color: white;
  z-index: 1000;
  top: 3.5rem;
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
      margin-right: 8px;
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
</style>