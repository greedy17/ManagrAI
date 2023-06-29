<template>
  <section class="lists">
    <header class="list-header">
      <p><span>List: </span> {{ currentView.title }}</p>

      <div style="display: flex; align-items: center">
        <button @click="reloadWorkflow" class="small-button">
          <img
            :class="{ 'rotate disabled': loading }"
            src="@/assets/images/refresh.svg"
            height="12px"
            alt=""
          />
        </button>

        <button @click="toggleAddField" class="small-button">
          <!-- <img src="@/assets/images/plusOne.svg" height="12px" alt="" /> -->
          <span>+ / -</span>

          Column
        </button>
      </div>
    </header>
    <div v-show="addingField" class="add-field">
      <header>
        <p>{{ addRemoveText }}</p>

        <div :class="{ disabled: loading }" class="save-close">
          <div v-if="addOrRemove === 'Add'" @click="addExtraFields" class="save">
            <span v-if="!loading">&#x2713;</span>
            <img
              class="rotate disabled"
              v-else
              src="@/assets/images/refresh.svg"
              height="11px"
              alt=""
            />
          </div>

          <div v-else @click="removeExtraFields" class="save">
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

      <div class="centered" v-if="!addOrRemove">
        <p style="font-size: 12px">Add or remove columns ?</p>

        <Multiselect
          style="width: 100%"
          v-model="addOrRemove"
          placeholder="add / remove"
          :options="addRemoveChoices"
          selectedLabel=""
          deselectLabel=""
          selectLabel=""
        >
        </Multiselect>
      </div>

      <main v-else class="centered">
        <Multiselect
          v-if="addOrRemove === 'Add'"
          style="width: 100%"
          v-model="extraFieldObjs"
          placeholder="Select the fields you want as columns"
          label="referenceDisplayLabel"
          openDirection="below"
          track-by="id"
          :options="
            formFields.list.filter(
              (field) => !listNames.includes(field.label) && field.crmObject === baseResourceType,
            )
          "
          selectedLabel=""
          deselectLabel=""
          selectLabel=""
          :multiple="true"
          :close-on-select="false"
        >
          <template v-slot:noResult>
            <p class="multi-slot">No results.</p>
          </template>
        </Multiselect>

        <Multiselect
          v-else
          style="width: 100%"
          v-model="removeExtraFieldObjs"
          placeholder="Select columns to remove"
          label="referenceDisplayLabel"
          openDirection="below"
          track-by="id"
          :options="extraPipelineFields"
          selectedLabel=""
          deselectLabel=""
          selectLabel=""
          :multiple="true"
          :close-on-select="false"
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

              <!-- <img class="left-margin" src="@/assets/images/trash.svg" height="10px" alt="" /> -->
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(opp, i) in currentView.sobjectInstances" :key="i">
            <td @click="setOpp(user.crm === 'HUBSPOT' ? opp.dealname : opp.Name)">
              <span>{{ user.crm === 'HUBSPOT' ? opp.dealname : opp.Name }}</span>
            </td>
            <td>
              {{
                user.crm === 'HUBSPOT'
                  ? stageField &&
                    stageField.options[0][opp.pipeline].stages.filter(
                      (stage) => stage.id === opp['dealstage'],
                    )[0].label
                  : opp.StageName
              }}
            </td>

            <td>
              {{
                user.crm === 'HUBSPOT'
                  ? formatDateTime(opp.closedate)
                  : formatDateTime(opp.CloseDate)
              }}
            </td>

            <td v-for="(field, i) in extraPipelineFields" :key="i">
              {{ fieldData(field.dataType, user.crm, field, opp) }}
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
import { CollectionManager } from '@thinknimble/tn-models'
import { ObjectField } from '@/services/crm'
import AlertTemplate from '@/services/alerts/'
import User from '@/services/users/'

