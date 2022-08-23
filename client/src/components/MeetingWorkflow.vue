<template>
  <div class="card">
    <!-- :class="{ 'left-green': meetingUpdated, 'left-red': !meetingUpdated }" -->

    <div>
      <p style="letter-spacing: 0.25px; font-size: 12px; margin-bottom: 3px">
        {{ meeting.topic ? meeting.topic : 'Meeting' }}
      </p>
      <span style="color: #9b9b9b; font-size: 11px">
        {{ meeting.start_time ? formatDateTimeToTime(meeting.start_time) : '' }}
      </span>
    </div>

    <div class="card__attendees">
      <p>{{ meeting.participants.length }} Attendees</p>
    </div>

    <div class="card__scroll">
      <div
        v-for="(participant, participantIndex) in participants"
        :key="participantIndex"
        class="column"
      >
        <div v-if="!meeting.participants[participantIndex].id" class="roww">
          <p class="add-contact">
            {{ meeting.participants[participantIndex].email }}
          </p>
          <span
            v-if="!meetingUpdated && !meeting.participants[participantIndex].__has_changes"
            class="tooltip"
          >
            <img
              @click="addContact(participantIndex)"
              class="contact-img green"
              src="@/assets/images/add-contact.svg"
              alt=""
            />
            <span class="tooltiptext">Add Contact</span>
          </span>
          <span
            v-if="!meetingUpdated && !meeting.participants[participantIndex].__has_changes"
            class="tooltip"
          >
            <img
              src="@/assets/images/remove.svg"
              class="contact-img red"
              @click="removeParticipant(participantIndex)"
              alt=""
            />
            <span class="tooltiptext">Remove</span>
          </span>
          <span v-if="meeting.participants[participantIndex].__has_changes">
            <img class="filter" src="@/assets/images/profile.svg" alt="" />
          </span>
        </div>

        <div v-else class="roww">
          <p class="add-contact">
            {{ meeting.participants[participantIndex].email }}
          </p>
          <img
            style="height: 0.75rem; margin-left: 0.25rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div>

        <div
          v-if="addingContact && selectedIndex === participantIndex"
          class="contact-field-section"
        >
          <div class="contact-field-section__title">
            <p>
              Add <span>"{{ meeting.participants[participantIndex].email }}"</span> to your Contacts
            </p>
            <img
              src="@/assets/images/close.svg"
              style="height: 1rem; cursor: pointer; margin-right: 0.75rem; margin-top: -0.5rem"
              @click="addingContact = !addingContact"
            />
          </div>

          <div v-if="hasLastName" class="contact-field-section__body">
            <div v-for="(field, i) in contactFields" :key="i">
              <div
                v-if="
                  field.dataType === 'Reference' &&
                  (field.apiName === 'AccountId' || field.apiName === 'OwnerId')
                "
              >
                <p>{{ field.referenceDisplayLabel }}:</p>
                <Multiselect
                  v-if="field.apiName === 'AccountId'"
                  placeholder="Select Account"
                  @search-change="$emit('filter-accounts', $event)"
                  @select="setUpdateValues(field.apiName, $event.id)"
                  v-model="selectedAccount"
                  style="width: 14vw"
                  :options="accounts"
                  openDirection="below"
                  selectLabel="Enter"
                  label="name"
                  track-by="id"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                </Multiselect>

                <Multiselect
                  v-if="field.apiName === 'OwnerId'"
                  placeholder="Select Owner"
                  style="width: 14vw"
                  v-model="selectedOwner"
                  @select="
                    setUpdateValues(field.apiName, $event.salesforce_account_ref.salesforce_id)
                  "
                  :options="owners"
                  openDirection="below"
                  selectLabel="Enter"
                  label="full_name"
                  track-by="id"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                </Multiselect>
              </div>

              <div
                v-else-if="
                  field.dataType === 'Picklist' ||
                  field.dataType === 'MultiPicklist' ||
                  (field.dataType === 'Reference' && field.apiName !== 'AccountId')
                "
              >
                <p>{{ field.dataType }}:</p>
                <Multiselect
                  v-model="dropdownVal[field.apiName]"
                  :options="
                    field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                      ? allPicklistOptions[field.id]
                      : referenceOpts[field.apiName]
                  "
                  @select="
                    setUpdateValues(
                      field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                      field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                        ? $event.value
                        : $event.id,
                      field.dataType === 'MultiPicklist' ? true : false,
                    )
                  "
                  @search-change="
                    field.dataType === 'Reference'
                      ? getReferenceFieldList(field.apiName, field.id, 'update', $event)
                      : null
                  "
                  :loading="dropdownLoading"
                  openDirection="below"
                  style="width: 14vw"
                  selectLabel="Enter"
                  :multiple="field.dataType === 'MultiPicklist' ? true : false"
                  :track-by="
                    field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                      ? 'value'
                      : 'id'
                  "
                  :label="
                    field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                      ? 'label'
                      : 'name'
                  "
                >
                  <template v-slot:noResult>
                    <p class="multi-slot">No results. Try loading more</p>
                  </template>
                  <template v-slot:placeholder>
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      {{ field.referenceDisplayLabel }}
                    </p>
                  </template>
                </Multiselect>
              </div>

              <div
                v-else-if="
                  field.dataType === 'TextArea' ||
                  (field.length > 250 && field.dataType === 'String')
                "
              >
                <p>{{ field.referenceDisplayLabel }}:</p>
                <textarea
                  @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                  ccols="30"
                  rows="4"
                  style="width: 26.25vw; border-radius: 0.4rem; padding: 7px"
                >
                </textarea>

                <p style="display: none">
                  {{
                    meeting.participants[participantIndex].secondary_data[field.apiName] ===
                      'null' ||
                    meeting.participants[participantIndex].secondary_data[field.apiName] ===
                      'undefined'
                      ? null
                      : setUpdateValues(
                          field.apiName,
                          meeting.participants[participantIndex].secondary_data[field.apiName],
                        )
                  }}
                </p>
              </div>
              <div
                v-else-if="
                  field.dataType === 'String' ||
                  field.dataType === 'Email' ||
                  field.dataType === 'Date' ||
                  field.dataType === 'DateTime'
                "
              >
                <p>{{ field.referenceDisplayLabel }}:</p>
                <input
                  @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                  type="text"
                  :placeholder="
                    `${meeting.participants[participantIndex].secondary_data[field.apiName]}` ===
                      'null' ||
                    `${meeting.participants[participantIndex].secondary_data[field.apiName]}` ===
                      'undefined'
                      ? `Enter ${field.referenceDisplayLabel}`
                      : `${meeting.participants[participantIndex].secondary_data[field.apiName]}`
                  "
                />

                <p style="display: none">
                  {{
                    meeting.participants[participantIndex].secondary_data[field.apiName] ===
                      'null' ||
                    meeting.participants[participantIndex].secondary_data[field.apiName] ===
                      'undefined'
                      ? null
                      : setUpdateValues(
                          field.apiName,
                          meeting.participants[participantIndex].secondary_data[field.apiName],
                        )
                  }}
                </p>
              </div>

              <div
                v-else-if="
                  field.dataType === 'Phone' ||
                  field.dataType === 'Double' ||
                  field.dataType === 'Currency'
                "
              >
                <p>{{ field.referenceDisplayLabel }}:</p>
                <input
                  type="number"
                  @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                  :placeholder="
                    `${meeting.participants[participantIndex].secondary_data[field.apiName]}` ===
                      'null' ||
                    `${meeting.participants[participantIndex].secondary_data[field.apiName]}` ===
                      'undefined'
                      ? `Enter ${field.referenceDisplayLabel}`
                      : `${meeting.participants[participantIndex].secondary_data[field.apiName]}`
                  "
                />

                <p style="display: none">
                  {{
                    meeting.participants[participantIndex].secondary_data[field.apiName] ===
                      'null' ||
                    meeting.participants[participantIndex].secondary_data[field.apiName] ===
                      'undefined'
                      ? null
                      : setUpdateValues(
                          field.apiName,
                          meeting.participants[participantIndex].secondary_data[field.apiName],
                        )
                  }}
                </p>
              </div>
            </div>
          </div>
          <div style="margin-left: 1rem; padding: 1rem" class="contact-field-section__body" v-else>
            Add "Last Name" to your<router-link class="link" :to="{ name: 'CreateContacts' }"
              >contact form</router-link
            >in order to add Contacts.
          </div>

          <div class="contact-field-section__footer">
            <p
              v-if="hasLastName"
              @click="
                ;(addingContact = !addingContact),
                  $emit(
                    'add-participant',
                    workflowId,
                    meeting.participants[participantIndex]._tracking_id,
                    formData,
                  )
              "
              style="color: #199e54"
            >
              Add
            </p>
            <p v-else style="color: #aaaaaa">Add</p>
            <p @click="addingContact = !addingContact" style="color: #fa646a">Cancel</p>
          </div>
        </div>

        <div
          v-if="removingParticipant && selectedIndex === participantIndex"
          class="participant-field-section"
        >
          <div class="participant-field-section__title">
            <p>
              Remove <span>"{{ meeting.participants[participantIndex].email }}"</span>
            </p>
            <img
              src="@/assets/images/close.svg"
              style="height: 1rem; cursor: pointer; margin-right: 0.75rem; margin-top: -0.5rem"
              @click="removingParticipant = !removingParticipant"
            />
          </div>

          <div class="participant-field-section__body">
            <p>Are you sure ?</p>
          </div>

          <div class="participant-field-section__footer">
            <p
              @click="
                ;(removingParticipant = !removingParticipant),
                  $emit(
                    'remove-participant',
                    workflowId,
                    meeting.participants[participantIndex]._tracking_id,
                  )
              "
            >
              Yes
            </p>
            <p @click="removingParticipant = !removingParticipant" style="color: #fa646a">No</p>
          </div>
        </div>
      </div>
    </div>

    <div class="table-cell">
      <div class="roww" v-if="resourceId && !meetingUpdated">
        <p>{{ resourceRef.name ? resourceRef.name : resourceRef.email }}</p>

        <div class="tooltip">
          <button class="name-cell-edit-note-button-1" @click="switchResource">
            <img style="filter: invert(10%); height: 0.6rem" src="@/assets/images/replace.svg" />
          </button>
          <span class="tooltiptext">Change {{ resourceType }}</span>
        </div>

        <div class="tooltip">
          <button class="name-cell-edit-note-button-1" @click="emitGetNotes(resourceId)">
            <img src="@/assets/images/white-note.svg" class="invert" height="12px" alt="" />
          </button>
          <span class="tooltiptext">View Notes</span>
        </div>
      </div>
      <p
        style="color: #9b9b9b; font-size: 11px; margin-top: -6px"
        v-if="resourceId && !meetingUpdated"
      >
        Record Type: {{ resourceType }}
      </p>
      <div v-else-if="meetingUpdated">
        <p>{{ resourceRef.name ? resourceRef.name : resourceRef.email }}</p>
        <p style="color: #9b9b9b; font-size: 11px; margin-top: -6px">
          Record Type: {{ resourceType }}
        </p>
      </div>

      <button @click="addingOpp = !addingOpp" v-else class="add-button">Link to CRM Record</button>

      <div v-if="addingOpp" class="add-field-section">
        <div class="add-field-section__title">
          <p v-if="!resourceType || !mapType">Select Record</p>
          <p
            v-else-if="resourceType && resourceId"
            style="cursor: pointer"
            @click="changeMapType(null)"
          >
            Select {{ !mapType ? 'Record' : resourceType && mapType ? mapType : resourceType }}
            <img src="@/assets/images/swap.svg" height="14px" alt="" />
          </p>
          <p v-else style="cursor: pointer" @click="changeMapType(null)">
            Select {{ mapType ? mapType : 'Record' }}
            <img src="@/assets/images/swap.svg" height="14px" alt="" />
          </p>

          <img
            src="@/assets/images/close.svg"
            style="height: 1rem; cursor: pointer; margin-right: 0.75rem; margin-top: -0.5rem"
            @click="addingOpp = !addingOpp"
          />
        </div>

        <div class="add-field-section__body">
          <Multiselect
            v-if="selectingResource || !mapType"
            style="width: 20vw"
            v-model="selectedResourceType"
            @select="changeResource($event)"
            placeholder="Select Record Type"
            selectLabel="Enter"
            openDirection="below"
            :options="resources"
          >
            <template slot="noResult">
              <p class="multi-slot">No results.</p>
            </template>
          </Multiselect>
          <!-- @search-change="mapType === 'Account' ? getAccounts($event) : null" -->
          <Multiselect
            v-else
            style="width: 20vw"
            v-model="mappedOpp"
            @select="selectOpp($event)"
            @search-change="getFilteredList($event)"
            :placeholder="`Select ${mapType}`"
            selectLabel="Enter"
            label="name"
            :customLabel="({ name, email }) => (name ? name : email)"
            openDirection="below"
            track-by="id"
            :options="allOpps"
            :loading="dropdownLoading || loadingAccounts"
          >
            <template slot="noResult">
              <p class="multi-slot">No results.</p>
            </template>
          </Multiselect>
        </div>

        <div v-if="mappedOpp" class="add-field-section__footer">
          <p @click="mapOpp">Link</p>
        </div>
        <div v-else style="cursor: text" class="add-field-section__footer">
          <p style="color: gray; cursor: text">Link</p>
        </div>
      </div>
    </div>

    <div v-if="!meetingUpdated" class="table-cell">
      <p v-if="!resourceId && !meetingLoading" class="red-text">Link meeting to take action.</p>
      <div>
        <div class="column" v-if="resourceId && !meetingLoading">
          <button
            @click="
              $emit(
                'update-Opportunity',
                resourceType,
                workflowId,
                resourceId,
                resourceRef ? resourceRef.integration_id : null,
                resourceRef ? resourceRef.secondary_data.Pricebook2Id : null,
              )
            "
            class="add-button"
          >
            Update {{ resourceType }}
          </button>
          <button @click="noUpdate = !noUpdate" class="no-update">No update needed</button>
        </div>
        <div v-if="noUpdate" class="noupdate-field-section">
          <div class="noupdate-field-section__title">
            <p>No Update Needed</p>
            <img
              src="@/assets/images/close.svg"
              style="height: 1rem; cursor: pointer; margin-right: 0.75rem; margin-top: -0.5rem"
              @click="noUpdate = !noUpdate"
            />
          </div>

          <div class="noupdate-field-section__body">Are you sure ?</div>

          <div class="noupdate-field-section__footer">
            <p @click="onNoUpdate">Yes</p>
            <p @click="noUpdate = !noUpdate" style="color: #fa646a">No</p>
          </div>
        </div>
      </div>
      <div v-if="meetingLoading">
        <div>
          <PipelineLoader />
        </div>
      </div>
    </div>
    <div v-else class="table-cell">
      <p class="success">Meeting Logged</p>
    </div>
  </div>
