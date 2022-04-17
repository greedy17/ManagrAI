<template>
  <div class="table-row">
    <!-- <div class="table-cell-checkbox">
      <div>
        <input type="checkbox" id="index" />
        <label for="index"></label>
      </div>
    </div> -->
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

    <div @click="test" class="table-cell">
      <div v-for="(participant, i) in meeting.participants" :key="i" class="roww">
        <span class="red">
          <img
            src="@/assets/images/remove.svg"
            class="contact-img"
            @click="removeParticipant(i)"
            alt=""
          />
        </span>
        <span class="green">
          <img class="contact-img" src="@/assets/images/add-contact.png" alt="" />
        </span>
        <p class="add-contact">
          {{ meeting.participants[i].email }}
        </p>
        <div v-if="removingParticipant && selectedIndex === i" class="participant-field-section">
          <div class="add-field-section__title">
            <p>
              Remove <span>"{{ meeting.participants[i].email }}"</span>
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
            <p @click="$emit('remove-participant', workflowId)">Yes</p>
            <p @click="removingParticipant = !removingParticipant" style="color: #fa646a">No</p>
          </div>
        </div>
      </div>
    </div>

    <div class="table-cell">
      <p class="roww" @click="addingOpp = !addingOpp" v-if="resourceId">
        {{ allOpps.filter((opp) => opp.id === resourceId)[0].name }}
        <img
          class="invert"
          style="height: 0.6rem; margin-left: 0.2rem"
          src="@/assets/images/edit.png"
          alt=""
        />
      </p>
      <button @click="addingOpp = !addingOpp" v-else class="add-button">Map to Opportunity</button>
      <!-- <button disabled class="add-button">Map to Opportunity (coming soon)</button> -->

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
    <div v-if="!meetingUpdated" class="table-cell">
      <p v-show="!resourceId">Please map meeting in order to take action.</p>
      <div v-if="resourceId">
        <button @click="$emit('create-form', resourceId)" class="add-button">
          Update Opportunity
        </button>
        <button @click="noUpdate = !noUpdate" class="no-update">No update needed</button>
      </div>
      <div v-if="noUpdate" class="noupdate-field-section">
        <div class="add-field-section__title">
          <p>No Update Needed</p>
          <img
            src="@/assets/images/closer.png"
            style="height: 1rem; cursor: pointer; margin-right: 0.75rem; margin-top: -0.5rem"
            @click="noUpdate = !noUpdate"
          />
        </div>

        <div class="noupdate-field-section__body">
          <p>Are you sure ?</p>
        </div>

        <div class="noupdate-field-section__footer">
          <p @click="onNoUpdate">Yes</p>
          <p @click="noUpdate = !noUpdate" style="color: #fa646a">No</p>
        </div>
      </div>
    </div>
    <div v-else class="table-cell">
      <p>testing update</p>
    </div>
  </div>
</template>
<script>
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
    }
  },
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  watch: {
    // allOpps: 'test',
  },
  props: {
    meeting: {},
    resourceId: {},
    allOpps: {},
    index: {},
    workflowId: {},
    meetingUpdated: {},
    meetingLoading: {},
  },
  created() {},
  methods: {
    test() {
      console.log(this.meetingUpdated)
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

.no-update {
  background-color: $base-gray;
  color: white;
  border: none;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  margin-top: 0.5rem;
  height: 4.5vh;
  width: 8.5rem;
  cursor: pointer;
}
.roww {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  cursor: pointer;
}
.contact-img {
  height: 1.25rem;
  margin-right: 0.2rem;
  padding: 0.25rem;
  border-radius: 0.25rem;
  border: 1px solid #e8e8e8;
}
.green:hover {
  filter: invert(39%) sepia(96%) saturate(373%) hue-rotate(94deg) brightness(104%) contrast(94%);
}
.red:hover {
  img {
    filter: invert(46%) sepia(37%) saturate(832%) hue-rotate(308deg) brightness(104%) contrast(104%);
  }
}

.add-contact {
  img {
    height: 0.6rem;
  }
  cursor: pointer;
}
.noupdate-field-section {
  z-index: 7;
  position: absolute;
  top: 15vh;
  left: 0;
  border-radius: 0.33rem;
  background-color: $white;
  min-width: 16vw;
  overflow: visible;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
  &__title {
    display: flex;
    justify-content: space-between;
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
  z-index: 7;
  position: absolute;
  top: 15vh;
  right: 0.5rem;
  border-radius: 0.33rem;
  background-color: $white;
  min-width: 20vw;
  overflow: visible;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
  &__title {
    display: flex;
    justify-content: space-between;
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
  z-index: 7;
  position: absolute;
  right: 0.5rem;
  top: 9vh;
  border-radius: 0.33rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $white;
  min-width: 22vw;
  overflow: visible;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
  &__title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: $base-gray;
    background-color: $off-white;
    letter-spacing: 0.4px;
    padding-left: 1rem;
    font-weight: bold;
    font-size: 16px;
    width: 100%;
  }
  &__body {
    min-height: 3rem;
    padding-left: 1rem;
    margin-top: 1rem;
  }
  &__footer {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 1rem;
    width: 100%;
    min-height: 6vh;
    border-top: 1px solid $soft-gray;
    p {
      cursor: pointer;
      color: $dark-green;
      font-weight: bold;
    }
  }
}
</style> 