<template>
  <div class="alerts-template-list">
    <Modal v-if="deleteOpen" dimmed>
      <div class="delete_modal">
        <div class="delete_modal__header">
          <h2>Delete Workflow</h2>
          <img @click="deleteOpen = !deleteOpen" src="@/assets/images/close.png" alt="" />
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
      <h3 @click="test" v-else :class="templates.refreshing ? 'loading-title titles' : 'titles'">
        Saved Workflow Automations
      </h3>
      <p
        :class="templates.refreshing ? 'loading-title titles' : ''"
        style="font-weight: bold; color: #aaaaaa; margin-top: -0.5rem; font-size: 13px"
      >
        Edit, Run, and Schedule your saved Automations
      </p>
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
    </div>
    <template
      style="margin-top: -1rem"
      v-if="!templates.refreshing && alertsCount(templates.list.length)"
    >
      <transition name="fade">
        <div class="middle" v-if="!editing">
          <div class="edit__modal">
            <div>
              <AlertsEditPanel :alert="currentAlert" />
            </div>
            <button style="margin-bottom: 1.5rem" class="yes__button" @click="closeEdit">
              Done
            </button>
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
                :disabled="clicked.includes(alert.id)"
                @click.stop="onRunAlertTemplateNow(alert.id)"
                class="green_button"
              >
                Run now
              </button>
              <!-- <div class="centered">
              <button @click="onTest(alert.id)" class="test-button">Test Alert</button>

              <p style="margin-left: 0.5rem">Results: {{ alert.instances.length }}</p>
            </div> -->
            </div>
            <div class="added-collection__footer">
              <p style="font-size: 13px">Schedule:</p>
              <div class="row__">
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

              <div class="row__two">
                <span class="img-border">
                  <img @click="makeAlertCurrent(alert)" src="@/assets/images/edit.png" />
                </span>

                <span class="img-border">
                  <img src="@/assets/images/whitetrash.png" @click="deleteClosed(alert.id)" />
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

    <!-- <div class="center-loader" v-else>
      <div class="dot-flashing"></div>
    </div> -->

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
import PulseLoadingSpinner from '@thinknimble/pulse-loading-spinner'

//Internal