export default {
  name: 'ChatList',
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },

  data() {
    return {
      message: '',
      addOrRemove: null,
      addRemoveText: 'List Columns',
      extraFields: [],
      extraFieldObjs: [],
      removeExtraFieldObjs: [],
      addRemoveChoices: ['Add', 'Remove'],
      addingField: false,
      loading: false,
      formFields: CollectionManager.create({
        ModelClass: ObjectField,
        pagination: { size: 1000 },
        filters: {
          updateable: true,
        },
      }),
    }
  },
  created() {
    this.formFields.refresh()
  },
  methods: {
    test() {
      console.log(this.user)
    },
    fieldData(type, crm, field, opp, owner = null, account = null) {
      if (field.apiName === 'OwnerId' || field.apiName === 'hubspot_owner_id') {
        return owner || '---'
      } else if (field.apiName === 'AccountId') {
        return account || '---'
      } else if (field.apiName === 'dealstage') {
        if (field.options[0][opp['secondary_data'].pipeline]) {
          return (
            field.options[0][opp['secondary_data'].pipeline].stages.filter(
              (stage) => stage.id === opp['secondary_data'][field.apiName],
            )[0].label || '---'
          )
        } else return '---'
      } else if (type === 'Date') {
        return this.fieldConditions(crm, field, opp)
          ? this.formatDate(this.fieldConditions(crm, field, opp))
          : '---'
      } else if (type === 'DateTime') {
        return this.fieldConditions(crm, field, opp)
          ? this.formatDateTime(this.fieldConditions(crm, field, opp))
          : '---'
      } else if (type === 'Currency') {
        return this.fieldConditions(crm, field, opp)
          ? this.formatCash(this.fieldConditions(crm, field, opp))
          : '---'
      } else {
        return this.fieldConditions(crm, field, opp) ? this.fieldConditions(crm, field, opp) : '---'
      }
    },
    fieldConditions(crm, field, opp) {
      return crm === 'SALESFORCE'
        ? field.apiName.includes('__c') || field.apiName.includes('__r')
          ? opp[field.apiName]
          : opp[this.capitalizeFirstLetter(this.camelize(field.apiName))]
        : opp[field.apiName]
    },
    formatDate(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return '-'
      }
      const replace = input.replace(pattern, '$2/$3/$1')
      return this.userCRM === 'HUBSPOT' ? replace.split('T')[0] : replace
    },
    formatDateTime(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return '-'
      }
      let newDate = input.replace(pattern, '$2/$3/$1')
      return newDate.split('T')[0]
    },
    async reloadWorkflow() {
      this.loading = true
      try {
        let res = await AlertTemplate.api.runAlertTemplateNow(this.currentView.id, {
          fromWorkflow: true,
        })
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.loading = false
        }, 1000)
        this.$emit('refresh-list')
      }
    },
    setOpp(name) {
      this.$emit('set-opp', name)
    },
    toggleAddField() {
      this.addingField = !this.addingField
      this.addOrRemove = null
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
        this.toggleAddField()
        this.extraFields = []
        this.extraFieldObjs = []
        this.addOrRemove = null
        setTimeout(() => {
          this.refreshUser()
          this.loading = false
        }, 1500)
      }
    },
    refreshUser() {
      User.api
        .getUser(this.user.id)
        .then((user) => {
          this.$store.dispatch('updateUser', user)
          return user
        })
        .catch(() => {
          // do nothing for now
          return null
        })
    },
    async removeExtraFields() {
      this.loading = true
      let list = this.removeExtraFieldObjs.map((field) => field.id)
      try {
        const res = await SObjects.api.removeExtraField({
          resource_type: this.baseResourceType,
          field_ids: list,
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.toggleAddField()
        this.removeExtraFieldObjs = []
        this.addOrRemove = null
        setTimeout(() => {
          this.refreshUser()
          this.loading = false
        }, 1500)
      }
    },
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    userCRM() {
      return this.$store.state.user.crm
    },
    baseResourceType() {
      return this.user.crm === 'HUBSPOT' ? 'Deal' : 'Opportunity'
    },
    currentView() {
      return this.$store.state.currentView
    },
    extraPipelineFields() {
      let extras = []
      extras = this.formFields.list.filter((field) => this.hasExtraFields.includes(field.id))
      return extras
    },
    hasExtraFields() {
      let accountRef = this.$store.state.user.salesforceAccountRef
        ? this.$store.state.user.salesforceAccountRef
        : this.$store.state.user.hubspotAccountRef
      let extraFields = accountRef.extraPipelineFieldsRef[this.baseResourceType]
      return extraFields && extraFields.length ? extraFields : []
    },
    listNames() {
      if (this.extraPipelineFields) {
        return this.extraPipelineFields.map((field) => field.label)
      } else {
        return []
      }
    },
    stageField() {
      if (this.user.crm === 'HUBSPOT') {
        return this.formFields.list.filter((field) => field.apiName === 'dealstage')[0]
      }
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
  width: 300px;
}
::v-deep .multiselect__placeholder {
  color: $base-gray;
}

::v-deep .multiselect__tag {
  background-color: $soft-gray;
  color: $base-gray;
}

.left-margin {
  margin-left: 1rem;
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

  span {
    margin-right: 0.5rem;
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
  height: 200px;
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
  max-width: 120px;
  -webkit-user-select: none;
  -ms-user-select: none;
  user-select: none;
}
td {
  max-width: 300px;
  min-width: 120px;
  max-height: 90px;
  overflow-y: scroll;
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
  min-width: 150px;

  span {
    background-color: $off-white;
    padding: 0.75rem 0.5rem 0.75rem 1rem;
    border-radius: 5px;
    max-width: 290px !important;
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