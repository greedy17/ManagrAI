<template>
  <div class="table-row">
    <div class="table-cell-checkbox">
      <div>
        <input type="checkbox" id="index" />
        <label for="index"></label>
      </div>
    </div>
    <div style="min-width: 22vw" class="table-cell cell-name">
      <div>
        <div>
          <p style="letter-spacing: 0.25px; font-size: 15px; margin-bottom: 3px">
            {{ meeting.topic }}
          </p>
          <span style="color: #9b9b9b; font-size: 11px">
            Time: {{ meeting.start_time ? formatDateTimeToTime(meeting.start_time) : '' }}
            <!-- {{ meeting.end_time ? formatDateTimeToTime(meeting.end_time) : '' }} -->
          </span>
        </div>
        <!-- <div style="color: #9b9b9b; font-size: 11px; margin-top: 3px">owner:</div> -->
      </div>
    </div>
    <div class="table-cell">
      {{ meeting.participants.length }}
    </div>
    <div class="table-cell">
      <p v-for="(participant, i) in meeting.participants" :key="i">
        {{ meeting.participants[i].email }}
      </p>
    </div>
    <div class="table-cell">
      <p v-if="resourceId">
        {{ allOpps.filter((opp) => opp.id === resourceId)[0].name }}
      </p>
      <!-- <button @click="addingOpp = !addingOpp" v-else class="add-button">Map to Opportunity</button> -->
      <button disabled class="add-button">Map to Opportunity (coming soon)</button>

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
            placeholder="Select Opportunity"
            selectLabel="Enter"
            label="name"
            openDirection="below"
            track-by="id"
            :options="allOpps"
            :multiple="true"
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
          <p>Add</p>
        </div>
        <div v-else style="cursor: text" class="add-field-section__footer">
          <p style="color: gray; cursor: text">Add</p>
        </div>
      </div>
    </div>
    <div class="table-cell">
      <button disabled v-if="resourceId" class="add-button">
        Update Opportunity (coming soon)
      </button>
      <p v-else>Please map meeting in order to take action.</p>
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
      mappedOpp: null,
    }
  },
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  created() {},
  methods: {
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
  props: {
    meeting: {},
    resourceId: {},
    allOpps: {},
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.add-field-section {
  z-index: 5;
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