</template>
<script>
import { SObjects } from '@/services/salesforce'

export default {
  name: 'MeetingWorkflow',
  data() {
    return {
      fields: ['topic', 'participants_count', 'participants.email'],
      resources: ['Opportunity', 'Account', 'Contact', 'Lead'],
      dropdownVal: {},
      selectedResourceType: null,
      selectingResource: false,
      loadingAccounts: false,
      addingOpp: false,
      noUpdate: false,
      mappedOpp: null,
      resource: null,
      loading: false,
      mapType: this.resourceType,
      removingParticipant: null,
      selectedIndex: null,
      addingContact: false,
      selectedAccount: null,
      selectedOwner: null,
      formData: {},
      currentVals: [],
      allOpps: null,
    }
  },
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
    Modal: () => import(/* webpackPrefetch: true */ '@/components/Modal'),
  },
  props: {
    meeting: {},
    resourceRef: {},
    resourceId: {},
    resourceType: {},
    index: {},
    workflowId: {},
    meetingUpdated: {},
    meetingLoading: {},
    dropdowns: {},
    contactFields: {},
    accounts: {},
    owners: {},
    index: {},
    participants: {},
    allPicklistOptions: {},
    referenceOpts: {},
    dropdownLoading: {},
    accountSobjectId: {},
  },
  computed: {
    hasLastName() {
      let lastName = null
      lastName = this.contactFields.filter((field) => field.apiName === 'LastName')
      lastName.length ? (lastName = lastName[0].apiName) : (lastName = null)
      return lastName
    },
  },
  // watch: {
  //   resourceType: 'getObjects',
  // },
  // mounted() {
  //   if (this.resourceId) {
  //     this.getCurrentVals()
  //   }
  // },
  created() {
    this.getObjects()
  },
  methods: {
    async getAccounts(val) {
      this.loadingAccounts = true
      try {
        const res = await SObjects.api.getSobjectPicklistValues({
          sobject_id: this.accountSobjectId,
          value: val,
          for_meetings: true,
        })
        this.allOpps = res
      } catch (e) {
        this.$toast('Error gathering Accounts!', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.loadingAccounts = false
      }
    },
    changeMapType(i) {
      this.mapType = i
    },
    selectResource() {
      this.selectingResource = true
    },
    switchResource() {
      this.getObjects()
      this.addingOpp = !this.addingOpp
    },
    async getFilteredList(name) {
      this.loadingAccounts = true
      try {
        const res = await SObjects.api.getObjects(this.mapType, 1, true, [
          ['CONTAINS', 'Name', name],
        ])
        this.allOpps = res.results
      } catch (e) {
        console.log(e)
      } finally {
        this.loadingAccounts = false
      }
    },
    async getObjects() {
      this.loading = true
      try {
        const res = await SObjects.api.getObjectsForWorkflows(this.mapType)
        this.allOpps = res.results
        this.originalList = res.results
      } catch (e) {
        console.log(e)
      } finally {
        this.loading = false
      }
    },
    changeResource(i) {
      this.$emit('change-resource', i)
      this.mapType = i
      this.mappedOpp = null
      this.selectedResourceType = null
      this.selectingResource = false
      this.getObjects()
    },
    emitGetNotes(id) {
      this.$emit('get-notes', id)
    },
    async getCurrentVals() {
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Contact',
          formType: 'CREATE',
          resourceId: this.resourceId,
        })
      } catch (e) {
        console.log(e)
      }
    },
    setUpdateValues(key, val) {
      if (val) {
        this.formData[key] = val
      }
    },
    addContact(index) {
      this.addingContact = !this.addingContact
      this.selectedIndex = index
    },
    onNoUpdate() {
      this.noUpdate = !this.noUpdate
      this.$emit('no-update', this.workflowId, this.resourceId)
    },
    removeParticipant(index) {
      this.removingParticipant = !this.removingParticipant
      this.selectedIndex = index
    },
    selectOpp(val) {
      console.log(val)
      this.resource = val.id
      // this.$emit('change-resource', this.resourceType)
      this.mappedOpp = null
      this.selectedResourceType = null
    },
    mapOpp() {
      this.$emit('map-opp', this.workflowId, this.resource, this.mapType)
      this.addingOpp = !this.addingOpp
    },
    formatUnix(unix) {
      let date = new Date(unix * 1000)
      let hours = date.getHours()
      let minutes = '0' + date.getMinutes()
      let formattedTime = hours + ':' + minutes.substr(-2)
      return formattedTime
    },
    formatDateTimeToTime(input) {
      let preDate = new Date(input)
      let newTime = preDate.toLocaleTimeString('en-US')
      let amPm = newTime.split(' ')[1]
      let hour = newTime.split(':')[0]
      let noSeconds = newTime.replace(':', ' ')
      let noAmPm = newTime.replace(amPm, '')
      let noAmPmSeconds = noAmPm.replace(':', ' ')

      if (parseInt(hour) < 10) {
        newTime = '0' + newTime
        noAmPm = '0' + noAmPm
        noSeconds = '0' + noSeconds
        noAmPmSeconds = '0' + noAmPmSeconds
      }
      noSeconds = noSeconds.replace(' ', ':')
      noSeconds = noSeconds.split(':')
      noSeconds = noSeconds[0] + ':' + noSeconds[1] + amPm
      return noSeconds
    },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

