<template>
  <div class="table-row">
    <div class="table-cell">
      <div v-if="!meeting.event_data">
        <div>
          <p style="letter-spacing: 0.25px; font-size: 15px; margin-bottom: 3px">
            {{ meeting.topic ? meeting.topic : 'Meeting' }}
          </p>
          <span style="color: #9b9b9b; font-size: 11px">
            Time: {{ meeting.start_time ? formatDateTimeToTime(meeting.start_time) : '' }}
            <!-- {{ meeting.end_time ? formatDateTimeToTime(meeting.end_time) : '' }} -->
          </span>
        </div>
        <!-- <div style="color: #9b9b9b; font-size: 11px; margin-top: 3px">owner:</div> -->
      </div>

      <div v-else>
        <div>
          <p style="letter-spacing: 0.25px; font-size: 15px; margin-bottom: 3px">
            {{ meeting.event_data.title }}
          </p>
          <span style="color: #9b9b9b; font-size: 11px">
            Time: {{ formatUnix(meeting.event_data.times.start_time) }}
          </span>
        </div>
      </div>
    </div>
    <div class="table-cell">
      {{ meeting.participants.length }}
    </div>

    <div class="table-cell">
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
            v-if="
              !meetingUpdated &&
              !meeting.participants[participantIndex].__has_changes &&
              (!resourceType || resourceType === 'Opportunity')
            "
            class="green"
          >
            <img
              @click="addContact(participantIndex)"
              class="contact-img"
              src="@/assets/images/add-contact.png"
              alt=""
            />
          </span>
          <span
            v-if="
              !meetingUpdated &&
              !meeting.participants[participantIndex].__has_changes &&
              (!resourceType || resourceType === 'Opportunity')
            "
            class="red"
          >
            <img
              src="@/assets/images/remove.svg"
              class="contact-img"
              @click="removeParticipant(participantIndex)"
              alt=""
            />
          </span>
          <span v-if="meeting.participants[participantIndex].__has_changes">
            <img class="filter" src="@/assets/images/profile.png" alt="" />
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
              src="@/assets/images/closer.png"
              style="height: 1rem; cursor: pointer; margin-right: 0.75rem; margin-top: -0.5rem"
              @click="addingContact = !addingContact"
            />
          </div>

          <div v-if="hasLastName" class="contact-field-section__body">
            <div v-for="(field, i) in contactFields" :key="i">
              <div v-if="field.dataType === 'Reference'">
                <p>{{ field.referenceDisplayLabel }}:</p>
                <Multiselect
                  v-if="field.apiName === 'AccountId'"
                  placeholder="Select Account"
                  @select="setUpdateValues(field.apiName, $event.integration_id)"
                  v-model="selectedAccount"
                  style="width: 14vw"
                  :options="accounts"
                  openDirection="below"
                  selectLabel="Enter"
                  label="name"
                  track-by="integration_id"
                >
                  <template slot="noResult">
                    <p>No results.</p>
                    <!-- @select="$emit('value-selected', $event.value)"
                      v-model="inputValue" -->
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
                    <p>No results.</p>
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
                    'null'
                      ? `Enter ${field.referenceDisplayLabel}`
                      : `${meeting.participants[participantIndex].secondary_data[field.apiName]}`
                  "
                />
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
                    'null'
                      ? `Enter ${field.referenceDisplayLabel}`
                      : `${meeting.participants[participantIndex].secondary_data[field.apiName]}`
                  "
                />
              </div>
              <!-- <div v-else-if="field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'">
                  <p>{{ field.referenceDisplayLabel }}:</p>
                  <Multiselect
                    :v-model="currentVals.length ? currentVals[0][field.apiName]: null"
                    :options="picklistQueryOpts[field.apiName]"
                    @select="
                      setUpdateValues(
                        field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                        $event.value,
                      )
                    "
                    openDirection="below"
                    style="width: 13vw"
                    selectLabel="Enter"
                    track-by="value"
                    label="label"
                  >
                    <template slot="noResult">
                      <p>No results.</p>
                    </template>
                  </Multiselect>
                </div> -->
            </div>
          </div>
          <div style="margin-left: 1rem; padding: 1rem" class="contact-field-section__body" v-else>
            Add "Last Name" to your<router-link class="link" :to="{ name: 'UpdateContacts' }"
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
              src="@/assets/images/closer.png"
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
      <div v-if="!resourceType || resourceType === 'Opportunity'">
        <p class="roww" @click="addingOpp = !addingOpp" v-if="resourceId && !meetingUpdated">
          {{ allOpps.filter((opp) => opp.id === resourceId)[0].name }}
          <img
            class="invert"
            style="height: 0.6rem; margin-left: 0.2rem"
            src="@/assets/images/edit.png"
            alt=""
          />
        </p>
        <p v-else-if="meetingUpdated">
          {{ allOpps.filter((opp) => opp.id === resourceId)[0].name }}
        </p>
        <button @click="addingOpp = !addingOpp" v-else class="add-button">
          Map to Opportunity
        </button>

        <div v-if="addingOpp" class="add-field-section">
          <div class="add-field-section__title">
            <p>Map to Opportunity</p>
            <img
              src="@/assets/images/closer.png"
              style="height: 1rem; cursor: pointer; margin-right: 0.75rem; margin-top: -0.5rem"
              @click="addingOpp = !addingOpp"
            />
          </div>

          <div class="add-field-section__body">
            <Multiselect
              style="width: 20vw"
              v-model="mappedOpp"
              @select="selectOpp($event)"
              placeholder="Select Opportunity"
              selectLabel="Enter"
              label="name"
              openDirection="below"
              track-by="id"
              :options="allOpps"
            >
              <template slot="noResult">
                <div class="row">
                  <p>No results</p>
                  <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
                </div>
              </template>
            </Multiselect>
          </div>

          <div v-if="mappedOpp" class="add-field-section__footer">
            <p @click="mapOpp">Add</p>
          </div>
          <div v-else style="cursor: text" class="add-field-section__footer">
            <p style="color: gray; cursor: text">Add</p>
          </div>
        </div>
      </div>

      <div v-else>
        <small>
          Looks like this meeting is mapped to an {{ resourceType }}. <br />
          We only support Opportunities at the moment.
        </small>
      </div>
    </div>

    <div v-if="!meetingUpdated" class="table-cell">
      <p v-if="!resourceId && !meetingLoading">Please map meeting in order to take action.</p>
      <div>
        <div class="column" v-if="resourceId && !meetingLoading">
          <button @click="$emit('update-Opportunity', workflowId, resourceId)" class="add-button">
            Update Opportunity
          </button>
          <button @click="noUpdate = !noUpdate" class="no-update">No update needed</button>
        </div>
        <div v-if="noUpdate" class="noupdate-field-section">
          <div class="noupdate-field-section__title">
            <p>No Update Needed</p>
            <img
              src="@/assets/images/closer.png"
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
      <p class="success">Meeting Logged <img src="@/assets/images/complete.png" alt="" /></p>
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
      addingOpp: false,
      noUpdate: false,
      mappedOpp: null,
      resource: null,
      removingParticipant: null,
      selectedIndex: null,
      addingContact: false,
      selectedAccount: null,
      selectedOwner: null,
      formData: {},
      currentVals: [],
    }
  },
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
    Modal: () => import(/* webpackPrefetch: true */ '@/components/Modal'),
  },
  props: {
    meeting: {},
    resourceId: {},
    resourceType: {},
    allOpps: {},
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
  },
  computed: {
    hasLastName() {
      let lastName = null
      lastName = this.contactFields.filter((field) => field.apiName === 'LastName')
      lastName.length ? (lastName = lastName[0].apiName) : (lastName = null)
      return lastName
    },
  },
  mounted() {
    if (this.resourceId) {
      this.getCurrentVals()
    }
  },
  methods: {
    async getCurrentVals() {
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Contact',
          formType: 'UPDATE',
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
    },
    mapOpp() {
      this.$emit('map-opp', this.workflowId, this.resource, 'Opportunity')
      this.addingOpp = !this.addingOpp
    },
    formatUnix(unix) {
      let date = new Date(unix * 1000)
      let hours = date.getHours()
      let minutes = '0' + date.getMinutes()
      let formattedTime = hours + ':' + minutes.substr(-2)
      return formattedTime
    },
    test() {
      console.log(this.mappedOpp.id)
    },
    formatDateTime(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      let newDate = input.replace(pattern, '$2/$3/$1')
      return newDate.split('T')[0]
    },
    formatDateTimeToTime(input) {
      let preDate = new Date(input)
      let newTime = preDate.toLocaleTimeString('en-US')
      let amPm = newTime.split(' ')[1]
      let hour = newTime.split(':')[0]
      let noSeconds = newTime.replace(':', ' ')
      let noAmPm = newTime.replace(amPm, '')
      let noAmPmSeconds = noAmPm.replace(':', ' ')

      if (parseInt(hour) < 9) {
        newTime = '0' + newTime
        noAmPm = '0' + noAmPm
        noSeconds = '0' + noSeconds
        noAmPmSeconds = '0' + noAmPmSeconds
      }
      noSeconds = noSeconds.replace(' ', ':')
      noSeconds = noSeconds.split(':')
      noSeconds = noSeconds[0] + noSeconds[1]
      return noSeconds
    },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

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
  filter: invert(80%);
  cursor: pointer;
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
}
.roww {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}
.columnn {
  display: flex;
  flex-direction: column;
}
.contact-img {
  height: 1.25rem;
  margin-right: 0.2rem;
  padding: 0.25rem;
  border-radius: 0.25rem;
  border: 1px solid #e8e8e8;
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
}
.success {
  display: flex;
  align-items: center;
  img {
    height: 1rem;
    filter: invert(40%) sepia(95%) saturate(370%) hue-rotate(90deg) brightness(54%) contrast(94%);
    margin-left: 0.25rem;
  }
}
.red:hover {
  img {
    filter: invert(46%) sepia(37%) saturate(832%) hue-rotate(308deg) brightness(104%) contrast(104%);
  }
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
  right: 0.5rem;
  border-radius: 0.33rem;
  background-color: $white;
  min-width: 30vw;
  overflow: scroll;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
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
    max-width: 30vw;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    margin: 0.5rem;
    gap: 0.5rem;
    flex-direction: row;
    flex-wrap: wrap;
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
.noupdate-field-section {
  position: absolute;
  z-index: 7;
  left: 1.5rem;
  top: 10vh;
  border-radius: 0.33rem;
  background-color: $white;
  min-width: 20vw;
  overflow: scroll;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
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
  border-radius: 0.33rem;
  background-color: $white;
  min-width: 20vw;
  overflow: scroll;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
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
  border-radius: 0.33rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: $white;
  min-width: 25vw;
  height: auto;
  overflow: scroll;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
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

.table-row {
  display: table-row;
  left: 0;
}
.table-cell {
  display: table-cell;
  position: relative;
  min-width: 12vw;
  background-color: $off-white;
  padding: 2vh 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  font-size: 13px;
}
.table-cell:hover {
  cursor: text;
  background-color: white;
}
</style> 