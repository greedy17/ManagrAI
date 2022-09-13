<template>
  <div class="alerts-template-list">
    <Modal v-if="deleteOpen" dimmed>
      <div class="delete_modal">
        <div class="delete_modal__header">
          <h2>Delete Workflow</h2>
          <img @click="deleteOpen = !deleteOpen" src="@/assets/images/close.svg" alt="" />
        </div>

        <div class="delete_modal__body">
          <p>This action cannot be undone, are you sure ?</p>
        </div>

        <div class="delete_modal__footer">
          <button class="no__button" @click="deleteClose">No</button>
          <button class="yes__button" @click.stop="onDeleteTemplate(deleteId)">Yes</button>
        </div>
      </div>
    </Modal>

    <!-- <div v-if="!alertsCount(templates.list.length) && !templates.refreshing">
      <h3
        class="bouncy"
        style="
          color: #5d5e5e;
          font-weight: bold;
          text-align: center;
          margin-top: 16vh;
          font-size: 3rem;
        "
      >
        0
      </h3>
      <p style="font-weight: bold; color: #5d5e5e; text-align: center">Nothing here.. (o^^)o</p>
    </div> -->
    <template v-if="!templates.refreshing && alertsCount(templates.list.length)">
      <transition name="fade">
        <div v-if="!editing" class="edit__modal">
          <AlertsEditPanel :alert="currentAlert" />
          <div class="edit__modal__button">
            <button @click="closeEdit">Done</button>
          </div>
        </div>
      </transition>

      <div class="alert_cards">
        <div v-if="hasRecapChannel && userLevel !== 'REP'" class="added-collection gray-shadow">
          <div class="added-collection__header">
            <div id="gray">
              <img src="@/assets/images/logo.png" height="36px" alt="" />
            </div>

            <div>
              <p class="gray">Inactive Template</p>
              <h3>Close Date Passed</h3>
            </div>
          </div>

          <div class="added-collection__body">
            <p class="gray">Get notified when important close dates have passed</p>
          </div>
          <div class="added-collection__footer">
            <button @click="goToRecap" class="gray_button">Activate</button>
          </div>
        </div>
      </div>

      <div class="alert_cards" v-if="editing">
        <div :key="i" v-for="(alert, i) in templates.list" class="added-collection green-shadow">
          <div class="added-collection__header" :data-key="alert.id">
            <img src="@/assets/images/logo.png" class="green-bg" height="36px" alt="" />
            <div>
              <p class="green">Managr Template</p>
              <h3>{{ alert.title }}</h3>
            </div>
          </div>
          <div class="added-collection__body">
            <p>Lorem ipsum latin sorem. Lorem ipsum latin so...</p>
          </div>
          <div class="added-collection__footer">
            <div class="row__">
              <button
                style="margin-right: 8px"
                :disabled="clicked.includes(alert.id) || !hasSlackIntegration"
                @click.stop="onRunAlertTemplateNow(alert.id)"
                class="green_button"
              >
                Send to Slack
              </button>
            </div>

            <div v-if="hasSlackIntegration" class="row__">
              <ToggleCheckBox
                @input="onToggleAlert(alert.id, alert.isActive)"
                v-model="alert.isActive"
                offColor="#aaaaaa"
                onColor="#41b883"
              />
            </div>
          </div>

          <template slot="panel-content">
            <div>
              <AlertsEditPanel :alert="alert" />
            </div>
          </template>
        </div>

        <div v-if="zoomChannel" class="added-collection yellow-shadow">
          <div class="added-collection__header">
            <div id="yellow">
              <img src="@/assets/images/logo.png" height="36px" alt="" />
            </div>

            <div>
              <p class="yellow">Meetings</p>
              <h3>Log Meeting</h3>
            </div>
          </div>

          <div class="added-collection__body">
            <p>{{ currentZoomChannel }}</p>
          </div>
          <div class="added-collection__footer">
            <div class="row__">
              <button @click="goToLogZoom" class="yellow_button">Change Channel</button>
            </div>
          </div>
        </div>

        <div v-if="hasRecapChannel && userLevel !== 'REP'" class="added-collection yellow-shadow">
          <div class="added-collection__header">
            <div id="yellow">
              <img src="@/assets/images/logo.png" height="36px" alt="" />
            </div>

            <div>
              <p class="yellow">Meetings</p>
              <h3>Meeting Recaps</h3>
            </div>
          </div>

          <div class="added-collection__body">
            <p>
              {{ currentRecapChannel }}
            </p>
          </div>
          <div class="added-collection__footer">
            <button @click="goToRecap" class="yellow_button">Change Channel</button>
          </div>
        </div>
      </div>
    </template>
    <div class="center-loader" v-if="templates.refreshing">
      <Loader loaderText="Gathering your workflows" />
    </div>
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges
import ToggleCheckBox from '@thinknimble/togglecheckbox'

