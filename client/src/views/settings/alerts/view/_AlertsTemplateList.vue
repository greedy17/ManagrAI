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

    <div class="center__">
      <h3 v-if="!editing" :class="templates.refreshing ? 'loading-title titles' : 'titles'">
        Edit your Workflow Automation
      </h3>
      <h3 v-else :class="templates.refreshing ? 'loading-title titles' : 'titles'">
        Active Workflow Automations
      </h3>
      <p
        :class="templates.refreshing ? 'loading-title titles' : ''"
        style="font-weight: bold; color: #aaaaaa; margin-top: -0.5rem; font-size: 13px"
      >
        Edit, Run, and Schedule your saved Automations
      </p>
    </div>
    <div v-if="!alertsCount(templates.list.length)">
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
    </div>
    <template
      style="margin-top: -1rem"
      v-if="!templates.refreshing && alertsCount(templates.list.length)"
    >
      <transition name="fade">
        <div v-if="!editing" class="edit__modal">
          <AlertsEditPanel :alert="currentAlert" />
          <div class="edit__modal__button">
            <button @click="closeEdit">Done</button>
          </div>
        </div>
      </transition>

      <transition name="fade">
        <div class="alert_cards" v-if="editing">
          <div :key="i" v-for="(alert, i) in templates.list" class="added-collection">
            <div class="added-collection__header" :data-key="alert.id">
              <h3>{{ alert.title }}</h3>
            </div>
            <div class="added-collection__body">
              <button
                :disabled="clicked.includes(alert.id) || !hasSlackIntegration"
                @click.stop="onRunAlertTemplateNow(alert.id)"
                class="green_button"
              >
                Run now
              </button>
            </div>
            <div class="added-collection__footer">
              <img
                v-if="hasSlackIntegration"
                style="margin-right: 0.25rem"
                src="@/assets/images/slackLogo.png"
                height="15px"
                alt=""
              />
              <p v-if="hasSlackIntegration" style="font-size: 13px">Schedule:</p>
              <div v-if="hasSlackIntegration" class="row__">
                <p
                  :class="!alert.isActive ? 'green' : ''"
                  style="margin-right: 0.5rem; font-size: 12px; letter-spacing: 1px"
                >
                  OFF
                </p>
                <ToggleCheckBox
                  @input="onToggleAlert(alert.id, alert.isActive)"
                  v-model="alert.isActive"
                  offColor="#aaaaaa"
                  onColor="#41b883"
                />
                <p
                  :class="alert.isActive ? 'green' : ''"
                  style="margin-left: 0.5rem; font-size: 12px; letter-spacing: 1px"
                >
                  ON
                </p>
              </div>
              <div style="width: 30vw" v-else>
                <img
                  style="margin-right: 0.2rem"
                  src="@/assets/images/slackLogo.png"
                  height="8px"
                  alt=""
                />
                <small
                  >Connect <span class="link" @click="goToConnect">Slack</span> for
                  notifications</small
                >
              </div>

              <div class="row__two">
                <span class="img-border">
                  <img
                    @click="makeAlertCurrent(alert)"
                    src="@/assets/images/edit.svg"
                    class="invert"
                  />
                </span>

                <span class="img-border">
                  <img
                    src="@/assets/images/trash.svg"
                    class="invert"
                    @click="deleteClosed(alert.id)"
                  />
                </span>
              </div>
            </div>

            <template slot="panel-content">
              <div>
                <AlertsEditPanel :alert="alert" />
              </div>
            </template>
          </div>
          <div v-if="zoomChannel" class="added-collection">
            <div class="added-collection__header">
              <h3>Log Meetings</h3>
              <p></p>
            </div>

            <div class="added-collection__body">
              <button @click="goToLogZoom" class="green_button">Change Channel</button>
            </div>
            <div class="added-collection__footer">
              <img
                style="margin-right: 0.25rem"
                src="@/assets/images/slackLogo.png"
                height="15px"
                alt=""
              />
              <p>
                Current channel:
                <span style="font-weight: bold; color: #41b883; font-size: 13px">{{
                  currentZoomChannel
                }}</span>
              </p>
            </div>
          </div>

          <div v-if="hasRecapChannel && userLevel !== 'REP'" class="added-collection">
            <div class="added-collection__header">
              <h3>Meeting Recaps</h3>
            </div>

            <div class="added-collection__body">
              <button @click="goToRecap" class="green_button">Change Channel/Pipelines</button>
            </div>
            <div class="added-collection__footer">
              <img
                style="margin-right: 0.2rem"
                src="@/assets/images/slackLogo.png"
                height="15px"
                alt=""
              />
              <p>
                Current channel:
                <span style="font-weight: bold; color: #41b883; font-size: 13px">{{
                  currentRecapChannel
                }}</span>
              </p>
            </div>
          </div>
        </div>
      </transition>
    </template>
    <div class="center-loader" v-if="templates.refreshing && alertsCount(templates.list.length)">
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
import { UserConfigForm } from '@/services/users/forms'
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
      userConfigForm: new UserConfigForm({}),
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
    this.userConfigForm = new UserConfigForm({
      activatedManagrConfigs: this.user.activatedManagrConfigs,
    })
  },
  methods: {
    // test() {
    //   console.log(this.templates)
    // },
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
        .update(this.user.id, this.userConfigForm.value)
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
        this.userConfigForm.field.activatedManagrConfigs.value =
          this.userConfigForm.field.activatedManagrConfigs.value.filter(
            (val) => val !== this.deleteTitle,
          )
        this.handleUpdate()

        this.deleteOpen = !this.deleteOpen
        this.$Alert.alert({
          message: 'Workflow removed',
          type: 'success',
          timeout: 2000,
        })
      } catch {
        this.$Alert.alert({
          message: 'There was an error removing your alert',
          type: 'error',
          timeout: 2000,
        })
      }
    },
    async onToggleAlert(id, value) {
      try {
        await AlertTemplate.api.updateAlertTemplate(id, { is_active: value })
        await this.templates.refresh()
        this.$Alert.alert({
          message: `Alert is now ${value ? 'active' : 'inactive'}`,
          type: 'success',
          timeout: 2000,
        })
      } catch {
        this.$Alert.alert({
          message: 'There was an error toggling your alert',
          type: 'error',
          timeout: 2000,
        })
      }
    },
    async onRunAlertTemplateNow(id) {
      try {
        await AlertTemplate.api.runAlertTemplateNow(id)
        this.$Alert.alert({
          message: `Alert has been initiated`,
          type: 'success',
          timeout: 2000,
        })
        this.clicked.push(id)
      } catch {
        this.$Alert.alert({
          message: 'There was an error removing your alert',
          type: 'error',
          timeout: 2000,
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
      return this.$store.state.user.slackAccount.recapChannel
    },
    zoomChannel() {
      return this.$store.state.user.slackAccount.zoomChannel
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
  width: 100%;
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
  margin-left: 10vw;
  margin-top: 3.5rem;
  color: $base-gray;
}
.alert_cards {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: flex-start;
  margin-top: 1rem;
  flex-wrap: wrap;
  padding: 0;
}
.added-collection:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
  transform: scale(1.015);
}

.added-collection {
  background-color: white;
  border-radius: 0.3rem;
  border: 1px solid #e8e8e8;
  width: 22vw;
  margin-right: 1rem;
  margin-bottom: 1rem;
  transition: all 0.25s;
  &__header {
    max-height: 3rem;
    padding: 1.75rem 1rem;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    border-bottom: 2px solid $soft-gray;
  }
  &__body {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 5rem;
    font-size: 13px;
  }
  &__footer {
    display: flex;
    align-items: center;
    height: 3rem;
    padding: 1rem;
    font-size: 14px;
    justify-content: space-evenly;
  }
}
a {
  text-decoration: none;
  color: white;
  cursor: pointer;
}

.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  margin: 0 0.5rem 0 0.5rem;
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
  border-radius: 0.25rem;
  padding: 0.5rem 1rem;
  font-weight: bold;
  font-size: 12px;
  border: none;
  cursor: pointer;
}
.green {
  color: $dark-green;
}
.center__ {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  flex-direction: column;
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
