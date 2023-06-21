<template>
  <section class="lists">
    <header class="list-header">
      <p><span>List: </span> {{ currentView.title }}</p>

      <button @click="toggleAddField" class="small-button">
        <img src="@/assets/images/plusOne.svg" height="12px" alt="" />

        Column
      </button>
    </header>
    <div v-show="addingField" class="add-field">
      <header>
        <p>Add Columns</p>

        <div :class="{ disabled: loading }" class="save-close">
          <div @click="addExtraFields" class="save">
            <span v-if="!loading">&#x2713;</span>
            <img
              class="rotate disabled"
              v-else
              src="@/assets/images/refresh.svg"
              height="11px"
              alt=""
            />
          </div>
          <div @click="toggleAddField" :class="{ disabled: loading }" class="close">
            <span>x</span>
          </div>
        </div>
      </header>
      <main class="centered">
        <Multiselect
          style="width: 100%"
          v-model="extraFieldObjs"
          placeholder="Select fields"
          label="referenceDisplayLabel"
          openDirection="below"
          track-by="id"
          :options="formFields"
          selectedLabel=""
          deselectLabel=""
          selectLabel=""
          :multiple="true"
        >
          <template v-slot:noResult>
            <p class="multi-slot">No results.</p>
          </template>
        </Multiselect>
      </main>
    </div>
    <section class="chat-table-section">
      <table class="table">
        <thead>
          <tr>
            <th style="padding-left: 1rem">Name</th>
            <th>Stage</th>
            <th>Close Date</th>
            <th v-for="(field, i) in extraPipelineFields" :key="i">
              {{ field.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(opp, i) in currentView.sobjectInstances" :key="i">
            <td @click="setOpp(opp.Name)">
              <span>{{ opp.Name }}</span>
            </td>
            <td>{{ opp.StageName }}</td>
            <td>
              {{ opp.CloseDate }}
            </td>

            <td v-for="(field, i) in extraPipelineFields" :key="i">
              {{ opp[field.apiName] || '---' }}
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <div class="row">
      <button class="chat-button">
        <img class="gold-filter" src="@/assets/images/sparkle.svg" height="16px" alt="" />Ask Managr
      </button>
      <button class="chat-button">
        <img class="gold-filter" src="@/assets/images/sparkle.svg" height="16px" alt="" />Run Review
      </button>
    </div>
  </section>
</template>

<script>
import { SObjects } from '@/services/salesforce'

export default {
  name: 'ChatList',
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  props: {
    formFields: {},
  },
  data() {
    return {
      message: '',
      extraFields: [],
      extraFieldObjs: [],
      addingField: false,
      loading: false,
      baseResourceType: this.userCrm === 'HUBSPOT' ? 'deal' : 'Opportunity',
    }
  },
  methods: {
    setOpp(name) {
      this.$emit('set-opp', name)
    },
    toggleAddField() {
      this.addingField = !this.addingField
    },
    async addExtraFields() {
      this.loading = true
      for (let i = 0; i < this.extraFieldObjs.length; i++) {
        this.extraFields.push(this.extraFieldObjs[i].id)
      }
      try {
        const res = await SObjects.api.addExtraFields({
          resource_type: this.baseResourceType,
          field_ids: this.extraFields,
        })
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.loading = false
        }, 1500)

        setTimeout(() => {
          this.toggleAddField()
          this.extraFields = []
          this.extraFieldObjs = []
        }, 1000)
      }
    },
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    userCrm() {
      return this.$store.state.user.crm
    },
    currentView() {
      return this.$store.state.currentView
    },
    hasExtraFields() {
      const accountRef = this.$store.state.user.salesforceAccountRef
        ? this.$store.state.user.salesforceAccountRef
        : this.$store.state.user.hubspotAccountRef
      const extraFields = accountRef.extraPipelineFieldsRef[this.baseResourceType]
      return extraFields && extraFields.length ? extraFields : []
    },
    extraPipelineFields() {
      let extras = []
      extras = this.formFields.filter((field) => this.hasExtraFields.includes(field.id))
      return extras
    },
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
  height: 175px;
}
::v-deep .multiselect__placeholder {
  color: $base-gray;
}

.chat-button {
  @include chat-button();
  padding: 0.7rem 1rem;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  margin-right: 1rem;
  img {
    margin-right: 0.5rem;
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
    margin-right: 0.25rem;
  }

  &:disabled {
    background-color: $off-white;
  }
}

.save-close {
  position: absolute;
  right: 0.75rem;

  display: flex;
  flex-direction: row;
  align-items: center;
}

.close {
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  outline: 1px solid rgba(0, 0, 0, 0.1);
  color: $coral;
  width: 20px;
  height: 20px;
  border-radius: 3px;
  cursor: pointer;
  margin-left: 0.5rem;
  margin-right: 2px;
  font-size: 13px;
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
  background: white;
  outline: 1px solid rgba(0, 0, 0, 0.1);
  color: $dark-green;
  width: 20px;
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

.disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.rotate {
  animation: rotation 3s infinite linear;
}

.sticky-header {
  position: sticky;
  top: 0;
  background-color: white;
  padding: 0.5rem 0;
  font-weight: 500;
  color: $light-gray-blue;
  font-size: 12px !important;
}

.gold-filter {
  filter: invert(89%) sepia(43%) saturate(4130%) hue-rotate(323deg) brightness(90%) contrast(87%);
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  background-color: white;
  padding: 1rem 0;
  padding-left: 1.25rem;
  margin-top: 1rem;
  width: 100%;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.lists {
  height: 100%;
  width: 100%;
  overflow-y: scroll;
  overflow-x: hidden;
  position: relative;
}

.add-field {
  position: absolute;
  top: 4.25rem;
  right: 0.75rem;
  width: 320px;
  height: 175px;
  background-color: white;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 1px 3px 7px 0 #b8bdc2;
  z-index: 100;
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0.75rem;
    font-size: 14px;
  }

  footer {
    position: inherit;
    bottom: 1rem;
    right: 1.25rem;
  }
}

.centered {
  padding: 0 0.75rem;
  margin-top: 1rem;
}

.chat-table-section {
  position: relative;
  height: 50vh;
  overflow: scroll;
  padding: 0 1rem 1rem 0;
  margin: 0 1rem;
  background-color: white;
  // border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.chat-table-section::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.chat-table-section::-webkit-scrollbar-thumb {
  background-color: transparent;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px !important;
}
.chat-table-section:hover::-webkit-scrollbar-thumb {
  background-color: $base-gray;
}

table {
  table-layout: fixed;
  border-collapse: collapse;
  font-size: 14px;
  position: absolute;
}
thead {
  position: sticky;
  background-color: white;
  color: $light-gray-blue;
  font-size: 12px !important;
  top: 0;
  z-index: 3;
}

thead tr th {
  position: relative;
}
th {
  text-align: left;
  max-width: 100px;
  -webkit-user-select: none;
  -ms-user-select: none;
  user-select: none;
}
td {
  max-width: 200px;
}
th,
td {
  padding: 1rem 1.25rem 1.25rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: normal;
}

td:first-of-type {
  position: sticky;
  left: 0;
  z-index: 2;
  background-color: white;
  cursor: pointer;
  min-width: 120px;
  span {
    background-color: $off-white;
    padding: 0.75rem 1rem;
    border-radius: 5px;
  }
}

th:first-of-type {
  left: 0;
  position: sticky;
  z-index: 4;
  background-color: white;
}

.list-header {
  position: sticky;
  background-color: white;
  top: 0;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  // border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  p {
    font-size: 12px;
    padding: 0;
    margin: 0;
    span {
      color: $light-gray-blue;
      margin-right: 0.25rem;
    }
  }
}

.gray-bg {
  background-color: $off-white;
  border-radius: 5px;
  padding: 0.5rem 1rem;
}

.ellipsis-text {
  white-space: nowrap;
  overflow: hidden;
  width: fit-content;
  max-width: 200px;
  margin-top: -0.5rem;

  p {
    text-overflow: ellipsis;
  }
}

.pointer {
  cursor: pointer;
  &:hover {
    opacity: 0.5;
  }
}
</style>