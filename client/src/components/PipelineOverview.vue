<template>
  <div class="overview">
    <div class="header">
      <p>
        {{ activeWorkflow.title }}
      </p>

      <p style="margin-right: 8px">
        <img
          src="@/assets/images/left.svg"
          height="12px"
          alt=""
          style="margin-right: 4px; padding-top: 2px"
        />
        {{ activeWorkflow.length }}
      </p>
    </div>

    <div v-if="activeWorkflow">
      <section class="workflow" :key="i" v-for="(opp, i) in activeWorkflow">
        <div class="title">
          <div>
            <h4>
              {{ opp.Name }}
              <!-- <span>{{ activeWorkflowType }}</span> -->
            </h4>
            <p>Stage: {{ opp.StageName }}</p>
            <p>Close Date: {{ opp.CloseDate }}</p>
          </div>
        </div>
        <section class="button-section">
          <div>
            <button class="green-button">Update Record</button>
            <img src="@/assets/images/note.svg" height="14px" alt="" />
            <img src="@/assets/images/pipeline.svg" height="14px" alt="" />
          </div>
        </section>
      </section>
    </div>
  </div>
</template>

<script>
import { MeetingWorkflows } from '@/services/salesforce'
import { CollectionManager } from '@thinknimble/tn-models'
import AlertTemplate from '@/services/alerts/'
import User from '@/services/users'

export default {
  name: 'PipelineOverview',
  data() {
    return {
      activeNotis: false,
      today: null,
      workflows: [],
      users: CollectionManager.create({ ModelClass: User }),
    }
  },
  watch: {
    meetings: 'needsAction',
  },
  props: {
    activeWorkflow: {},
  },
  methods: {
    test(i) {
      console.log(i)
    },
    needsAction() {
      let NA = 0
      if (this.meetings.length) {
        for (let i = 0; i < this.meetings.length; i++) {
          !this.meetings[i].is_completed ? (NA += 1) : null

          NA === 0 ? (this.activeNotis = false) : (this.activeNotis = true)
        }
      }
    },
    async runWorkflows() {
      let ids = this.templates.list.map((wf) => wf.id)
      try {
        for (let i = 0; i < ids.length; i++) {
          let res = await AlertTemplate.api.runAlertTemplateNow(ids[i], {
            fromWorkflow: true,
          })
          this.workflows.push(res.data.results.length)
        }
      } catch (error) {
        console.log(error)
      }
    },
    owner(usr) {
      return this.users.list.filter((user) => user.id === usr)[0]
        ? this.users.list.filter((user) => user.id === usr)[0].fullName
        : 'Management'
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
    goToWorkflow(id) {
      this.$router.push({ path: `/pipelines/${id}` })
    },
    goToMeetings() {
      this.$router.push({ name: 'Meetings' })
    },

    async getMeetingList() {
      try {
        const res = await MeetingWorkflows.api.getMeetingList()
        this.meetings = res.results
      } catch (e) {
        console.log(e)
      } finally {
      }
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

.overview {
  padding: 0px 20px;
}

.title {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  margin-bottom: 16px;
  width: 100%;

  div {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    margin-left: 16px;
    h4 {
      font-weight: 900;
      font-size: 14px;
      margin: 0;
      padding: 0;
      width: 36vw;
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: space-between;

      span {
        // background-color: $off-white;
        color: $light-gray-blue;
        padding: 4px 8px;
        border-radius: 4px;
        margin-left: 12px;
        font-size: 13px;
        opacity: 0.9;
      }
    }

    p {
      font-weight: bold;
      font-size: 10px;
      color: $light-gray-blue;
      padding: 0;
      margin: 0;
      margin-top: 4px;
    }
  }
}
.green-button {
  border: none;
  padding: 6px 12px;
  margin-right: 1rem;
  border-radius: 8px;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
  font-size: 12px;
}
.white-button {
  border: 1px solid $dark-green;
  padding: 6px 4px 6px 12px;
  margin-right: 1rem;
  border-radius: 8px;
  background-color: white;
  cursor: pointer;
  color: $dark-green;
  transition: all 0.3s;
  font-size: 12px;
  display: flex;
  flex-direction: row;
  align-items: center;
  img {
    margin-left: 6px;
  }
}
.button-section {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-left: 16px;
  border-bottom: 2px solid $soft-gray;
  padding-bottom: 16px;
  div {
    display: flex;
    flex-direction: row;
    align-items: center;

    img {
      margin-left: 8px;
    }
  }
}
.workflow {
  //   border-bottom: 2px solid $soft-gray;
  padding: 16px 0px 0px 0px;
  background-color: white;
  z-index: -1;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-left: 14px;
  position: sticky;
  background-color: white;
  z-index: 2;
  top: 0;
  p {
    font-size: 14px;
    span {
      color: $dark-green;
      padding: 2px 4px;
    }
  }
}
.light-blue {
  color: $light-gray-blue;
}
.filtered {
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
</style>