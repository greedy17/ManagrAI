<template>
  <div class="cards">
    <section class="cards__header">
      <img src="@/assets/images/meeting.svg" height="16px" alt="" />
      <div style="margin-left: 18px" class="cards__header__div">
        <h4>
          {{ meeting.topic ? meeting.topic : 'Meeting' }}
        </h4>
        <p style="font-size: 11px">
          {{ meeting.start_time ? formatDateTimeToTime(meeting.start_time) : '' }}
          <span>{{
            meeting.end_time ? '- ' + formatDateTimeToTime(meeting.end_time) : '- TBD'
          }}</span>
        </p>
      </div>
    </section>

    <section class="cards__header">
      <img src="@/assets/images/people.svg" height="16px" alt="" />
      <div
        v-if="!showingAttendees"
        @click="showAttendees"
        class="cards__header__div cards__attendees"
      >
        <p>View Meeting Attendees: {{ meeting.participants.length }}</p>
      </div>
      <div v-else class="attendees">
        <div
          class="attendees__div"
          v-for="(participant, participantIndex) in participants"
          :key="participantIndex"
        >
          <div class="roww" v-if="!meeting.participants[participantIndex].id">
            <p>
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
              class="right-tooltip"
            >
              <img
                src="@/assets/images/remove.svg"
                class="contact-img red"
                @click="removeParticipant(participantIndex)"
                alt=""
              />
              <span class="right-tooltiptext">Remove</span>
            </span>
            <span v-if="meeting.participants[participantIndex].__has_changes">
              <img class="filter" src="@/assets/images/profile.svg" alt="" />
            </span>
          </div>

          <div v-else class="roww">
            <p>
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
                Add <span>"{{ meeting.participants[participantIndex].email }}"</span> to your
                Contacts
              </p>
              <img
                src="@/assets/images/close.svg"
                style="height: 18px; cursor: pointer; margin-right: 0.75rem; margin-top: -0.5rem"
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
                    style="width: 26vw"
                    :options="accounts"
                    openDirection="below"
                    selectLabel="Enter"
                    label="name"
                    track-by="id"
                  >
                    <template slot="noResult">
                      <small class="multi-slot">No results.</small>
                    </template>
                  </Multiselect>

                  <Multiselect
                    v-if="field.apiName === 'OwnerId'"
                    placeholder="Select Owner"
                    style="width: 26vw"
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
                      <small class="multi-slot">No results.</small>
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
                  <p>{{ field.referenceDisplayLabel }}:</p>
                  <Multiselect
                    v-model="dropdownVal[field.apiName]"
                    :options="
                      field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                        ? allPicklistOptions[field.id]
                        : referenceOpts[field.apiName]
                    "
                    @select="
                      setUpdateValues(
                        field.apiName === 'ForecastCategory'
                          ? 'ForecastCategoryName'
                          : field.apiName,
                        $event.id ? $event.id : $event.value,
                      )
                    "
                    @search-change="
                      field.dataType === 'Reference'
                        ? getReferenceFieldList(field.apiName, field.id, 'update', $event)
                        : null
                    "
                    :loading="dropdownLoading"
                    openDirection="below"
                    style="width: 26vw"
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
                      <small class="multi-slot">No results. Try loading more</small>
                    </template>
                    <template v-slot:placeholder>
                      <small class="slot-icon">
                        <img src="@/assets/images/search.svg" alt="" />
                        {{
                          `${
                            meeting.participants[participantIndex].secondary_data[field.apiName]
                          }` === 'null' ||
                          `${
                            meeting.participants[participantIndex].secondary_data[field.apiName]
                          }` === 'undefined'
                            ? `${field.referenceDisplayLabel}`
                            : `${
                                meeting.participants[participantIndex].secondary_data[field.apiName]
                              }`
                        }}
                      </small>
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
                    style="width: 26vw; border-radius: 0.4rem; padding: 7px"
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
            <div
              style="margin-left: 1rem; padding: 1rem"
              class="contact-field-section__body"
              v-else
            >
              Add "Last Name" to your<router-link class="link" :to="{ name: 'CreateContacts' }"
                >contact form</router-link
              >in order to add Contacts.
            </div>

            <div class="contact-field-section__footer">
              <button
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
                class="add-button"
              >
                Add
              </button>
              <!-- <p v-else style="color: #aaaaaa">Add</p> -->
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
      <img
        v-if="showingAttendees"
        @click="showAttendees"
        src="@/assets/images/left.svg"
        height="11px"
        alt=""
        style="margin-left: 8px; cursor: pointer"
      />
    </section>

    <div class="cards__header">
      <img src="@/assets/images/link.svg" height="15px" alt="" />
      <section class="cards__header__section" v-if="resourceId && !meetingUpdated">
        <div class="cards__header__div removeSpace">
          <p class="header-text">{{ resourceRef.name ? resourceRef.name : resourceRef.email }}</p>
          <p style="font-size: 11px">{{ resourceType }}</p>
        </div>

        <div class="cards__header__div row">
          <button class="img-button" @click="switchResource">
            <img src="@/assets/images/replace.svg" height="16px" />
          </button>

          <!-- <div class="tooltip">
            <button class="img-button" @click="emitGetNotes(resourceId)">
              <img src="@/assets/images/note.svg" height="16px" alt="" />
            </button>
            <span class="tooltiptext">View Notes</span>
          </div> -->
        </div>
      </section>

      <div class="cards__header__div" v-else-if="meetingUpdated">
        <p class="header-text">{{ resourceRef.name ? resourceRef.name : resourceRef.email }}</p>
        <p>
          {{ resourceType }}
        </p>
      </div>

      <div class="cards__header__div" v-else>
        <button @click="addingOpp = !addingOpp" class="white-button">Link to CRM Record</button>
      </div>

      <div v-if="addingOpp" class="add-field-section">
        <div class="add-field-section__title">
          <h4 v-if="!resourceType || !mapType">Select Record</h4>
          <h4
            v-else-if="resourceType && resourceId"
            style="cursor: pointer; color: #4d4e4c; font-size: 14px"
            @click="changeMapType(null)"
          >
            Select
            {{ !mapType ? 'Record' : resourceType && mapType ? mapType : resourceType }}
            <img src="@/assets/images/swap.svg" height="14px" alt="" />
          </h4>
          <h4
            v-else
            style="cursor: pointer; color: #4d4e4c; font-size: 14px"
            @click="changeMapType(null)"
          >
            Select {{ mapType ? mapType : 'Record' }}
            <img src="@/assets/images/swap.svg" height="14px" alt="" />
          </h4>

          <img
            src="@/assets/images/close.svg"
            style="height: 1rem; cursor: pointer; margin-right: 0.75rem; margin-top: -0.5rem"
            @click="addingOpp = !addingOpp"
          />
        </div>

        <div class="add-field-section__body">
          <Multiselect
            v-if="selectingResource || !mapType"
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

        <div class="add-field-section__footer">
          <button :disabled="!mappedOpp" @click="mapOpp" class="add-button">Link to Record</button>
        </div>
      </div>
    </div>

    <div class="cards__header bottom" v-if="!meetingUpdated">
      <img src="@/assets/images/cloud-upload.svg" height="16px" alt="" />

      <div class="cards__header__div">
        <p v-if="!resourceId && !meetingLoading" class="red-text">
          Link meeting to a record in order to update.
        </p>
      </div>

      <div class="cards__header__div row" v-if="resourceId && !meetingLoading">
        <button
          style="margin-left: -16px"
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
          class="white-button"
        >
          Update
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

      <div v-if="meetingLoading">
        <div>
          <PipelineLoader />
        </div>
      </div>
    </div>
    <div class="cards__header bottom" v-else>
      <img class="filtered-green" src="@/assets/images/badge-check.svg" height="18px" alt="" />
      <div class="cards__header__div">
        <p style="color: #41b883">Meeting Logged</p>
      </div>
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
      showingAttendees: false,
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
    showAttendees() {
      this.showingAttendees = !this.showingAttendees
    },
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
          ['CONTAINS', this.mapType === 'Contact' ? 'Email' : 'Name', name],
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

