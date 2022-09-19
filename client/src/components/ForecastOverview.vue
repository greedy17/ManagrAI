<template>
  <div class="overview">
    <div>
      <section class="forecast">
        <div class="flex-end">
          <p class="light-blue">Forecast</p>
          <img src="@/assets/images/settings.svg" alt="" />
        </div>
        <div class="header">
          <p>Monthly Summmary</p>
        </div>

        <section class="review-section">
          <div>
            <h2>
              $100,000 <img src="@/assets/images/trendingUp.svg" class="green-filter" alt="" />
            </h2>
            <h4>$80,000</h4>
          </div>

          <button class="green-button">Open</button>
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
  name: 'ForecastOverview',
  data() {
    return {
      meetings: null,
      activeNotis: false,
      today: null,
      day: null,
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

.header {
  h4,
  p {
    padding: 0;
    margin: 0;
  }

  p {
    font-size: 13px;
  }
}
.review-section {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: space-between;
  height: 10vh;
  div {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-end;
    max-height: 100px;
    h2,
    h4 {
      margin: 0;
      padding: 0;
    }

    h2 {
      color: $dark-green;
      font-size: 32px;
    }
    h4 {
      color: $light-gray-blue;
      font-size: 12px;
      margin-top: 4px;
    }
  }
}
.flex-end {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.green-button {
  border: none;
  padding: 6px 12px;
  border-radius: 8px;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
  font-size: 12px;
}
.green-filter {
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.light-blue {
  color: $light-gray-blue;
}
</style>