@keyframes tooltips-horz {
  to {
    opacity: 0.95;
    transform: translate(0%, 50%);
  }
}
.card {
  width: 100%;
  outline: 1px solid $soft-gray;
  height: 100%;
  margin-top: 16px;
  min-height: 70vh;
  border-radius: 4px;
  background-color: white;
  box-shadow: 1px 1px 2px 1px $very-light-gray;

  &__attendees {
    background-color: $soft-gray;
    color: $light-gray-blue;
    border-radius: 4px;
    width: 100%;
  }

  &__scroll {
    width: 100%;
  }
}

.slot-icon {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0;
  margin: 0;
  img {
    height: 1rem;
    margin-right: 0.25rem;
    filter: invert(70%);
  }
}
.tooltip {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 2px 0px;
}
.tooltip .tooltiptext {
  visibility: hidden;
  background-color: $base-gray;
  color: white;
  text-align: center;
  border: 1px solid $soft-gray;
  letter-spacing: 0.5px;
  padding: 4px 0px;
  border-radius: 6px;
  font-size: 12px;

  /* Position the tooltip text */
  position: absolute;
  z-index: 1;
  width: 100px;
  top: 100%;
  left: 50%;
  margin-left: -50px;

  /* Fade in tooltip */
  opacity: 0;
  transition: opacity 0.3s;
}
.tooltip:hover .tooltiptext {
  visibility: visible;
  animation: tooltips-horz 300ms ease-out forwards;
}