::v-deep .multiselect__content-wrapper {
  // margin-top: 49vh;
}

@keyframes tooltips-horz {
  to {
    opacity: 0.95;
    transform: translate(0%, 50%);
  }
}
.cards {
  width: 100%;
  height: 100%;
  margin-top: 16px;
  // min-height: 70vh;
  border-radius: 4px;
  background-color: white;
  padding: 0px 16px;
  overflow: auto;
  margin-top: auto;
  // box-shadow: 1px 1px 2px 1px $very-light-gray;

  &__attendees {
    width: fit-content !important;
    background-color: $off-white;
    letter-spacing: 0.75px;
    border-radius: 6px;
    width: 100%;
    padding: 6px 10px 6px 6px;
    p {
      color: $base-gray !important;
      cursor: pointer;
    }
    span {
      color: $light-gray-blue;
    }
  }

  &__scroll {
    width: 100%;
    display: none;
  }

  &__header {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    margin-bottom: 16px;
    width: 100%;
    &__div {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: center;
      margin-left: 16px;
      letter-spacing: 0.75px;
      h4 {
        font-weight: 400 !important;
        font-size: 16px;
        margin: 0;
        padding: 0;
      }

      p {
        font-weight: bold;
        font-size: 14px;
        color: $light-gray-blue;
        padding: 0;
        margin: 0;
        margin-top: 2px;
      }
    }

    &__section {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: flex-start;
      background-color: $off-white;
      border-radius: 8px;
      padding: 8px;
      margin-left: 12px;
    }
  }
}
.attendees {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  max-width: 26vw;
  overflow-x: scroll;
  flex-wrap: nowrap;
  gap: 8px;
  border-radius: 8px;
  margin-left: 12px;
  padding-top: 12px;
  &__div {
    background-color: $off-white;
    border-radius: 8px;
    color: $base-gray;
    cursor: pointer;
    font-size: 13px;
    padding: 0px 8px;
  }
}
.header-text {
  font-size: 14px !important;
  color: $base-gray !important;
}
.filtered-green {
  filter: invert(55%) sepia(75%) saturate(324%) hue-rotate(101deg) brightness(97%) contrast(91%);
}
.removeSpace {
  margin: 0 !important;
  padding: 0 !important;
}
.bottom {
  padding-bottom: 16px;
  border-bottom: 2px solid $soft-gray;
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
  display: inline-block;
}

