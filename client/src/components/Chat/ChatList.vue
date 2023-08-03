<template>
  <section class="lists">
    <Modal
      @close-modal="
        () => {
          $emit('cancel'), toggleEditAlert()
        }
      "
      v-if="editingAlert"
      dimmed
    >
      <div class="edit-modal">
        <header>
          <p>{{ currentView.title }}</p>

          <p v-if="!loading" style="cursor: pointer" @click="toggleEditAlert">x</p>
          <img
            class="rotate disabled"
            v-else
            src="@/assets/images/refresh.svg"
            height="11px"
            alt=""
          />
        </header>

        <main>
          <AlertsEditPanel :alert="currentView" />
        </main>
      </div>
    </Modal>

    <header class="list-header">
      <!-- <p @click="test()"><span>List: </span> {{ currentView.title }}</p> -->
      <div class="row__">
        <div class="flexed-start" v-if="templates.refreshing">
          <div class="loading">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
        </div>

        <div class="" v-else>
          <div class="row__" v-if="templates.list.length">
            <Multiselect
              style="width: 200px"
              v-model="activeList"
              :placeholder="currentView ? currentView.title : 'Select list'"
              :options="templates.list"
              selectedLabel=""
              deselectLabel=""
              selectLabel=""
              track-by="id"
              label="title"
              @select="selectList($event)"
              :loading="templates.refreshing"
            >
            </Multiselect>
            <p class="counter" v-if="currentView !== 'pipeline' && !templates.refreshing">
              Results: {{ currentView ? currentView.sobjectInstances.length : '' }}
            </p>
          </div>
          <div v-else>
            <div
              v-if="userCRM && !(displayedOpps.results && displayedOpps.results.length)"
              class="create-list-button create-disabled"
            >
              Create List
            </div>
            <div v-else class="create-list-button" @click="openChangeConfig('workflows')">
              Create List
            </div>
          </div>
        </div>
        <!-- <select
          v-else
          @input="selectList($event.target.selectedOptions[0]._value)"
          class="dropdown__content"
          name="listOptions"
          id=""
        >
          <option disabled selected value="">Select list</option>
          <option class="select-items" v-for="(list, i) in templates.list" :key="i" :value="list">
            {{ list.title }}
          </option>
        </select> -->
      </div>

      <div style="display: flex; align-items: center">
        <button @click="toggleEditAlert" class="small-button">
          <img src="@/assets/images/edit.svg" height="12px" alt="" />
        </button>
        <button @click="handleConfigureOpen" class="small-button">
          <img src="@/assets/images/plusOne.svg" height="12px" alt="" />
        </button>
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

    <!-- <div v-show="editingAlert" class="add-field">
      <header>
        <p>{{ currentView.title }}</p>

        <p v-if="!loading" style="cursor: pointer" @click="toggleEditAlert">x</p>
        <img
          class="rotate disabled"
          v-else
          src="@/assets/images/refresh.svg"
          height="11px"
          alt=""
        />
      </header>

      <main class="centered">
        <AlertsEditPanel :alert="currentView" />
      </main>

      <footer class="list-footer" :class="{ disabled: loading }">
        <button @click="toggleEditAlert">Close</button>

        <button :disabled="loading">Save</button>
      </footer>
    </div> -->

    <div v-show="addingField" class="add-field">
      <header>
        <p>{{ addRemoveText }}</p>

        <p v-if="!loading" style="cursor: pointer" @click="toggleAddField">x</p>
        <img
          class="rotate disabled"
          v-else
          src="@/assets/images/refresh.svg"
          height="11px"
          alt=""
        />
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
          placeholder="Select fields"
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
      <footer v-if="addOrRemove" class="list-footer" :class="{ disabled: loading }">
        <button @click="toggleAddField">Close</button>

        <button :disabled="loading" @click="addExtraFields" v-if="addOrRemove === 'Add'">
          Save
        </button>

        <button :disabled="loading" @click="removeExtraFields" v-else>Save</button>
      </footer>
    </div>
    <section v-if="!formFields.refreshing" class="chat-table-section">
      <table class="table">
        <thead>
          <tr>
            <th
              style="padding-left: 1rem"
              @click="reversed ? sortOpps(
                'String',
                userCRM === 'SALESFORCE' ? 'Name' : 'dealname',
                userCRM === 'SALESFORCE' ? 'name' : 'dealname',
              ) 
              : 
              sortOppsReverse(
                'String',
                userCRM === 'SALESFORCE' ? 'Name' : 'dealname',
                userCRM === 'SALESFORCE' ? 'name' : 'dealname',
              )"
              class="pipeline-header"
            >
              Name {{ selectedFilter === 'Name' }}
              <span v-if="selectedFilter === 'Name' || selectedFilter === 'dealname'" class="filter-arrow-container">
                <img v-if="reversed" src="@/assets/images/arrowDrop.svg"  class="filter-arrow"/>
                <img v-else src="@/assets/images/arrowDropUp.svg"  class="filter-arrow"/>
              </span>
            </th>
            <th
              @click="reversed ? sortOpps(
                'String',
                userCRM === 'SALESFORCE' ? 'Stage' : 'dealstage',
                userCRM === 'SALESFORCE' ? 'stage' : 'dealstage',
              ) 
              : 
              sortOppsReverse(
                'String',
                userCRM === 'SALESFORCE' ? 'Stage' : 'dealstage',
                userCRM === 'SALESFORCE' ? 'stage' : 'dealstage',
              )"
              class="pipeline-header"
            >
              Stage
              <span v-if="selectedFilter === 'Stage' || selectedFilter === 'dealstage'" class="filter-arrow-container">
                <img v-if="reversed" src="@/assets/images/arrowDrop.svg"  class="filter-arrow"/>
                <img v-else src="@/assets/images/arrowDropUp.svg"  class="filter-arrow"/>
              </span>
            </th>
            <th
              @click="reversed ? sortOpps(
                'String',
                userCRM === 'SALESFORCE' ? 'CloseDate' : 'closedate',
                userCRM === 'SALESFORCE' ? 'closedate' : 'closedate',
              ) 
              : 
              sortOppsReverse(
                'String',
                userCRM === 'SALESFORCE' ? 'CloseDate' : 'closedate',
                userCRM === 'SALESFORCE' ? 'closedate' : 'closedate',
              )"
              class="pipeline-header"
            >
              Close Date
              <span v-if="selectedFilter === 'CloseDate' || selectedFilter === 'closedate'" class="filter-arrow-container">
                <img v-if="reversed" src="@/assets/images/arrowDrop.svg"  class="filter-arrow"/>
                <img v-else src="@/assets/images/arrowDropUp.svg"  class="filter-arrow"/>
              </span>
            </th>
            <th 
              v-for="(field, i) in extraPipelineFields" 
              :key="i" 
              @click="reversed ? sortOpps(field.dataType, field.label, field.apiName) : sortOppsReverse(field.dataType, field.label, field.apiName)"
              class="pipeline-header"
            >
              {{ field.label }}
              <span v-if="selectedFilter === field.label" class="filter-arrow-container">
                <img v-if="reversed" src="@/assets/images/arrowDrop.svg"  class="filter-arrow"/>
                <img v-else src="@/assets/images/arrowDropUp.svg"  class="filter-arrow"/>
              </span>
            </th>
          </tr>
        </thead>
        <tbody v-if="currentView">
          <tr v-for="(opp, i) in currentView.sobjectInstances" :key="i">
            <td
              :title="user.crm === 'HUBSPOT' ? opp.dealname : opp.Name"
              @click="setOpp(user.crm === 'HUBSPOT' ? opp.dealname : opp.Name)"
            >
              <span>{{ user.crm === 'HUBSPOT' ? opp.dealname : opp.Name }}</span>
            </td>
            <td
              :title="
                user.crm === 'HUBSPOT'
                  ? stageField &&
                    stageField.options[0][opp.pipeline].stages.filter(
                      (stage) => stage.id === opp['dealstage'],
                    )[0].label
                  : opp.StageName
              "
            >
              {{
                user.crm === 'HUBSPOT'
                  ? stageField &&
                    stageField.options[0][opp.pipeline].stages.filter(
                      (stage) => stage.id === opp['dealstage'],
                    )[0].label
                  : opp.StageName
              }}
            </td>

            <td
              :title="
                user.crm === 'HUBSPOT'
                  ? formatDateTime(opp.closedate)
                  : formatDateTime(opp.CloseDate)
              "
            >
              {{
                user.crm === 'HUBSPOT'
                  ? formatDateTime(opp.closedate)
                  : formatDateTime(opp.CloseDate)
              }}
            </td>

            <td
              :title="fieldData(field.dataType, user.crm, field, opp)"
              v-for="(field, i) in extraPipelineFields"
              :key="i"
            >
              {{ fieldData(field.dataType, user.crm, field, opp) }}
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <div v-else class="loading">
      <div class="dot"></div>
      <div class="dot"></div>
      <div class="dot"></div>
    </div>

    <div class="row">
      <!-- <button class="chat-button">
        <img class="gold-filter" src="@/assets/images/sparkle.svg" height="16px" alt="" />Ask Managr
      </button>
      <button class="chat-button">
        <img class="gold-filter" src="@/assets/images/sparkle.svg" height="16px" alt="" />Run Review
      </button> -->
    </div>
  </section>
