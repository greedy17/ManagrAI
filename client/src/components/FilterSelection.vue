<template>
  <div class="filter-selection">
    <div>
      <div class="filter-selection__body">
        <Multiselect
          placeholder="Select Operator"
          style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
          v-model="selectedOperator"
          :options="operators"
          @select="$emit('operator-selected', $event.value)"
          openDirection="below"
          selectLabel="Enter"
          track-by="value"
          label="label"
        >
          <template slot="noResult">
            <p>No results.</p>
          </template>
        </Multiselect>

        <!-- <select
          @input=";(value = $event.target.value), $emit('operator-selected', `${value}`)"
          v-model="selectedOperator"
          id="operators"
        >
          <option disabled selected hidden>{{ operators[0].label }}</option>
          <option v-for="(option, i) in operators" :value="option.value" :key="i">
            <p>{{ option.label }}</p>
          </option>
        </select> -->
      </div>

      <div
        v-if="type === 'Currency' || type === 'Double' || type === 'Phone'"
        class="filter-selection__body"
      >
        <input
          @input=";(value = $event.target.value), $emit('value-selected', value)"
          v-model="inputValue"
          id="input-field-id"
          type="number"
        />
      </div>

      <!-- <div
        v-if="
          (type === 'Currency' || type === 'Double' || type === 'Phone') &&
          selectedOperator === 'range'
        "
        class="filter-selection__body"
      >
        <div class="range-row">
          <input id="input-field-id-small" type="number" />
          <p style="margin-right: 0.5rem; margin-left: 0.5rem">-</p>
          <input id="input-field-id-small" type="number" />
        </div>
      </div> -->

      <div
        v-else-if="type === 'Picklist' || type === 'MultiPicklist'"
        class="filter-selection__body"
      >
        <Multiselect
          :placeholder="'Select ' + `${filterName}`"
          style="max-width: 20vw"
          v-model="inputValue"
          :options="dropdowns[apiName]"
          @select="$emit('value-selected', $event.value)"
          openDirection="below"
          selectLabel="Enter"
          track-by="value"
          label="label"
        >
          <template slot="noResult">
            <p>No results.</p>
          </template>
        </Multiselect>

        <!-- <select
          v-model="inputValue"
          @input=";(value = $event.target.value), $emit('value-selected', `${value}`)"
          id="input-field-id"
        >
          <option v-for="(option, i) in dropdowns[apiName]" :key="i">
            <p>{{ option.label }}</p>
          </option>
        </select> -->
      </div>

      <div v-else-if="type === 'Reference'" class="filter-selection__body">
        <Multiselect
          v-if="apiName === 'OwnerId'"
          placeholder="Select Owner"
          style="max-width: 20vw"
          v-model="inputValue"
          @select="
            $emit('value-selected', `${$event.salesforce_account_ref.salesforce_id}`, apiName)
          "
          :options="owners"
          openDirection="below"
          selectLabel="Enter"
          label="full_name"
          track-by="id"
        >
          <template slot="noResult">
            <p>No results.</p>
          </template>
        </Multiselect>

        <!-- <select
          @input=";(value = $event.target.value), $emit('value-selected', `${value}`, apiName)"
          v-model="inputValue"
          v-if="apiName === 'OwnerId'"
          id="input-field-id"
        >
          <option
            v-for="(owner, i) in owners"
            :key="i"
            :value="
              owner.salesforce_account_ref ? owner.salesforce_account_ref.salesforce_id : null
            "
          >
            <p>
              {{ owner.full_name }}
            </p>
          </option>
        </select> -->
        <Multiselect
          v-if="apiName === 'AccountId'"
          placeholder="Select Account"
          style="max-width: 20vw"
          v-model="inputValue"
          @select="$emit('value-selected', `${$event.integration_id}`, apiName)"
          :options="accounts"
          openDirection="below"
          selectLabel="Enter"
          label="name"
          track-by="integration_id"
        >
          <template slot="noResult">
            <p>No results.</p>
          </template>
        </Multiselect>

        <!-- <select
          v-model="inputValue"
        
          id="input-field-id"
          @input=";(value = $event.target.value), $emit('value-selected', `${value}`, apiName)"
        >
          <option v-for="(account, i) in accounts" :key="i" :value="account.integration_id">
            <p>{{ account.name }}</p>
          </option>
        </select> -->
      </div>

      <div v-else-if="type === 'Date' || type === 'DateTime'" class="filter-selection__body">
        <input
          @input=";(value = $event.target.value), $emit('value-selected', `${value}`)"
          type="date"
          placeholder="Select date"
          id="input-field-id"
          v-model="inputValue"
        />
      </div>

      <div v-else-if="type === 'String' || type === 'TextArea'" class="filter-selection__body">
        <input
          @input=";(value = $event.target.value), $emit('value-selected', `${value}`)"
          v-model="inputValue"
          id="input-field-id"
          type="text"
        />
      </div>

      <div v-if="inputValue" class="filter-selection__footer">
        <p
          style="color: #199e54"
          @click="
            $emit(
              'filter-added',
              type === 'Currency' || type === 'Double' || type === 'Phone'
                ? parseInt(inputValue)
                : type === 'Picklist' || type === 'MultiPicklist'
                ? inputValue.value
                : apiName === 'OwnerId'
                ? inputValue.salesforce_account_ref.salesforce_id
                : apiName === 'AccountId'
                ? inputValue.integration_id
                : inputValue,
            )
          "
        >
          Add
        </p>
        <p style="color: #fa646a" @click="closeFilters">Cancel</p>
      </div>
      <div v-else class="filter-selection__footer">
        <p style="color: #fa646a" @click="closeFilters">Cancel</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FilterSelection',
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },

  data() {
    return {
      operators: [
        { label: 'equals', value: 'EQUALS' },
        { label: 'not equals', value: 'NOT_EQUALS' },
        { label: 'greater than', value: 'GREATER_THAN' },
        { label: 'greater or equal', value: 'GREATER_THAN_EQUALS' },
        { label: 'less than', value: 'LESS_THAN' },
        { label: 'less or equal', value: 'LESS_THAN_EQUALS' },
        { label: 'contains', value: 'CONTAINS' },
        // { label: 'range', value: 'RANGE' },
      ],
      selectedOperator: '',
      inputValue: null,
      counter: 0,
    }
  },
  props: {
    type: {},
    filterName: {},
    dropdowns: {},
    apiName: {},
    accounts: {},
    owners: {},
  },
  computed: {
    filteredFilters() {
      return this.oppFilters.filter((opp) =>
        opp.title.toLowerCase().includes(this.searchFilterText.toLowerCase()),
      )
    },
  },
  methods: {
    closeFilters() {
      this.$emit('close-selection')
    },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
// @import '@/styles/buttons';

#input-field-id {
  border: 1px solid #e8e8e8;
  border-radius: 0.25rem;
  min-height: 2.5rem;
  width: 20vw;
}
.range-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}
#operators {
  border: none;
  //   border-bottom: 1px solid $very-light-gray;
  border-radius: 0.25rem;
  background-color: white;
  height: 3.5rem;
  max-width: 9vw;
  overflow: scroll;
}
#operators:focus {
  outline: none;
}
::placeholder {
  color: $very-light-gray;
}
.wide {
  display: flex;
  justify-content: center;
  width: 100%;
  background-color: white;
}
.filter-selection {
  z-index: 5;
  position: absolute;
  top: 6vh;
  left: 0;
  border-radius: 0.33rem;
  background-color: $white;
  min-width: 24vw;
  padding: 1rem 1rem 0rem 1rem;
  overflow: scroll;
  box-shadow: 1px 1px 7px 2px $very-light-gray;

  &__title {
    margin: 1rem;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    position: sticky;
    top: 0;
    color: $base-gray;
  }

  &__body {
    display: flex;
    align-items: center;
    justify-content: flex-start;
  }

  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-evenly;
    margin-top: 1.5rem;
    // width: 100%;
    height: 2rem;
    border-top: 1px solid $soft-gray;
    p {
      cursor: pointer;
      font-size: 13px;
      padding-top: 0.5rem;
    }
  }
}
.filter-button {
  display: flex;
  align-items: center;
  min-height: 4.5vh;
  width: 100%;
  background-color: transparent;
  border: none;
  padding: 0.75 0rem;
  border-radius: 0.2rem;
  color: #7a7777;
  cursor: pointer;
  font-size: 14px;
}
.filter-button:hover {
  color: $base-gray;
  background-color: $off-white;

  img {
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
  }
}

.filter-search-bar {
  height: 4.5vh;
  background-color: transparent;
  border-bottom: 1px solid $very-light-gray;
  display: flex;
  align-items: center;
  padding: 2px;
  margin-right: 0.5rem;
}
</style>