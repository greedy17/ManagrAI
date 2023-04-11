<template>
  <div>
    <section class="set-height">
      <div class="top-row">
        <Multiselect
          :options="formFields.list"
          :multiple="true"
          :placeholder="
            userCRM === 'SALESFORCE' ? 'Search for your fields' : 'Search for your properties'
          "
          label="label"
          track-by="apiName"
          openDirection="below"
          selectLabel=""
          :maxHeight="350"
          :hideSelected="true"
          :loading="refreshing"
          @close="onTouch"
          :disabled="
            !hasZoomChannel ||
            !(orgHasSlackIntegration || hasSlackIntegration) ||
            !hasNylasIntegration ||
            !userCRM
          "
          @input="onAddField($event[0])"
          :class="{ invalidOutline: isInvalid }"
          style="width: 27vw"
        >
          <template v-slot:noResult>
            <p class="multi-slot">No results.</p>
          </template>
          <template v-slot:placeholder>
            <p class="slot-icon">
              {{
                userCRM === 'SALESFORCE'
                  ? 'Opportunity Fields'
                  : userCRM === 'HUBSPOT'
                  ? 'Deal properties'
                  : 'Connect CRM'
              }}
            </p>
          </template>
          <template v-slot:noOptions>
            <div class="slot-icon">
              <p>Sync in progress... Reload in a minute</p>
              <span @click="refreshFields()" class="button">Reload</span>
            </div>
          </template>
        </Multiselect>
        <button
          v-if="!savingForm"
          @click="onSave()"
          :disabled="!(addedFields.length > 2)"
          :class="{ pulse: saveNeeded && addedFields.length > 2 }"
        >
          Save
        </button>
        <PipelineLoader v-else />
      </div>
      <label v-if="addedFields.length < 3" class="small-text" for=""
        >Suggestions: "Name" , "Stage" , "Close Date" , "Next Step" , "Amount"</label
      >
    </section>
    <draggable
      v-model="addedFields"
      group="fields"
      @start="drag = true"
      @end="drag = false"
      class="drag-section"
    >
      <div v-for="field in addedFields" :key="field.id">
        <div v-if="!unshownIds.includes(field.id)">
          <div class="drag-item">
            <img src="@/assets/images/drag.svg" height="16px" alt="" />
            <p id="formField">
              {{ field.label }}
            </p>
            <label for="">|</label>
            <span
              alt=""
              id="remove"
              @click="
                () => {
                  onRemoveField(field)
                }
              "
              >x</span
            >
          </div>
        </div>
      </div>
    </draggable>

    <!-- <button :disabled="!selectedFields.length">Save</button> -->
  </div>
</template>

<script>
import { CollectionManager } from '@thinknimble/tn-models'
import draggable from 'vuedraggable'
import SlackOAuth from '@/services/slack'
import { ObjectField } from '@/services/crm'
import User from '@/services/users'