//Internal
import AlertsEditPanel from '@/views/settings/alerts/view/_AlertsEditPanel'
/**
 * Services
 *
 */
import { CollectionManager } from '@thinknimble/tn-models'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
// import { UserConfigForm } from '@/services/users/forms'
import User from '@/services/users'

import AlertTemplate from '@/services/alerts/'

export default {
  name: 'AlertsTemplateList',
  components: {
    ToggleCheckBox,
    AlertsEditPanel,
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    Loader: () => import(/* webpackPrefetch: true */ '@/components/Loader'),
  },
  data() {
    return {
      userChannelOpts: new SlackListResponse(),
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
      users: CollectionManager.create({ ModelClass: User }),
      deleteOpen: false,
      deleteId: '',
      deleteTitle: '',
      currentAlert: {},
      editing: true,
      isHiding: false,
      // userConfigForm: new UserConfigForm({}),
      configName: '',
      configArray: [],
      currentZoomChannel: '',
      currentRecapChannel: '',
      clicked: [],
      pageLoaded: false,
    }
  },
  async created() {
    this.templates.refresh()
    if (this.zoomChannel) {
      this.getZoomChannel()
    }
    if (this.hasRecapChannel) {
      this.getRecapChannel()
    }
    await this.listUserChannels()
  },
  methods: {
    async getRecapChannel() {
      const res = await SlackOAuth.api.channelDetails(this.hasRecapChannel)
      this.currentRecapChannel = res.channel.name
    },
    async getZoomChannel() {
      const res = await SlackOAuth.api.channelDetails(this.zoomChannel)
      this.currentZoomChannel = res.channel.name
    },
    deletedTitle(id) {
      let newList = []
      newList = this.templates.list.filter((val) => val.id === id)
      this.deleteTitle = newList[0].title
    },
    handleUpdate() {
      // this.loading = true
      User.api
        .update(this.user.id)
        .then((response) => {
          this.$store.dispatch('updateUser', User.fromAPI(response.data))
        })
        .catch((e) => {
          console.log(e)
        })
    },
    alertsCount(num) {
      if (this.zoomChannel && !this.hasRecapChannel) {
        return num + 1
      } else if (this.hasRecapChannel && !this.zoomChannel) {
        return num + 1
      } else if (this.hasRecapChannel && this.zoomChannel) {
        return num + 2
      } else {
        return num
      }
    },
    goToLogZoom() {
      this.$router.push({ name: 'LogZoom' })
    },
    goToRecap() {
      this.$router.push({ name: 'ZoomRecap' })
    },
    goToConnect() {
      this.$router.push({ name: 'Integrations' })
    },
    makeAlertCurrent(val) {
      this.currentAlert = val
      this.editing = !this.editing
    },
    deleteClosed(val) {
      this.deleteOpen === false ? (this.deleteOpen = true) : (this.deleteOpen = false)
      this.deleteId = val
    },
    deleteClose() {
      this.deleteOpen === false ? (this.deleteOpen = true) : (this.deleteOpen = false)
    },
    closeEdit() {
      this.editing = !this.editing
    },
    async listUserChannels(cursor = null) {
      const res = await SlackOAuth.api.listUserChannels(cursor)
      const results = new SlackListResponse({
        channels: [...this.userChannelOpts.channels, ...res.channels],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.userChannelOpts = results
    },
    async onDeleteTemplate(id) {
      this.deletedTitle(id)
      try {
        await AlertTemplate.api.deleteAlertTemplate(id)
        await this.templates.refresh()
        this.handleUpdate()

        this.deleteOpen = !this.deleteOpen
        this.$toast('Workflow removed', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch {
        this.$toast('Error removing workflow', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async onToggleAlert(id, value) {
      try {
        await AlertTemplate.api.updateAlertTemplate(id, { is_active: value })
        await this.templates.refresh()

        this.$toast(`Alert is now ${value ? 'active' : 'inactive'}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch {
        this.$toast('Error toggling workflow', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async onRunAlertTemplateNow(id) {
      try {
        await AlertTemplate.api.runAlertTemplateNow(id)
        this.$toast('Workflow initiated', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.clicked.push(id)
      } catch {
        this.$toast('Error removing workflow', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    hasSlackIntegration() {
      return !!this.$store.state.user.slackRef
    },
    hasRecapChannel() {
      return this.$store.state.user.slackAccount
        ? this.$store.state.user.slackAccount.recapChannel
        : null
    },
    zoomChannel() {
      return this.$store.state.user.slackAccount
        ? this.$store.state.user.slackAccount.zoomChannel
        : null
    },
    userLevel() {
      return this.$store.state.user.userLevel
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/sidebars';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';
@import '@/styles/buttons';

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}

.bouncy {
  animation: bounce 0.2s infinite alternate;
}

@keyframes dotFlashing {
  0% {
    background-color: $dark-green;
  }
  50%,
  100% {
    background-color: $lighter-green;
  }
}

#yellow {
  padding: 4px 8px;
  margin-left: 16px;
  margin-top: 4px;
  border-radius: 6px;
  background-color: $light-yellow;
  img {
    filter: brightness(0%) invert(83%) sepia(28%) saturate(7222%) hue-rotate(6deg) brightness(103%)
      contrast(104%);
  }
}
#gray {
  padding: 4px 8px;
  margin-left: 16px;
  margin-top: 4px;
  border-radius: 6px;
  background-color: $soft-gray;
  img {
    filter: brightness(0%) invert(63%) sepia(13%) saturate(553%) hue-rotate(200deg) brightness(95%)
      contrast(86%);
  }
}

.yellow {
  color: $yellow !important;
}

h2 {
  font-size: 1.4rem;
}
button:disabled {
  background-color: $very-light-gray;
  cursor: not-allowed;
}
.titles {
  color: $base-gray;
  font-weight: bold;
}
.delete_modal {
  background-color: $white;
  color: $base-gray;
  border-radius: 0.3rem;
  width: 40vw;
  padding: 1rem;
  &__header {
    height: 3rem;
    padding: 1rem 0rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 400;
    border-bottom: 1px solid $soft-gray;
    img {
      height: 1rem;
      margin-top: -1rem;
      cursor: pointer;
    }
  }
  &__body {
    height: 4rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  &__footer {
    height: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
.edit__modal {
  background-color: white;
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  color: $base-gray;
  width: 84vw;
  height: 74vh;
  overflow: scroll;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: column;
  padding: none;

  &__button {
    display: flex;
    align-items: flex-end;
    justify-content: flex-end;
    padding: 0rem 2rem 1rem 0rem;
    width: 100%;

    button {
      background-color: $dark-green;
      border: none;
      border-radius: 0.25rem;
      color: white;
      cursor: pointer;
      padding: 0.5rem 2rem;
    }
  }
}

.no__button {
  background-color: $soft-gray;
  outline: 1px solid $soft-gray;
  border: none;
  font-size: 16px;
  border-radius: 0.3rem;
  cursor: pointer;
  padding: 0.4rem 2rem;
  margin-right: 0.5rem;
  color: $base-gray;
}
.yes__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 2rem;
  border-radius: 0.3rem;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  color: white;
  background-color: $dark-green;
  outline: 1px solid $dark-green;
  cursor: pointer;
  font-size: 16px;
}
.alerts-template-list {
  margin: 16px 8px;
  color: $base-gray;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  // justify-content: space-evenly;
}

.alert_cards {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: flex-start;
  flex-wrap: wrap;
  width: 100%;
  border-radius: 6px;
  overflow: scroll;
}

// .added-collection:hover {
//   box-shadow: 1px 2px 2px $very-light-gray;
//   transform: scale(1.015);
// }

.green-shadow {
  box-shadow: 1px 2px 6px $very-light-gray;
  border: 0.5px solid $soft-gray;
}
.yellow-shadow {
  box-shadow: 1px 2px 6px $very-light-gray;
  border: 0.5px solid $soft-gray;
}
.gray-shadow {
  box-shadow: 2px 2px 6px $very-light-gray;
  border: 0.5px solid $soft-gray;
}
.gray {
  color: $light-gray-blue !important;
}
.added-collection {
  background-color: white;
  border-radius: 9px;
  // border: 1px solid #e8e8e8;
  width: 20.5vw;
  height: 175px;
  margin-bottom: 1rem;
  margin-right: 1rem;
  padding-bottom: 0;
  transition: all 0.25s;
  font-size: 12px;
  &__header {
    max-height: 50px;
    display: flex;
    flex-direction: row;
    align-items: center;
    margin-top: 8px;
    div {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: flex-start;
      margin-left: 8px;
      p,
      h3 {
        margin: 0;
        padding: 0;
      }
      p {
        font-size: 10px;
        color: $light-gray-blue;
      }
    }
  }
  &__body {
    display: flex;
    align-items: flex-start;
    margin-left: 16px;
    padding-right: 8px;
    margin-top: 8px;
    font-size: 12px;
    letter-spacing: 0.75px;
  }
  &__footer {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    height: 50px;
    margin-left: 16px;
  }
}
a {
  text-decoration: none;
  color: white;
  cursor: pointer;
}
.green-bg {
  padding: 4px 8px;
  margin-left: 16px;
  margin-top: 4px;
  border-radius: 6px;
  background-color: $white-green;
}
.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  margin: 0 0.5rem 0 0;
  color: $base-gray;
  font-weight: bold;
}
.img-border {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e8e8e8;
  border-radius: 0.2rem;
  cursor: pointer;
  padding: 0.15rem 0.3rem;
}
.row__two {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  width: 100%;
  img {
    height: 0.8rem;
    cursor: pointer;
    filter: invert(20%);
  }
}
.invert {
  filter: invert(20%);
}
.green_button:disabled {
  background-color: $soft-gray;
  color: $gray;
}
.green_button {
  color: white;
  background-color: $dark-green;
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 12px;
  border: none;
  cursor: pointer;
  text-align: center;
}
.yellow_button {
  color: $yellow;
  background-color: white;
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 12px;
  border: 1px solid $yellow;
  cursor: pointer;
  text-align: center;
}
.white_button {
  color: $dark-green;
  background-color: white;
  border-radius: 6px;
  outline: 1px solid $dark-green;
  padding: 4px 8px;
  font-size: 12px;
  border: none;
  cursor: pointer;
  text-align: center;
}
.gray_button {
  color: white;
  background-color: $light-gray-blue;
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 12px;
  border: none;
  cursor: pointer;
  text-align: center;
}
.green {
  color: $dark-green !important;
}
.center__ {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 82vw;
}
.center-loader {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60vh;
}
.loading-title {
  display: none;
}
.link {
  color: $dark-green;
  border-bottom: 1px solid $dark-green;
  cursor: pointer;
}
</style>
