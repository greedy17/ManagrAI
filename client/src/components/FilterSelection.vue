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
            <p class="multi-slot">No results.</p>
          </template>
        </Multiselect>
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

        <Multiselect
          v-if="apiName === 'AccountId'"
          placeholder="Select Account"
          style="max-width: 20vw"
          v-model="inputValue"
          @search-change="$emit('filter-accounts', $event)"
          @select="$emit('value-selected', `${$event.id}`, apiName)"
          :options="accounts"
          openDirection="below"
          selectLabel="Enter"
          label="name"
          track-by="id"
        >
          <template slot="noResult">
            <p>No results.</p>
          </template>
        </Multiselect>
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
                ? inputValue.id
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
  methods: {
    closeFilters() {
      this.$emit('close-selection')
    },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';

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
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
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
    margin: 0;
    cursor: pointer;
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