export default {
  name: 'OnboardingForms',
  components: {
    draggable,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
  },
  data() {
    return {
      formType: 'UPDATE',
      savingForm: false,
      saveNeeded: false,
      addedFields: [],
      refreshing: false,
      removedFields: [],
      selectedFields: [],
      formFields: CollectionManager.create({
        ModelClass: ObjectField,
        pagination: { size: 500 },
        filters: {
          crmObject: this.resourceType,
          updateable: true,
        },
      }),
      isTouched: false,
      noteTitle: {
        model: 'crm.ObjectField',
        id: '6407b7a1-a877-44e2-979d-1effafec5034', // '6407b7a1-a877-44e2-979d-1effafec5035'
        includeInRecap: true,
        apiName: 'meeting_type',
        createable: true,
        required: false,
        updateable: true,
        dataType: 'String',
        displayValue: '',
        label: 'Note Subject',
        reference: false,
        referenceToInfos: [],
        relationshipName: null,
        options: [],
        length: 0,
        isPublic: true,
        filterable: true,
        datetimeCreated: '2020-08-03 11:39:23.632256Z',
        lastEdited: '2020-08-03 11:39:23.632256Z',
      },
      noteTitleHubspot: {
        model: 'crm.ObjectField',
        id: '6407b7a1-a877-44e2-979d-1effafec5034', //'6407b7a1-a877-44e2-979d-1effafec5035',
        includeInRecap: true,
        apiName: 'meeting_type',
        createable: true,
        required: false,
        updateable: true,
        dataType: 'String',
        displayValue: '',
        label: 'Note Subject',
        reference: false,
        referenceToInfos: [],
        relationshipName: null,
        options: [],
        length: 0,
        isPublic: true,
        filterable: true,
        datetimeCreated: '2020-08-03 11:39:23.632256Z',
        lastEdited: '2020-08-03 11:39:23.632256Z',
      },
      noteSubject: {
        model: 'crm.ObjectField',
        id: '0bb152b5-aac1-4ee0-9c25-51ae98d55af2', // '0bb152b5-aac1-4ee0-9c25-51ae98d55af1'
        includeInRecap: true,
        apiName: 'meeting_comments',
        createable: true,
        updateable: true,
        required: false,
        dataType: 'String',
        displayValue: '',
        label: 'Notes',
        reference: false,
        referenceToInfos: [],
        relationshipName: null,
        options: [],
        length: 255,
        isPublic: true,
        filterable: true,
        datetimeCreated: '2020-08-03 11:39:23.632256Z',
        lastEdited: '2020-08-03 11:39:23.632256Z',
      },
      noteSubjectHubspot: {
        model: 'crm.ObjectField',
        id: '0bb152b5-aac1-4ee0-9c25-51ae98d55af2', //'0bb152b5-aac1-4ee0-9c25-51ae98d55af1',
        includeInRecap: true,
        apiName: 'meeting_comments',
        createable: true,
        updateable: true,
        required: false,
        dataType: 'String',
        displayValue: '',
        label: 'Notes',
        reference: false,
        referenceToInfos: [],
        relationshipName: null,
        options: [],
        length: 255,
        isPublic: true,
        filterable: true,
        datetimeCreated: '2020-08-03 11:39:23.632256Z',
        lastEdited: '2020-08-03 11:39:23.632256Z',
      },
    }
  },
  watch: {
    formFields: 'refreshFormFields',
    customForm: {
      immediate: true,
      deep: true,
      handler(val) {
        if (val && val.customFields.length) {
          this.addedFields = [...val.fieldsRef]
          if (this.formType == 'UPDATE') {
            let currentFormFields = this.addedFields.map((field) => {
              return field.id
            })
            if (
              currentFormFields.includes('6407b7a1-a877-44e2-979d-1effafec5035') == false &&
              currentFormFields.includes('6407b7a1-a877-44e2-979d-1effafec5034') == false
            ) {
              let fieldsToAdd =
                this.userCRM === 'SALESFORCE'
                  ? [this.noteTitle, this.noteSubject]
                  : [this.noteTitleHubspot, this.noteSubjectHubspot]
              let copyArray = this.addedFields
              fieldsToAdd = fieldsToAdd.concat(copyArray)
              this.addedFields = fieldsToAdd.map((field, i) => {
                let altField = { ...field }
                altField.order = i
                if (
                  altField.id == '6407b7a1-a877-44e2-979d-1effafec5034' ||
                  altField.id == '0bb152b5-aac1-4ee0-9c25-51ae98d55af1' ||
                  altField.id == '6407b7a1-a877-44e2-979d-1effafec5035' ||
                  altField.id == '0bb152b5-aac1-4ee0-9c25-51ae98d55af2'
                ) {
                  altField.includeInRecap = true
                }
                return altField
              })
            }
          }
          if (this.formType !== 'UPDATE') {
            this.addedFields = this.addedFields.filter((field) => {
              return (
                field.id !== '6407b7a1-a877-44e2-979d-1effafec5034' &&
                field.id !== '0bb152b5-aac1-4ee0-9c25-51ae98d55af1' &&
                field.id !== '6407b7a1-a877-44e2-979d-1effafec5035' &&
                field.id == '0bb152b5-aac1-4ee0-9c25-51ae98d55af2'
              )
            })
          }
        } else if (val && val.formType == 'STAGE_GATING' && !val.customFields.length) {
          this.addedFields = []
        }
      },
    },
  },
  computed: {
    currentFields() {
      return this.customForm ? this.customForm.customFields : []
    },
    isInvalid() {
      return this.isTouched && this.addedFields.length < 3
    },
    resources() {
      if (this.userCRM === 'SALESFORCE') {
        return [
          { label: 'Opportunity', value: 'OPPORTUNITY' },
          { label: 'Account', value: 'ACCOUNT' },
          { label: 'Contact', value: 'CONTACT' },
          { label: 'Lead', value: 'LEAD' },
        ]
      } else {
        return [
          { label: 'Deal', value: 'DEAL' },
          { label: 'Account', value: 'ACCOUNT' },
          { label: 'Contact', value: 'CONTACT' },
        ]
      }
    },
    filteredFields() {
      return this.formFields.list.filter((field) => !this.addedFieldNames.includes(field.apiName))
    },
    addedFieldIds() {
      return this.addedFields.map((field) => {
        return field.id
      })
    },
    addedFieldNames() {
      return this.addedFields.map((field) => {
        return field.apiName
      })
    },
    unshownIds() {
      return [
        '6407b7a1-a877-44e2-979d-1effafec5035',
        '0bb152b5-aac1-4ee0-9c25-51ae98d55af1',
        '6407b7a1-a877-44e2-979d-1effafec5034',
        '0bb152b5-aac1-4ee0-9c25-51ae98d55af2',
        'e286d1d5-5447-47e6-ad55-5f54fdd2b00d',
        'fae88a10-53cc-470e-86ec-32376c041893',
      ]
    },
    user() {
      return this.$store.state.user
    },
    userCRM() {
      return this.$store.state.user.crm
    },
    orgHasSlackIntegration() {
      return !!this.$store.state.user.organizationRef.slackIntegration
    },
    hasSlackIntegration() {
      return !!this.$store.state.user.slackRef
    },
    hasNylasIntegration() {
      return !!this.$store.state.user.nylas
    },
    userCanIntegrateSlack() {
      return this.$store.state.user.isAdmin
    },
    hasZoomChannel() {
      return this.$store.state.user.slackAccount
        ? this.$store.state.user.slackAccount.zoomChannel
        : null
    },
  },
  props: {
    customForm: {
      type: Object,
    },
    disable: {
      type: Boolean,
    },
    resourceType: {},
  },
  created() {
    this.formFields.refresh()
  },
  methods: {
    refreshFormFields() {
      this.formFields.refresh()
    },
    refreshFields() {
      this.refreshing = true
      this.formFields.refresh()
      setTimeout(() => {
        this.refreshing = false
      }, 3000)
    },
    onTouch() {
      this.isTouched = true
    },
    selectingFields(val) {
      this.$emit('selecting', val)
    },
    customLabel(prop) {
      const label = prop.customObject ? `${prop.customObject}` : `${prop.label}`
      return label.replace('&amp;', '&')
    },
    removeAmp(label) {
      return label.replace('&amp;', '&')
    },
    searchFields() {
      this.formFields = CollectionManager.create({
        ModelClass: ObjectField,
        pagination: { size: 500 },
        filters: {
          crmObject: this.resourceType,
          search: this.filterText,
          updateable: true,
        },
      })
    },
    async refreshForms() {
      this.pulseLoading = true
      const res = await SlackOAuth.api.refreshForms()
      setTimeout(() => {
        this.pulseLoading = false
        this.$router.go()
      }, 300)
    },

    canRemoveField(field) {
      // If form is create required fields cannot be removed
      // if form is update required fields can be removed
      // if form is meeting review depening on the resource it can/cant be removed
      if (
        this.MEETING_REVIEW_REQUIRED_FIELDS[this.resource] &&
        ~this.MEETING_REVIEW_REQUIRED_FIELDS[this.resource].findIndex((f) => field.id == f)
      ) {
        return false
      } else {
        return true
      }
    },
    onAddField(field) {
      this.saveNeeded = true
      if (this.addedFieldIds.includes(field.id)) {
        this.canRemoveField(field) && this.onRemoveField(field)
        return
      }
      this.addedFields.push({ ...field, order: this.addedFields.length, includeInRecap: true })
    },
    onRemoveField(field) {
      this.saveNeeded = true
      // remove from the array if  it exists

      this.addedFields = [...this.addedFields.filter((f) => f.id != field.id)]
      // if it exists in the current fields add it to remove field
      if (~this.currentFields.findIndex((f) => f == field.id)) {
        this.removedFields = [...this.removedFields, field]
      }
    },
    async onSave() {
      this.savingForm = true

      let currentFormFields = this.addedFields.map((field) => {
        return field.id
      })

      if (
        currentFormFields.includes('6407b7a1-a877-44e2-979d-1effafec5035') == false &&
        currentFormFields.includes('6407b7a1-a877-44e2-979d-1effafec5034') == false
      ) {
        let fieldsToAdd =
          this.userCRM === 'SALESFORCE'
            ? [this.noteTitle, this.noteSubject]
            : [this.noteTitleHubspot, this.noteSubjectHubspot]
        let copyArray = this.addedFields
        this.addedFields = fieldsToAdd.concat(copyArray)
      }

      let fields = new Set([...this.addedFields.map((f) => f.id)])
      fields = Array.from(fields).filter((f) => !this.removedFields.map((f) => f.id).includes(f))
      let fieldsCheck = []
      fields.forEach((field) => {
        if (
          field === '6407b7a1-a877-44e2-979d-1effafec5034' ||
          field === '6407b7a1-a877-44e2-979d-1effafec5035' ||
          field === '0bb152b5-aac1-4ee0-9c25-51ae98d55af2' ||
          field === '0bb152b5-aac1-4ee0-9c25-51ae98d55af1'
        ) {
          return
        }
        fieldsCheck.push(field)
      })

      let fields_ref = this.addedFields.filter((f) => fields.includes(f.id))

      SlackOAuth.api
        .postOrgCustomForm({
          ...this.customForm,
          fields: fields,
          removedFields: this.removedFields,
          fields_ref: fields_ref,
          custom_object: '',
        })
        .then((res) => {
          // this.$emit('update:selectedForm', res)
          User.api.getUser(this.user.id).then((response) => {
            this.$store.commit('UPDATE_USER', response)
          })

          // this.customForm = res

          this.$toast('Fields saved!', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.removedFields = []
          this.addedFields = fields_ref
        })
        .finally(() => {
          this.savingForm = false
          this.saveNeeded = false
          this.formChange = false
          this.$emit('refresh-forms', this.customForm)
          this.formFields.refresh()
        })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 $dark-green;
  }

  70% {
    transform: scale(1);
    box-shadow: 0 0 0 10px rgba(0, 0, 0, 0);
  }

  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(0, 0, 0, 0);
  }
}
.pulse {
  box-shadow: 0 0 0 0 $dark-green;
  transform: scale(1);
  animation: pulse 1.25s infinite;
}

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}