/* Tooltip text */
.tooltip .tooltiptext {
  visibility: hidden;
  width: 110px;
  background-color: $base-gray;
  opacity: 0.9;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;

  /* Position the tooltip text - see examples below! */
  position: absolute;
  z-index: 1;
  top: -5px;
  right: 105%;
}

/* Show the tooltip text when you mouse over the tooltip container */
.tooltip:hover .tooltiptext {
  visibility: visible;
}

.right-tooltip {
  position: relative;
  display: inline-block;
}

.right-tooltip .right-tooltiptext {
  visibility: hidden;
  width: 110px;
  background-color: $base-gray;
  opacity: 0.9;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;
  position: absolute;
  z-index: 1;
  top: -5px;
  left: 105%;
}

/* Show the tooltip text when you mouse over the tooltip container */
.right-tooltip:hover .right-tooltiptext {
  visibility: visible;
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
  width: 26vw;
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
.white-button {
  border: 1px solid $soft-gray;
  padding: 8px 12px;
  margin-right: 1rem;
  border-radius: 8px;
  background-color: white;
  cursor: pointer;
  color: $dark-green;
  transition: all 0.3s;
  font-size: 12px;
  letter-spacing: 0.75px;
}
.add-button {
  border: none;
  padding: 8px 12px;
  margin-right: 1rem;
  border-radius: 8px;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
  font-size: 12px;
}
.add-button:disabled {
  border: none;
  padding: 8px 12px;
  margin-right: 1rem;
  border-radius: 8px;
  background-color: $soft-gray;
  cursor: text;
  color: $gray;
  transition: all 0.3s;
  font-size: 12px;
}
.no-update {
  border: none;
  padding: 8px 12px;
  margin-right: 1rem;
  border-radius: 8px;
  background-color: $base-gray;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
  font-size: 12px;
}
.row {
  display: flex;
  flex-direction: row !important;
  align-items: flex-start;
  justify-content: flex-start;
}
.roww {
  display: flex;
  flex-direction: row;
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
  color: $dark-green !important;
  // background-color: $white-green;
  // padding: 4px 8px !important;
  // border-radius: 4px;
  // max-width: 140px;
  // display: flex;
  // align-items: center;
}
.red-text {
  color: $coral !important;
  font-weight: 400;
  background-color: $light-coral;
  padding: 8px !important;
  border-radius: 8px;
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
  top: 20vh;
  left: 36vw;
  border-radius: 8px;
  background-color: white !important;
  width: 40vw;
  overflow: scroll;
  box-shadow: 2px 2px 3px 2px $very-light-gray;
  min-height: 36vh;
  max-height: 70vh;
  &__title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px !important;
    color: $base-gray;
    letter-spacing: 0.4px;
    font-weight: bold;
    font-size: 15px !important;
    width: 100%;
    position: sticky;
    top: 0;
    z-index: 2;
    background-color: white;
  }
  &__body {
    display: flex;
    align-items: flex-start;
    justify-content: center;
    margin-left: 8px;
    flex-direction: column;
    overflow: scroll;
    background-color: white !important;

    p {
      color: $light-gray-blue;
      font-size: 12px;
    }
  }
  &__footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    position: sticky;
    bottom: 0;
    z-index: 2;
    background-color: white !important;
    margin-top: 0.5rem;
    padding: 0.75rem 0.5rem;
    width: 100%;
    height: 2rem;
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
  top: 20vh;
  left: 36vw;
  border-radius: 8px;
  background-color: $white;
  width: 26vw;
  overflow: scroll;
  box-shadow: 1px 1px 2px 1px $very-light-gray;
  &__title {
    display: flex;
    justify-content: space-between;
    padding: 0 0.5rem;
    align-items: center;
    color: $base-gray;

    letter-spacing: 0.4px;
    font-weight: bold;
    font-size: 14px;
    width: 100%;
  }
  &__body {
    margin: 16px 0px;
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
  top: 20vh;
  left: 36vw;
  border-radius: 8px;
  background-color: $white;
  min-width: 26vw;
  overflow: scroll;
  box-shadow: 1px 1px 2px 1px $very-light-gray;
  &__title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    color: $base-gray;

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
  z-index: 20;
  top: 20vh;
  left: 36vw;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: white;
  width: 30vw;
  height: auto;
  overflow: visible;
  box-shadow: 1px 1px 2px 1px $very-light-gray;
  margin-left: 0px;

  &__title {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 8px 4px 8px 12px;
    color: $base-gray;

    letter-spacing: 0.75px;
    width: 100%;
  }
  &__body {
    padding: 32px 16px;
    width: 30vw;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  &__footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    margin-top: 1rem;
    width: 100%;
    height: 80px;

    p {
      cursor: pointer;
      color: $dark-green;
      font-size: 14px;
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

.img-button {
  background-color: transparent;
  padding: 4px 6px;
  border: none;
  cursor: pointer;
}
</style> 