import ExpandablePanel from '@/components/ExpandablePanel'
import FormField from '@/components/forms/FormField'
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
    ExpandablePanel,
    PulseLoadingSpinner,
    ToggleCheckBox,
    FormField,
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
  // mounted() {
  //   console.log(this.hasRecapChannel)
  // },
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
    test() {
      console.log(this.templates)
    },
    async getRecapChannel() {
      const res = await SlackOAuth.api.channelDetails(this.hasRecapChannel)
      this.currentRecapChannel = res.channel.name
    },
    async getZoomChannel() {
      const res = await SlackOAuth.api.channelDetails(this.zoomChannel)
      this.currentZoomChannel = res.channel.name
    },
    logChannels() {
      console.log(this.userChannelOpts)
    },
    deletedTitle(id) {
      let newList = []
      newList = this.templates.list.filter((val) => val.id === id)
      this.deleteTitle = newList[0].title
    },
    handleUpdate() {
      this.loading = true
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
    hideCard() {
      this.isHiding = true
    },
    goToTemplates() {
      this.$router.push({ name: 'CreateNew' })
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
    async onTest(id) {
      try {
        await AlertTemplate.api.testAlertTemplate(id)
        this.$Alert.alert({
          message: `Alert has been initiated to test against your data only`,
          type: 'success',
          timeout: 2000,
        })
      } catch {
        this.$Alert.alert({
          message: 'There was an error testing your alert',
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
    hasSlack() {
      return this.$store.state.user.slackAccount
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
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}

.bouncy {
  animation: bounce 0.2s infinite alternate;
}

.dot-flashing {
  position: relative;
  width: 14px;
  height: 14px;
  border-radius: 7px;
  background-color: $dark-green;
  color: $dark-green;
  animation: dotFlashing 1s infinite linear alternate;
  animation-delay: 0.5s;
}

.dot-flashing::before,
.dot-flashing::after {
  content: '';
  display: inline-block;
  position: absolute;
  top: 0;
}

.dot-flashing::before {
  left: -15px;
  width: 14px;
  height: 14px;
  border-radius: 7px;
  background-color: $dark-green;
  color: $dark-green;
  animation: dotFlashing 1s infinite alternate;
  animation-delay: 0s;
}

.dot-flashing::after {
  left: 15px;
  width: 14px;
  height: 14px;
  border-radius: 7px;
  background-color: $dark-green;
  color: $dark-green;
  animation: dotFlashing 1s infinite alternate;
  animation-delay: 1s;
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

.spacer {
  height: 0.75rem;
}
h2 {
  font-size: 1.4rem;
}
button:disabled {
  background-color: $panther-silver;
  cursor: not-allowed;
}
::v-deep .item-container__label {
  color: white;
  border: none;
}
::v-deep .ls-container__list--horizontal {
  background-color: $panther;
  width: 50vw;
}
::v-deep .ls-container {
  background: transparent;
  box-shadow: none;
  margin-bottom: 1rem;
}
.keep-activating {
  outline: 2px solid $coral;
}
.keep-activating__ {
  outline: 2px solid $panther-gold;
}
.done-activating {
  outline: 2px solid $dark-green;
}
.titles {
  color: $base-gray;
  font-weight: bold;
}
.alert-links {
  color: #41b883;
  border-bottom: 3px solid #19954e;
}
.activate-button {
  background-color: $dark-green;
  color: white;
  border: none;
  font-weight: bold;
  font-size: 1rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.6rem;
  cursor: pointer;
}
.test-button {
  background-color: white;
  color: $dark-green;
  border: none;
  font-weight: bold;
  padding: 0.5rem 0.75rem;
  border-radius: 0.25rem;
  cursor: pointer;
}
.middle {
  display: flex;
  justify-content: center;
  align-items: center;
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
  box-shadow: 3px 4px 7px $very-light-gray;
  border-radius: 1rem;
  color: $base-gray;
  height: 70vh;
  overflow: scroll;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: column;
}

.yes__button {
  width: 8vw;
  background-color: $dark-green;
  border: none;
  border-radius: 0.25rem;
  color: white;
  cursor: pointer;
  margin-right: 0.5rem;
  padding: 0.5rem;
}
.no__button {
  width: 8vw;
  background-color: $soft-gray;
  border: none;
  border-radius: 0.25rem;

  cursor: pointer;
  padding: 0.5rem;

  margin-right: 0.5rem;
}
.yes__button:hover,
.no__button:hover {
  filter: brightness(80%);
}
.no-data {
  color: $gray;
  margin-left: 0.5rem;
  font-size: 15px;
}
.alerts-template-list__header--heading {
  @include header-subtitle();
}
.alerts-template-list {
  margin-left: 10vw;
  margin-top: 3.5rem;
  color: $base-gray;
  &__header {
    display: flex;

    &-item {
      min-width: 10rem;
      &--main {
        flex: 1 0 auto;
      }
    }
  }
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
// .centered__cards {
//   display: flex;
//   flex-direction: row;
//   justify-content: space-evenly;
//   align-items: center;
//   margin-top: 2rem;
//   flex-wrap: wrap;
// }
.added-collection {
  background-color: white;
  box-shadow: 2px 2px 3px $very-light-gray;
  border-radius: 0.5rem;
  width: 22vw;
  margin-right: 1rem;
  margin-bottom: 1rem;
  &__header {
    max-height: 3rem;
    padding: 1.75rem 1rem;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    border-bottom: 3px solid $soft-gray;
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
.card__ {
  background-color: white;
  padding: 0;
  border: none;
  width: 22vw;
  min-height: 25vh;
  margin: 0rem 0.5rem 0.5rem 0rem;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 3px 4px 7px $very-light-gray;
  color: $base-gray;

  &header {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 3rem;
    font-weight: 900px;
    margin-bottom: 1rem;
    font-size: 0.875rem;
  }
}
.icon {
  display: block;
  cursor: pointer;
  width: 20px;
  height: 30px;
}
// img {
//   filter: invert(90%);
// }
.pink {
  color: $candy;
}
a {
  text-decoration: none;
  color: white;
  cursor: pointer;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-evenly;
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
  border: 1px solid #e8e8e8;
  margin-right: 0.25rem;
  border-radius: 0.2rem;
  cursor: pointer;
  padding: 0.1rem 0.3rem;
}
.row__two {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  width: 100%;
  img {
    height: 0.8rem;
    cursor: pointer;
    filter: invert(70%);
  }
}
.row__start {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-top: 0.25rem;
  width: 100%;
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
.delete_button {
  color: $panther-orange;
  border: none;
  background-color: $panther;
  width: 8vw;
  border-radius: 0.25rem;
  padding: 0.5rem;
  font-weight: bold;
  font-size: 16px;
  cursor: pointer;
}
.edit_button {
  color: $panther-blue;
  background-color: white;
  width: 8vw;
  border-radius: 0.25rem;
  padding: 0.5rem;
  font-weight: bold;
  font-size: 16px;
  border: 2px solid $white;
  cursor: pointer;
}
.debug {
  border: 2px solid red;
}
.center {
  display: flex;
  justify-content: center;
  align-items: center;
}
.center__ {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  flex-direction: column;
}
.centered {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
}
.center-loader {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60vh;
}
.invert {
  filter: invert(99%);
}
.invisible {
  display: none;
}
.loading-title {
  display: none;
}
// ::-webkit-scrollbar {
//   background-color: $panther;
//   -webkit-appearance: none;
//   width: 4px;
//   height: 100%;
// }
// ::-webkit-scrollbar-thumb {
//   border-radius: 2px;
//   background-color: $panther-silver;
// }
</style>