@keyframes shake-animation {
  0% {
    transform: translate(0, 0);
  }
  1.78571% {
    transform: translate(5px, 0);
  }
  3.57143% {
    transform: translate(0, 0);
  }
  5.35714% {
    transform: translate(5px, 0);
  }
  7.14286% {
    transform: translate(0, 0);
  }
  8.92857% {
    transform: translate(5px, 0);
  }
  10.71429% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(0, 0);
  }
}

input[type='checkbox']:checked + label::after {
  content: '';
  position: absolute;
  width: 1ex;
  height: 0.3ex;
  background: rgba(0, 0, 0, 0);
  top: 0.9ex;
  left: 0.4ex;
  border: 2px solid $dark-green;
  border-top: none;
  border-right: none;
  -webkit-transform: rotate(-45deg);
  -moz-transform: rotate(-45deg);
  -o-transform: rotate(-45deg);
  -ms-transform: rotate(-45deg);
  transform: rotate(-45deg);
}

input[type='checkbox'] {
  line-height: 2.1ex;
}

input[type='checkbox'] {
  position: absolute;
  left: -999em;
}

input[type='checkbox'] + label {
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

input[type='checkbox'] + label::before {
  content: '';
  display: inline-block;
  vertical-align: -22%;
  height: 1.75ex;
  width: 1.75ex;
  background-color: white;
  border: 1px solid rgb(182, 180, 180);
  border-radius: 4px;
  margin-right: 0.5em;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.set-height {
  min-height: 10vh;
  //   width: 98%;
  //   display: flex;
  //   flex-direction: column;
  //   flex-wrap: wrap;
  //   overflow-x: scroll;
  //   gap: 12px;
}
.no-margin {
  margin: 0;
}

.fit-content::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.fit-content::-webkit-scrollbar-thumb {
  background-color: $very-light-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 0.3rem;
}
.fit-content::-webkit-scrollbar-track {
  box-shadow: inset 2px 2px 4px 0 $soft-gray;
  border-radius: 0.3rem;
}
.fit-content::-webkit-scrollbar-track-piece {
}
.margin-bottom {
  margin-bottom: 1rem;
}
p {
  margin: 4px;
}
.slot-icon {
  display: flex;
  flex-direction: row !important;
  align-items: center;
  justify-content: space-between;
  padding: 0;
  margin: 0;
  img {
    height: 1rem;
    margin-right: 0.25rem;
    filter: invert(70%);
  }
}
.small-text {
  color: $light-gray-blue;
  font-size: 12px;
  margin: 8px 4px;
}
.invalid {
  color: $coral;
  font-size: 13px;
}
.invalidOutline {
  outline: 1px solid $coral;
  border-radius: 4px;
  animation: shake-animation 4.72s ease infinite;
  transform-origin: 50% 50%;
}
.top-row {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}
.invisible {
  display: none;
}
button {
  background-color: $dark-green;
  padding: 11px;
  font-size: 13px;
  border-radius: 4px;
  // outline: 1px solid $dark-green;
  border: none;
  color: white;
  margin-left: 12px;
  margin-top: 2px;
  cursor: pointer;
  transition: all 0.25s;
}
button:hover {
  box-shadow: 0 6px 6px rgba(0, 0, 0, 0.1);
  transform: scale(1.025);
}
button:disabled {
  background-color: $soft-gray;
  color: $light-gray-blue;
  outline: none;
}
.drag-section {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: flex-start;
  padding: 2px;
  max-width: 56vw;
  overflow-x: auto;
}
.drag-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin-right: 8px;
  margin-bottom: 8px;
  border-radius: 4px;
  background-color: $white;
  color: $base-gray;
  outline: 1px solid $soft-gray;
  font-size: 13px;
  width: fit-content;
  white-space: nowrap;
  img {
    filter: invert(10%);
    cursor: grab;
  }
  label {
    color: $very-light-gray !important;
    padding-left: 2px;
  }
  span {
    color: $base-gray;
    font-size: 11px;
    padding: 6px 8px 8px 8px;
    border-radius: 4px;
  }
  span:hover {
    background-color: rgba(0, 0, 0, 0.6);
    cursor: pointer;
    color: $white;
  }
}

.drag-section::-webkit-scrollbar {
  width: 0px;
  height: 8px;
}
.drag-section::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  border-radius: 0.3rem;
}
.drag-section::-webkit-scrollbar-track {
  box-shadow: inset 4px 4px 8px 0 $off-white;
  background: $soft-gray;
  border-radius: 0.2rem;
}
.button {
  display: block;
  padding: 4px 6px;
  background-color: $grape;
  color: white;
  width: fit-content;
  border-radius: 3px;
  // margin-top: 8px;
}
</style>