input:focus {
  outline: none;
  cursor: text;
}
input {
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  background-color: white;
  min-height: 2.5rem;
  width: 14vw;
}
.link {
  border-bottom: 2px solid $dark-green;
  padding-bottom: 2px;
  padding: 2px 0px 2px 0px;
  margin-left: -0.1rem;
}
a {
  text-decoration: none;
  padding: 0;
  margin: 0;
  color: $dark-green;
  font-weight: bold;
}
.invert {
  filter: invert(30%);
  cursor: pointer;
}
.inverted {
}
.add-button {
  border: none;
  max-height: 4.5vh;
  min-height: 2rem;
  padding: 0.5rem 1.25rem;
  margin-right: 1rem;
  border-radius: 0.2rem;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
  font-size: 12px;
}
.no-update {
  background-color: $base-gray;
  color: white;
  border: none;
  border-radius: 0.2rem;
  max-height: 4.5vh;
  min-height: 2rem;
  padding: 0.5rem 1.25rem;
  cursor: pointer;
  font-size: 12px;
}
.roww {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}
.contact-img {
  height: 1.25rem;
  margin-right: 0.2rem;
  margin-left: 0.1rem;
  padding: 0.25rem;
  border-radius: 0.25rem;
  border: 0.8px solid $gray;
}
.green {
  margin-left: 0.2rem;
}
.green:hover {
  filter: invert(39%) sepia(96%) saturate(373%) hue-rotate(94deg) brightness(104%) contrast(94%);
  cursor: pointer;
}
.filter {
  filter: invert(39%) sepia(96%) saturate(373%) hue-rotate(94deg) brightness(104%) contrast(94%);
  height: 1rem;
  cursor: text;
  margin-left: 0.25rem;
}
.success {
  color: $dark-green;
  background-color: $white-green;
  padding: 5px;
  border-radius: 6px;
  max-width: 140px;
  display: flex;
  align-items: center;
}
.red-text {
  color: $coral;
  background-color: $light-coral;
  padding: 4px;
  border-radius: 4px;
  max-width: 180px;
  display: flex;
  align-items: center;
}
.red:hover {
  img {
    filter: invert(46%) sepia(37%) saturate(832%) hue-rotate(308deg) brightness(104%) contrast(104%);
  }
  cursor: pointer;
}
.name-cell-edit-note-button-1 {
  height: 1.1rem;
  width: 1.1rem;
  margin: 0 0.2rem;
  padding: 0.25rem;
  border-radius: 4px;
  background-color: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0.7px solid $gray;
  cursor: pointer;
}
.add-contact {
  img {
    height: 0.6rem;
  }
  cursor: text;
}
.contact-field-section {
  position: absolute;
  z-index: 7;
  right: 0;
  top: 0;
  border-radius: 8px;
  background-color: $white;
  width: 46vw;
  overflow: scroll;
  box-shadow: 1px 1px 2px 1px $very-light-gray;
  &__title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    color: $base-gray;
    background-color: $off-white;
    letter-spacing: 0.4px;
    font-weight: bold;
    font-size: 14px;
    width: 100%;
  }
  &__body {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    margin: 0.5rem;
    gap: 0.5rem;
    flex-direction: row;
    flex-wrap: wrap;
    overflow: scroll;
  }
  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-around;
    margin-top: 0.5rem;
    padding: 0.75rem 0.5rem;
    width: 100%;
    height: 2rem;
    border-top: 1px solid $soft-gray;
    p {
      cursor: pointer;
      font-weight: bold;
      font-size: 14px;
      color: $dark-green;
    }
  }
}
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 12px;
  width: 100%;
  padding: 0.5rem 0rem;
  margin: 0;
  cursor: text;
  &__more {
    background-color: white;
    color: $dark-green;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border-top: 1px solid #e8e8e8;
    width: 100%;
    padding: 0.75rem 0rem;
    margin: 0;
    cursor: pointer;

    img {
      height: 12px;
      margin-left: 0.25rem;
      filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
        brightness(93%) contrast(89%);
    }
  }
}
.noupdate-field-section {
  position: absolute;
  z-index: 7;
  left: 1.5rem;
  top: 10vh;
  border-radius: 8px;
  background-color: $white;
  min-width: 20vw;
  overflow: scroll;
  box-shadow: 1px 1px 2px 1px $very-light-gray;
  &__title {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem;
    align-items: center;
    color: $base-gray;
    background-color: $off-white;
    letter-spacing: 0.4px;
    font-weight: bold;
    font-size: 14px;
    width: 100%;
  }
  &__body {
    height: 2rem;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-around;
    margin-top: 1rem;
    padding: 0rem 0.5rem;
    width: 100%;
    min-height: 6vh;
    border-top: 1px solid $soft-gray;
    p {
      cursor: pointer;
      font-weight: bold;
      font-size: 14px;
      color: $dark-green;
    }
  }
}
.participant-field-section {
  position: absolute;
  z-index: 7;
  right: 0.5rem;
  border-radius: 8px;
  background-color: $white;
  min-width: 20vw;
  overflow: scroll;
  box-shadow: 1px 1px 2px 1px $very-light-gray;
  &__title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    color: $base-gray;
    background-color: $off-white;
    letter-spacing: 0.4px;
    font-weight: bold;
    font-size: 14px;
    width: 100%;
  }
  &__body {
    height: 2rem;
    display: flex;
    justify-content: center;
  }
  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-around;
    margin-top: 1rem;
    padding: 0rem 0.5rem;
    width: 100%;
    min-height: 6vh;
    border-top: 1px solid $soft-gray;
    p {
      cursor: pointer;
      font-weight: bold;
      font-size: 14px;
      color: $dark-green;
    }
  }
}
.add-field-section {
  position: absolute;
  z-index: 7;
  top: 10vh;
  right: 0.5rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: $white;
  min-width: 28vw;
  height: auto;
  overflow: scroll;
  box-shadow: 1px 1px 2px 1px $very-light-gray;
  &__title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    color: $base-gray;
    background-color: $off-white;
    letter-spacing: 0.4px;
    padding-left: 1rem;
    font-weight: bold;
    font-size: 16px;
    width: 100%;
  }
  &__body {
    min-height: 8rem;
    padding-left: 1rem;
    margin-top: 1rem;
  }
  &__footer {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 1rem;
    width: 100%;
    min-height: 2rem;
    border-top: 1px solid $soft-gray;
    p {
      cursor: pointer;
      color: $dark-green;
      font-weight: bold;
    }
  }
}
.table-cell-name {
  display: table-cell;
  position: relative;
  min-width: 18vw;
  max-width: 24vw;
  background-color: white;
  padding: 2vh 3vh;
  border: none;
  z-index: 2;
  left: 0;
  position: sticky;
  border-bottom: 2px solid $soft-gray;
  font-size: 13px;
}
.table-row {
  display: table-row;
  left: 0;
}
.table-cell-small {
  display: table-cell;
  position: relative;
  min-width: 3vw;
  background-color: $off-white;
  padding: 2vh;
  border: none;
  border-bottom: 3px solid $soft-gray;
  font-size: 13px;
}
.table-cell {
  display: table-cell;
  position: relative;
  min-width: 12vw;
  background-color: $off-white;
  padding: 2vh;
  border: none;
  border-bottom: 3px solid $soft-gray;
  font-size: 13px;
}
.left-green {
  border-left: 2px solid $dark-green !important;
}
.left-red {
  border-left: 2px solid $coral !important;
}
.wt-bg {
  background-color: white;
}

.sticky-header {
  left: 0;
  top: 0;
  position: sticky;
}

.table-cell:hover,
.table-cell-small:hover {
  cursor: text;
  background-color: white;
}
</style> 
