<template>
  <div class="overview">
    <div>
      <div class="header">
        <p>Your pipeline</p>
        <p><span>You have 5 active workflows</span></p>
      </div>
      <section class="workflow" :key="i" v-for="(alert, i) in templates.list">
        <div class="title">
          <img src="@/assets/images/logo.png" height="28px" alt="" />
          <div>
            <h4>
              {{ alert.title }}
              <span>{{ workflows[i] ? workflows[i] : '0' }}</span>
            </h4>

            <p>
              {{ owner(alert.user) !== 'Management' ? 'Owner:' : 'Management' }}
              {{ users ? owner(alert.user) : '' }}
            </p>
          </div>
        </div>

        <section class="button-section">
          <div>
            <button class="green-button">View List</button>
            <button class="white-button">
              Send Slack <img src="@/assets/images/slackLogo.png" height="12px" alt="" />
            </button>
          </div>

          <div>
            <img src="@/assets/images/pencil.svg" height="14px" alt="" />
            <img src="@/assets/images/trash.svg" height="14px" alt="" />
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
      meetings: null,
      activeNotis: false,
      today: null,
      day: null,
      workflows: [],
      templates: CollectionManager.create({
        ModelClass: AlertTemplate,
        filters: { forPipeline: true },
      }),
      users: CollectionManager.create({ ModelClass: User }),
    }
  },
  watch: {
    meetings: 'needsAction',
  },
  methods: {
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
  async created() {
    this.templates.refresh()
    this.users.refresh()
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
      width: 34vw;
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: space-between;

      span {
        background-color: $off-white;
        color: $light-gray-blue;
        padding: 2px 6px;
        border-radius: 4px;
        margin-left: 12px;
        font-size: 11px;
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
  margin-left: 44px;
  border-bottom: 2px solid $soft-gray;
  padding-bottom: 16px;
  div {
    display: flex;
    flex-direction: row;
    align-items: center;

    img {
      margin-right: 8px;
    }
  }
}
.workflow {
  //   border-bottom: 2px solid $soft-gray;
  padding: 16px 0px 0px 0px;
  background-color: white;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;

  position: sticky;
  background-color: white;
  top: 0;
  p {
    font-size: 14px;

    span {
      background-color: $white-green;
      color: $dark-green;
      padding: 4px 8px;
      border-radius: 6px;
      margin-left: 4px;
      font-size: 11px;
    }
  }
  img {
    margin-left: 8px;
  }
}
</style>