</template>

<script>
import { SObjects } from '@/services/salesforce'
import { CollectionManager } from '@thinknimble/tn-models'
import AlertsEditPanel from '@/views/settings/alerts/view/_AlertsEditPanel'
import { ObjectField } from '@/services/crm'
import AlertTemplate from '@/services/alerts/'
import User from '@/services/users/'
import Modal from '@/components/InviteModal'
import { decryptData } from '../../encryption'

export default {
  name: 'ChatList',
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    AlertsEditPanel,
    Modal,
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
      editingAlert: false,
      loading: false,
      activeList: null,
      reversed: true,
      selectedFilter: '',
      storedFilters: [],
      listCount: 0,
      formFields: CollectionManager.create({
        ModelClass: ObjectField,
        pagination: { size: 1000 },
        filters: {
          updateable: true,
        },
      }),
      templates: CollectionManager.create({
        ModelClass: AlertTemplate,
        filters: { forPipeline: true },
      }),
    }
  },
  created() {
    this.formFields.refresh()
    this.templates.refresh()
  },
  mounted() {
    this.setList()
  },
  methods: {
    test() {
      console.log(this.templates.list)
    },
    setList() {
      setTimeout(() => {
        if (this.templates.list) {
          this.activeList = this.templates.list[0]
          this.selectList(this.templates.list[0])
        }
      }, 2000)
    },
    handleConfigureOpen() {
      this.$emit('handleConfigureOpen', 'workflows')
    },
    openChangeConfig(page) {
      this.$emit('open-change-config', page)
    },
    selectList(alert) {
      this.selectedFilter = ''
      this.$store.dispatch('setCurrentView', alert)
    },
    capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1)
    },
    camelize(str) {
      return str.replace(/(?:^\w|[A-Z]|\b\w|\s+)/g, function (match, index) {
        if (+match === 0) return ''
        return index === 0 ? match.toLowerCase() : match.toUpperCase()
      })
    },
    sortOpps(dT, field, apiName) {
      let newField
      if (this.userCRM === 'SALESFORCE') {
        newField = this.capitalizeFirstLetter(this.camelize(field))
      } else {
        newField = field
      }
      const userCRM = this.userCRM
      let sortedWorkflow
      if (this.currentView && this.currentView.sobjectInstances.length) {
        this.selectedFilter = field
        console.log('this.selectedFilter', this.selectedFilter)
        if (field === 'Stage' || field === 'Deal Stage') {
          sortedWorkflow = this.currentView.sobjectInstances.sort(function (a, b) {
            const nameA =
              userCRM === 'SALESFORCE'
                ? a['StageName']
                : a['dealstage']
            const nameB =
              userCRM === 'SALESFORCE'
                ? b['StageName']
                : b['dealstage']
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else if (field === 'Last Activity') {
          sortedWorkflow = this.currentView.sobjectInstances.sort(function (a, b) {
            const nameA = a[`${newField}` + 'Date']
            const nameB = b[`${newField}` + 'Date']
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else if (dT === 'TextArea' && !apiName.includes('__c')) {
          sortedWorkflow = this.currentView.sobjectInstances.sort(function (a, b) {
            const nameA = a[`${newField}`]
            const nameB = b[`${newField}`]
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else if (apiName.includes('__c') && dT !== 'TextArea') {
          sortedWorkflow = this.currentView.sobjectInstances.sort(function (a, b) {
            const nameA = a[`${apiName}`]
            const nameB = b[`${apiName}`]
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else if (apiName.includes('__c') && dT === 'TextArea') {
          sortedWorkflow = this.currentView.sobjectInstances.sort(function (a, b) {
            const nameA = a[`${apiName}`]
            const nameB = b[`${apiName}`]
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else if (this.userCRM === 'HUBSPOT') {
          this.currentView.sobjectInstances.sort(function (a, b) {
            const nameA = a[`${apiName}`]
            const nameB = b[`${apiName}`]
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else {
          sortedWorkflow = this.currentView.sobjectInstances.sort(function (a, b) {
            const nameA = a[`${newField}`]
            const nameB = b[`${newField}`]
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        }
        this.activeList.sobjectInstances = sortedWorkflow
        this.$store.dispatch('setCurrentView', this.activeList)
      }

      let custom = false
      this.reversed = false
      this.storedFilters = [dT, field, apiName, { reversed: false }, custom]
    },
    sortOppsReverse(dT, field, apiName) {
      let newField
      if (this.userCRM === 'SALESFORCE') {
        newField = this.capitalizeFirstLetter(this.camelize(field))
      } else {
        newField = field
      }

      const userCRM = this.userCRM
      let sortedWorkflow
      if (this.currentView && this.currentView.sobjectInstances.length) {
        this.selectedFilter = field
        if (field === 'Stage' || field === 'Deal Stage') {
          sortedWorkflow = this.currentView.sobjectInstances.sort(function (a, b) {
            const nameA =
              userCRM === 'SALESFORCE'
                ? a['StageName']
                : a['dealstage']
            const nameB =
              userCRM === 'SALESFORCE'
                ? b['StageName']
                : b['dealstage']
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else if (field === 'Last Activity') {
          sortedWorkflow = this.currentView.sobjectInstances.sort(function (a, b) {
            const nameA = a[`${newField}` + 'Date']
            const nameB = b[`${newField}` + 'Date']
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else if (dT === 'TextArea' && !apiName.includes('__c')) {
          sortedWorkflow = this.currentView.sobjectInstances.sort(function (a, b) {
            const nameA = a[`${newField}`]
            const nameB = b[`${newField}`]
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else if (apiName.includes('__c') && dT !== 'TextArea') {
          sortedWorkflow = this.currentView.sobjectInstances.sort(function (a, b) {
            const nameA = a[`${apiName}`]
            const nameB = b[`${apiName}`]
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else if (apiName.includes('__c') && dT === 'TextArea') {
          sortedWorkflow = this.currentView.sobjectInstances.sort(function (a, b) {
            const nameA = a[`${apiName}`]
            const nameB = b[`${apiName}`]
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else if (this.userCRM === 'HUBSPOT') {
          this.currentView.sobjectInstances.sort(function (a, b) {
            const nameA = a[`${apiName}`]
            const nameB = b[`${apiName}`]
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else {
          sortedWorkflow = this.currentView.sobjectInstances.sort(function (a, b) {
            const nameA = a[`${newField}`]
            const nameB = b[`${newField}`]
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        }
        this.activeList.sobjectInstances = sortedWorkflow
        this.$store.dispatch('setCurrentView', this.activeList)
      } 

      let custom = false
      this.reversed = true
      this.storedFilters = [dT, field, apiName, { reversed: true }, custom]
    },
    fieldData(type, crm, field, opp, owner = null, account = null) {
      if (field.apiName === 'OwnerId' || field.apiName === 'hubspot_owner_id') {
        return owner || '---'
      } else if (field.apiName === 'AccountId') {
        return account || '---'
      } else if (field.apiName === 'dealstage') {
        if (field.options[0][opp.pipeline]) {
          return (
            field.options[0][opp.pipeline].stages.filter(
              (stage) => stage.id === opp[field.apiName],
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
    capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1)
    },
    camelize(str) {
      return str.replace(/(?:^\w|[A-Z]|\b\w|\s+)/g, function (match, index) {
        if (+match === 0) return ''
        return index === 0 ? match.toLowerCase() : match.toUpperCase()
      })
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
    formatCash(money) {
      let cash = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
      })
      if (money) {
        return cash.format(money)
      }
      return '-'
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
    toggleEditAlert() {
      this.editingAlert = !this.editingAlert
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
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user
    },
    userCRM() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.crm
    },
    displayedOpps: {
      get() {
        return this.$store.state.chatOpps
      },

      set(value) {
        this.displayedOpps = value
      },
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
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      // let accountRef = decryptedUser.salesforceAccountRef
      //   ? decryptedUser.salesforceAccountRef
      //   : decryptedUser.hubspotAccountRef
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

::v-deep .multiselect__single {
  white-space: nowrap;
}

::v-deep .multiselect__tag {
  background-color: $soft-gray;
  color: $base-gray;
  // height: 32px;
}

::v-deep .multiselect__tags {
  // height: 32px;
}

.edit-modal {
  display: flex;
  flex-direction: column;
  width: 520px;
  height: 610px;
  padding: 0 0.5rem 0 1rem;
  background-color: white;
  border-radius: 6px;
  overflow-y: scroll;
  overflow-x: hidden;

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0.75rem;
    font-size: 16px;
  }
}

.dropdown__content {
  border: none;
  -moz-appearance: none;
  -webkit-appearance: none;
  appearance: none;
  background: white
    url("data:image/svg+xml;utf8,<svg viewBox='0 0 140 140' width='10' height='12' xmlns='http://www.w3.org/2000/svg'><g><path stroke-width='5' d='m121.3,34.6c-1.6-1.6-4.2-1.6-5.8,0l-51,51.1-51.1-51.1c-1.6-1.6-4.2-1.6-5.8,0-1.6,1.6-1.6,4.2 0,5.8l53.9,53.9c0.8,0.8 1.8,1.2 2.9,1.2 1,0 2.1-0.4 2.9-1.2l53.9-53.9c1.7-1.6 1.7-4.2 0.1-5.8z' stroke='black' fill='black'/></g></svg>")
    no-repeat;
  background-position: right 5px top 50%;
  font-family: 'Lato', sans-serif;
  height: 29px;
  font-size: 12px;
  font-family: $base-font-family;
  color: $chat-font-color;
  letter-spacing: 0.4px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  padding: 0.35rem 1.2rem 0.35rem 0.5rem;
  cursor: pointer;
  outline: none;
  margin: 0;
}

.counter {
  margin-left: 1rem !important;
  background-color: $white-green;
  color: $dark-green;
  padding: 0.125rem 0.5rem !important;
  border-radius: 4px;

  p {
    font-size: 12px;
    width: fit-content;
  }
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 6px;
  padding: 0.75rem 0.75rem;
}

.dot {
  width: 4px;
  height: 4px;
  margin: 0 5px;
  background: rgb(97, 96, 96);
  border-radius: 50%;
  animation: bounce 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: -0.4s;
}

.dot:nth-child(3) {
  animation-delay: -0.2s;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
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

.list-footer {
  display: flex;
  flex-direction: row;
  align-items: center;
  position: relative;
  bottom: 0;
  padding: 0;
  margin-right: -6px;

  button {
    @include chat-button();
    padding: 0.35rem 0.5rem;
    font-size: 12px;
  }

  button:first-of-type {
    margin-right: 0.5rem;
  }
  button:last-of-type {
    background-color: $dark-green;
    color: white;
    border: none;
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
    // margin-right: 0.25rem;
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

.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  background-color: white;
  padding: 1rem 0;
  padding-left: 1.25rem;
  width: 100%;
  // border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.lists {
  height: 100%;
  width: 100%;
  overflow-y: scroll;
  overflow-x: hidden;
  position: relative;
  // background: $soft-gray;
}

.add-field {
  position: absolute;
  top: 4.25rem;
  right: 0.75rem;
  width: 320px;
  min-height: 200px;
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
    display: flex;
    justify-content: flex-end;
    margin: 0.5rem 1rem 0.5rem 0;
    // position: inherit;
    // bottom: 1rem;
    // right: 1.25rem;
  }
}

.centered {
  padding: 0 0.75rem;
  margin-top: 1rem;
}

.chat-table-section {
  position: relative;
  // border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  height: 96vh;
  overflow: scroll;
  margin: 0 0.25rem 0 0.5rem;
  padding: 0 0 2px 0 !important;
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
  min-width: 100%;
}
tr {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

thead {
  position: sticky;
  color: $base-gray;
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
  border: none !important;
  background: $off-white !important;
}
td {
  max-width: 300px;
  min-width: 120px;
  max-height: 90px;
  overflow-y: scroll;
  background-color: white;
}
th,
td {
  // position: relative;
  padding: 1rem 1.25rem 1rem 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: normal;
  // border-left: 1px solid rgba(0, 0, 0, 0.1);
  // border-right: 1px solid rgba(0, 0, 0, 0.1);
}

td:first-of-type {
  position: sticky;
  left: 0;
  z-index: 2;
  background-color: white;
  cursor: pointer;
  min-width: 150px;

  // color: $dark-gray-blue;

  span {
    background-color: $off-white;
    padding: 0.5rem 0.5rem 0.5rem 0.5rem !important;
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
  z-index: 5;
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
.create-list-button {
  // @include gray-text-button();
  @include primary-button();
}
.create-disabled {
  @include base-button();
  border: 1px solid $soft-gray;
  font-size: 12px;
  transition: all 0.3s;
  box-shadow: none;
  border: none;
  scale: 1;
  background-color: $soft-gray;
  color: $gray;
}
.create-disabled:hover {
  box-shadow: none;
  scale: 1;
}
.filter-arrow-container {
  // display: flex;
  // flex-direction: column;
  // justify-content: flex-end;
  // padding-top: 1.5rem;
  position: relative;
  top: 5px;
}
.filter-arrow {
  height: 14px;
  width: 16px;
  // padding-top: 0.5rem;
}
.pipeline-header {
  cursor: pointer;
}
.pipeline-header:hover {
  background-color: $soft-gray !important;
}
</style>